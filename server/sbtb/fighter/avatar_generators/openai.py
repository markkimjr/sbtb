import base64
import io

import aiohttp
import structlog
from openai import AsyncOpenAI
from PIL import Image

from sbtb.core.config import settings
from sbtb.core.database.session import DbSession
from sbtb.core.integrations.supabase import SupabaseHandler, get_supabase_handler
from sbtb.fighter.repository import FighterRepo
from sbtb.fighter.schemas import AvatarGenerationResult
from sbtb.models import Fighter

logger = structlog.get_logger(__name__)

_STORAGE_BUCKET = "boxer-images"

_OPENAI_MODEL = "gpt-image-1"
_OPENAI_SIZE = "1024x1024"
_OPENAI_QUALITY = "medium"  # "low" | "medium" | "high"

# gpt-image-1 responds better to natural-language instructions than tag soup, so this
# prompt is written as a brief rather than a list of keywords.
_GHIBLI_PROMPT = (
    "Transform this photo into a Studio Ghibli anime style illustration. "
    "Hayao Miyazaki hand-drawn 2D cartoon, thick clean outlines, flat cel shading, "
    "warm watercolor palette, expressive Ghibli-style face with large eyes. "
    "Pose the boxer in an orthodox fighting stance: body facing left, head turned left, "
    "left shoulder forward, both fists raised in a high guard. "
    "Outfit: bright red lace-up boxing gloves, black boxing trunks, white high-top boxing shoes. "
    "Plain off-white background with no detail. "
    "Preserve the person's recognisable face, skin tone, and any tattoos. "
    "The body should be fully cartoon — not photorealistic."
)


class GptFighterImageGenerator:
    @staticmethod
    def _convert_to_webp(image_bytes: bytes, quality: int = 90) -> bytes:
        """Convert raw image bytes to WebP format for storage."""
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode == "RGBA":
            image = image.convert("RGB")
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=quality)
        return output.getvalue()

    @staticmethod
    def _convert_to_png(image_bytes: bytes) -> bytes:
        """Convert reference image to PNG (the format gpt-image-1 expects)."""
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    async def generate_fighter_avatars(self, session: DbSession) -> AvatarGenerationResult:
        """Generate Ghibli-style avatars for all fighters that don't yet have one.

        For each fighter: searches for a reference image via SerpAPI, generates a
        Studio Ghibli version via OpenAI gpt-image-1, uploads to Supabase Storage,
        and saves the public URL to fighter.avatar_url.

        Args:
            session: The active database session for this request.

        Returns:
            AvatarGenerationResult with lists of updated and skipped fighter names.
        """
        fighter_repo = FighterRepo.from_session(session)
        fighters = await fighter_repo.get_without_avatar()

        if not fighters:
            logger.info("No fighters missing avatars")
            return AvatarGenerationResult(updated=[], skipped=[])

        logger.info(f"Generating avatars for {len(fighters)} fighters")

        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        supabase_handler = await get_supabase_handler()

        updated = []
        skipped = []

        for fighter in fighters:
            try:
                avatar_url = await self._generate_avatar(
                    fighter=fighter,
                    openai_client=openai_client,
                    supabase_handler=supabase_handler,
                )
                if avatar_url:
                    await fighter_repo.update(fighter, update_dict={"avatar_url": avatar_url}, flush=True)
                    updated.append(fighter.name)
                    logger.info(f"Generated avatar for {fighter.name}")
                else:
                    skipped.append(fighter.name)
            except Exception:
                logger.exception(f"Failed to generate avatar for {fighter.name}")
                skipped.append(fighter.name)

        logger.info("Avatar generation complete", updated=len(updated), skipped=len(skipped))
        return AvatarGenerationResult(updated=updated, skipped=skipped)

    async def _generate_avatar(
        self,
        *,
        fighter: Fighter,
        openai_client: AsyncOpenAI,
        supabase_handler: SupabaseHandler,
    ) -> str | None:
        reference_bytes = await self._fetch_reference_image(fighter_name=fighter.name)
        if not reference_bytes:
            logger.error(f"No reference image found for {fighter.name}")
            return None

        ghibli_bytes = await self._generate_ghibli_image(
            fighter_name=fighter.name,
            reference_bytes=reference_bytes,
            openai_client=openai_client,
        )
        if not ghibli_bytes:
            return None

        webp_bytes = self._convert_to_webp(ghibli_bytes)
        return await supabase_handler.upload_to_storage(
            bucket=_STORAGE_BUCKET,
            path=f"{fighter.id}.webp",
            file=webp_bytes,
            content_type="image/webp",
        )

    async def _fetch_reference_image(self, *, fighter_name: str) -> bytes | None:
        """Search Google Images via SerpAPI and download the first result."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://serpapi.com/search.json",
                    params={
                        "engine": "google_images",
                        "q": f"{fighter_name} boxer portrait",
                        "api_key": settings.SERPAPI_KEY,
                        "num": "5",
                    },
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            images = data.get("images_results", [])
            if not images:
                logger.error(f"SerpAPI returned no images for {fighter_name}")
                return None

            image_url = images[0]["original"]
            logger.info(f"Fetching reference image for {fighter_name}", url=image_url)

            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    response.raise_for_status()
                    return await response.read()

        except Exception:
            logger.exception(f"Failed to fetch reference image for {fighter_name}")
            return None

    async def _generate_ghibli_image(
        self,
        *,
        fighter_name: str,
        reference_bytes: bytes,
        openai_client: AsyncOpenAI,
    ) -> bytes | None:
        """Send reference image to OpenAI gpt-image-1 and return Ghibli-style image bytes.

        Unlike diffusion-based img2img (Flux/SD), gpt-image-1 does not have a strength dial.
        It interprets the prompt as an instruction to transform the image, and naturally
        preserves the subject's identity (face, skin tone) while applying the requested
        style and pose changes. This means we can ask it to fully restyle the body AND
        keep the face recognisable in the same call.

        The response is base64-encoded PNG (gpt-image-1 always returns b64_json).
        """
        try:
            png_bytes = self._convert_to_png(reference_bytes)
            image_file = io.BytesIO(png_bytes)
            image_file.name = "reference.png"

            result = await openai_client.images.edit(
                model=_OPENAI_MODEL,
                image=image_file,
                prompt=_GHIBLI_PROMPT,
                size=_OPENAI_SIZE,
                quality=_OPENAI_QUALITY,
                n=1,
            )

            if not result.data:
                logger.error(f"OpenAI returned no output for {fighter_name}")
                return None

            b64 = result.data[0].b64_json
            if not b64:
                logger.error(f"OpenAI returned empty b64_json for {fighter_name}")
                return None

            return base64.b64decode(b64)
        except Exception:
            logger.exception(f"Failed to generate Ghibli image for {fighter_name}")
            return None


gpt_fighter_image_generator = GptFighterImageGenerator()
