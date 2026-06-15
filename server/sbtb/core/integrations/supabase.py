from typing import Annotated

import structlog
from fastapi import Depends
from supabase import AsyncClient, acreate_client
from supabase.client import AsyncClientOptions

from sbtb.core.config import settings

logger = structlog.get_logger(__name__)


class SupabaseHandler:
    supabase_client: AsyncClient | None = None

    async def init(self) -> "SupabaseHandler":
        self.supabase_client = await acreate_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SECRET_KEY,
            options=AsyncClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            ),
        )
        return self

    async def delete_user(self, supabase_user_id: str) -> None:
        """Delete a user from Supabase Auth by their UUID.

        Args:
            supabase_user_id: The auth.users UUID of the user to delete.

        Raises:
            Exception: Re-raised after logging if the Supabase admin call fails.
        """
        try:
            await self.supabase_client.auth.admin.delete_user(id=supabase_user_id)
            logger.info("Deleted Supabase auth user", supabase_user_id=supabase_user_id)
        except Exception:
            logger.exception("Failed to delete Supabase auth user", supabase_user_id=supabase_user_id)
            raise

    async def upload_to_storage(
        self,
        *,
        bucket: str,
        path: str,
        file: bytes,
        content_type: str = "image/png",
    ) -> str:
        """Upload bytes to Supabase Storage and return the public URL.

        Args:
            bucket: The storage bucket name.
            path: The destination path within the bucket (e.g. "{fighter_id}.png").
            file: Raw bytes to upload.
            content_type: MIME type of the file.

        Returns:
            Public URL of the uploaded file.

        Raises:
            Exception: Re-raised after logging if the upload fails.
        """
        try:
            await self.supabase_client.storage.from_(bucket).upload(
                path=path,
                file=file,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            url = await self.supabase_client.storage.from_(bucket).get_public_url(path)
            logger.info("Uploaded file to Supabase Storage", bucket=bucket, path=path)
            return url
        except Exception:
            logger.exception("Failed to upload file to Supabase Storage", bucket=bucket, path=path)
            raise


async def get_supabase_handler() -> SupabaseHandler:
    """FastAPI dependency — creates a fresh SupabaseHandler per request.

    A new client is created each time to avoid the API key contamination issue:
    https://github.com/supabase/supabase-py/issues/1143
    """
    return await SupabaseHandler().init()


SupabaseDep = Annotated[SupabaseHandler, Depends(get_supabase_handler)]
