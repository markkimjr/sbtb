from sbtb.core.repository.base import BaseRepository
from sbtb.models import User


class UserRepository(BaseRepository[User]):
    model = User
