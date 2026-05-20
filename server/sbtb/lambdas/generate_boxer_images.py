import asyncio
from typing import Any

import structlog

from sbtb.core.database.session import SessionLocal
from sbtb.fighter.image_generator import fighter_image_generator

logger = structlog.get_logger(__name__)


async def _handler() -> dict[str, Any]:
    async with SessionLocal() as session:
        try:
            logger.info("Starting boxer avatar generation")
            result = await fighter_image_generator.generate_fighter_avatars(session=session)
            await session.commit()
            logger.info("Boxer avatar generation complete", updated=len(result.updated), skipped=len(result.skipped))
            return {
                "statusCode": 200,
                "body": {"updated": result.updated, "skipped": result.skipped},
            }
        except Exception:
            await session.rollback()
            logger.exception("Boxer avatar generation failed")
            raise
        finally:
            await session.close()


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    return asyncio.run(_handler())


if __name__ == "__main__":
    lambda_handler(event={}, context=None)
