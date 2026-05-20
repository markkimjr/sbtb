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

_STORAGE_BUCKET = "fighter-images"
_GHIBLI_PROMPT = (
    "Reimagine this person as a Studio Ghibli anime character portrait. "
    "Keep their facial features recognizable. "
    "Hand-drawn watercolor style inspired by Hayao Miyazaki. "
    "Clean simple background. Professional boxing portrait."
)


class FighterImageGenerator:
    @staticmethod
    def _convert_to_webp(image_bytes: bytes, quality: int = 90) -> bytes:
        """Convert raw image bytes to WebP format."""
        image = Image.open(io.BytesIO(image_bytes))
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=quality)
        return output.getvalue()

    async def generate_fighter_avatars(self, session: DbSession) -> AvatarGenerationResult:
        """Generate Ghibli-style avatars for all fighters that don't yet have one.

        For each fighter: searches for a reference image via SerpAPI, generates a
        Studio Ghibli version via gpt-image-1, uploads to Supabase Storage, and
        saves the public URL to fighter.avatar_url.

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
        """Send reference image to gpt-image-1 and return Ghibli-style PNG bytes."""
        try:
            image_file = io.BytesIO(reference_bytes)
            image_file.name = "reference.png"

            response = await openai_client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt=_GHIBLI_PROMPT,
                size="1024x1024",
            )
            return base64.b64decode(response.data[0].b64_json)
        except Exception:
            logger.exception(f"Failed to generate Ghibli image for {fighter_name}")
            return None


fighter_image_generator = FighterImageGenerator()
