"""add rank table

Revision ID: b6b2c6c4e8f2
Revises: e4b921984471
Create Date: 2025-03-29 18:52:34.650102

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6b2c6c4e8f2'
down_revision: Union[str, None] = 'e4b921984471'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ranks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('fighter_id', sa.Integer(), nullable=False),
    sa.Column('weight_class_id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['fighter_id'], ['fighters.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['fight_organizations.id'], ),
    sa.ForeignKeyConstraint(['weight_class_id'], ['weight_classes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('rank', 'weight_class_id', 'organization_id')
    )
    op.create_index(op.f('ix_ranks_id'), 'ranks', ['id'], unique=False)
    op.add_column('fighter_weight_class_association', sa.Column('current_rank', sa.Integer(), nullable=True))
    op.add_column('fighter_weight_class_association', sa.Column('is_champ', sa.Boolean(), nullable=True))
    op.add_column('weight_classes', sa.Column('pounds', sa.Integer(), nullable=True))
    op.add_column('weight_classes', sa.Column('kilos', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('weight_classes', 'kilos')
    op.drop_column('weight_classes', 'pounds')
    op.drop_column('fighter_weight_class_association', 'is_champ')
    op.drop_column('fighter_weight_class_association', 'current_rank')
    op.drop_index(op.f('ix_ranks_id'), table_name='ranks')
    op.drop_table('ranks')
    # ### end Alembic commands ###
