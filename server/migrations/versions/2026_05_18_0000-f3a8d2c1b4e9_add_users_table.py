"""add users table

Revision ID: f3a8d2c1b4e9
Revises: 6905bc7723a1
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3a8d2c1b4e9"
down_revision: Union[str, None] = "6905bc7723a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("notification_email", sa.String(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("modified_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("users_pkey")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index(op.f("ix_users_created_at"), "users", ["created_at"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # No FK constraint to auth.users: public.users.id mirrors auth.users.id by convention,
    # but the row is intentionally retained after auth deletion for PII anonymization
    # (email nulled, deleted_at set). A FK would block deleting auth.users while the
    # public.users row still exists.

    # Trigger: auto-insert into public.users when a new auth user is created.
    # Wrapped in an auth schema existence check so the migration runs cleanly on
    # local Postgres (no auth schema) and executes fully on Supabase.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth') THEN
                CREATE OR REPLACE FUNCTION public.handle_new_user()
                RETURNS trigger AS $func$
                BEGIN
                    INSERT INTO public.users (id, email, is_active, is_superuser, created_at)
                    VALUES (NEW.id, NEW.email, true, false, NOW());
                    RETURN NEW;
                END;
                $func$ LANGUAGE plpgsql SECURITY DEFINER;

                CREATE TRIGGER on_auth_user_created
                AFTER INSERT ON auth.users
                FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
            END IF;
        END;
        $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth') THEN
                DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
            END IF;
        END;
        $$;
    """)
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user()")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_created_at"), table_name="users")
    op.drop_table("users")