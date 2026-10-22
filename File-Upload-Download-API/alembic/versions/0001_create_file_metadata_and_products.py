"""Create file metadata and products tables."""

from alembic import op
import sqlalchemy as sa


revision = "0001_files_products"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "file_metadata",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "original_filename",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "stored_filename",
            sa.String(length=255),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "relative_path",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "content_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "file_kind",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "uploaded_by",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "uploaded_at",
            sa.DateTime(),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_file_metadata_id",
        "file_metadata",
        ["id"],
    )

    op.create_index(
        "ix_file_metadata_stored_filename",
        "file_metadata",
        ["stored_filename"],
        unique=True,
    )

    op.create_index(
        "ix_file_metadata_file_kind",
        "file_metadata",
        ["file_kind"],
    )

    op.create_index(
        "ix_file_metadata_uploaded_by",
        "file_metadata",
        ["uploaded_by"],
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "image_id",
            sa.Integer(),
            sa.ForeignKey(
                "file_metadata.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_products_id",
        "products",
        ["id"],
    )

    op.create_index(
        "ix_products_name",
        "products",
        ["name"],
    )

    op.create_index(
        "ix_products_owner_id",
        "products",
        ["owner_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_owner_id",
        table_name="products",
    )

    op.drop_index(
        "ix_products_name",
        table_name="products",
    )

    op.drop_index(
        "ix_products_id",
        table_name="products",
    )

    op.drop_table("products")

    op.drop_index(
        "ix_file_metadata_uploaded_by",
        table_name="file_metadata",
    )

    op.drop_index(
        "ix_file_metadata_file_kind",
        table_name="file_metadata",
    )

    op.drop_index(
        "ix_file_metadata_stored_filename",
        table_name="file_metadata",
    )

    op.drop_index(
        "ix_file_metadata_id",
        table_name="file_metadata",
    )

    op.drop_table("file_metadata")