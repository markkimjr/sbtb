import io

import aiohttp
import structlog
from google import genai
from google.genai import types
from PIL import Image

from sbtb.core.config import settings
from sbtb.core.database.session import DbSession
from sbtb.core.integrations.supabase import SupabaseHandler, get_supabase_handler
from sbtb.fighter.repository import FighterRepo
from sbtb.fighter.schemas import AvatarGenerationResult
from sbtb.models import Fighter

logger = structlog.get_logger(__name__)

_STORAGE_BUCKET = "boxer-images"

# Gemini 2.5 Flash Image (Nano Banana)
_GEMINI_MODEL = "gemini-2.5-flash-image"

# Structure: style → pose → outfit → background → identity-preservation note.
_GHIBLI_PROMPT = (
    "Transform this photo into a Studio Ghibli anime illustration.\n\n"
    "Style: Hayao Miyazaki, hand-drawn 2D cartoon watercolor, thick clean "
    "outlines, flat cel shading, warm watercolor palette, expressive Ghibli-"
    "style face with large expressive eyes.\n\n"
    "Pose the boxer in an orthodox fighting stance: body angled to the left, "
    "head turned left, left shoulder forward, both fists clenched and raised "
    "in a high guard near the face.\n\n"
    "Outfit: bright red lace-up boxing gloves, black boxing trunks with a "
    "thin white waistband, white high-top boxing shoes.\n\n"
    "Background: plain off-white, no detail.\n\n"
    "Preserve the person's recognisable face, skin tone, and any tattoos. "
    "The body should be fully cartoon — not photorealistic."
)


class GeminiFighterImageGenerator:
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
        """Convert reference image to PNG (most reliable format for Gemini)."""
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    async def generate_fighter_avatars(self, session: DbSession) -> AvatarGenerationResult:
        """Generate Ghibli-style avatars for all fighters that don't yet have one.

        For each fighter: searches for a reference image via SerpAPI, sends it to
        Gemini 2.5 Flash Image with a Ghibli style-transfer instruction, uploads
        the result to Supabase Storage, and saves the public URL.

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

        gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        supabase_handler = await get_supabase_handler()

        updated: list[str] = []
        skipped: list[str] = []

        for fighter in fighters:
            try:
                avatar_url = await self._generate_avatar(
                    fighter=fighter,
                    gemini_client=gemini_client,
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
        gemini_client: genai.Client,
        supabase_handler: SupabaseHandler,
    ) -> str | None:
        reference_bytes = await self._fetch_reference_image(fighter_name=fighter.name)
        if not reference_bytes:
            logger.error(f"No reference image found for {fighter.name}")
            return None

        ghibli_bytes = await self._generate_ghibli_image(
            fighter_name=fighter.name,
            reference_bytes=reference_bytes,
            gemini_client=gemini_client,
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
        gemini_client: genai.Client,
    ) -> bytes | None:
        """Send reference image to Gemini 2.5 Flash Image and return the Ghibli bytes.

        The model returns its output as a sequence of parts on the response — each
        part is either text (any commentary from the model) or inline_data (the
        generated image as raw bytes). We walk the parts and return the first
        image we find.

        Failure modes:
        - Safety filter blocks the request — surfaces as finish_reason="SAFETY"
          or a prompt_feedback block_reason. We log and skip.
        - Model returns only text (no image) — we log the text for debugging and
          treat it as a skip.
        """
        try:
            png_bytes = self._convert_to_png(reference_bytes)
            image_part = types.Part.from_bytes(data=png_bytes, mime_type="image/png")

            response = await gemini_client.aio.models.generate_content(
                model=_GEMINI_MODEL,
                contents=[_GHIBLI_PROMPT, image_part],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )

            # Check for safety/policy blocks before walking parts.
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                logger.error(
                    f"Gemini blocked request for {fighter_name}",
                    block_reason=str(response.prompt_feedback.block_reason),
                )
                return None

            if not response.candidates:
                logger.error(f"Gemini returned no candidates for {fighter_name}")
                return None

            candidate = response.candidates[0]
            finish_reason = getattr(candidate, "finish_reason", None)

            if not candidate.content or not candidate.content.parts:
                logger.error(
                    f"Gemini returned empty content for {fighter_name}",
                    finish_reason=str(finish_reason),
                )
                return None

            # Walk parts; prefer the first image, but log any text we find for visibility.
            for part in candidate.content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    return part.inline_data.data
                if getattr(part, "text", None):
                    logger.info(
                        f"Gemini text response for {fighter_name}",
                        text=part.text[:300],
                    )

            logger.error(
                f"Gemini returned no image part for {fighter_name}",
                finish_reason=str(finish_reason),
            )
            return None
        except Exception:
            logger.exception(f"Failed to generate Ghibli image for {fighter_name}")
            return None


gemini_fighter_image_generator = GeminiFighterImageGenerator()
