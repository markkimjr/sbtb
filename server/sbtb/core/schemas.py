from datetime import datetime

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_mode_override="serialization",
        alias_generator=to_camel,
    )


class IDSchema(BaseSchema):
    id: UUID4 = Field(..., description="The ID of the object.")

    model_config = ConfigDict(
        # IMPORTANT: this ensures FastAPI doesn't generate `-Input` for output schemas
        json_schema_mode_override="serialization",
    )


class TimestampedSchema(BaseSchema):
    created_at: datetime = Field(description="Creation timestamp of the object.")
    modified_at: datetime | None = Field(
        description="Last modification timestamp of the object."
    )
