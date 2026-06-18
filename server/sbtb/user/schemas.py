from sbtb.core.schemas import IDSchema


class UserMeRead(IDSchema):
    """Frontend-facing user profile. Camel-cased on the wire via BaseSchema."""

    email: str | None = None
    notification_email: str | None = None
    timezone: str | None = None
    is_active: bool
    is_superuser: bool
