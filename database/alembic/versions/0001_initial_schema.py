"""Initial NWIS persistent storage schema."""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    # Use SQLAlchemy metadata creation for the initial schema to keep the migration
    # synchronized with the model definitions. This is intentionally the first migration only.
    from database.db import Base
    from database import models
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade():
    from database.db import Base
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
