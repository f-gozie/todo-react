"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from __future__ import annotations

from alembic import op  # type: ignore
import sqlalchemy as sa  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "${up_revision}"
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | None = None
depends_on: str | None = None

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"} 