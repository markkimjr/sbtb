"""change rank type from int to double

Revision ID: 74487e240e76
Revises: c456bf837b23
Create Date: 2025-03-29 21:27:29.090791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74487e240e76'
down_revision: Union[str, None] = 'c456bf837b23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ranks', 'rank',
               existing_type=sa.INTEGER(),
               type_=sa.Double(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ranks', 'rank',
               existing_type=sa.Double(),
               type_=sa.INTEGER(),
               existing_nullable=False)
    # ### end Alembic commands ###
