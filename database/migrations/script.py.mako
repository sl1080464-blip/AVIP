"""Auto-generated migration script."""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '${_alembic_revision}'
down_revision = ${repr(_alembic_down_revision)}
branch_labels = ${repr(_alembic_branch_labels)}
depends_on = ${repr(_alembic_depends_on)}


def upgrade():
${upgrades if upgrades else "    pass"}


def downgrade():
${downgrades if downgrades else "    pass"}
