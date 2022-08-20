"""empty message

Revision ID: 32659e29e645
Revises: 901475339e3d
Create Date: 2022-08-20 13:13:03.848871

"""
from email.policy import default
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32659e29e645'
down_revision = '901475339e3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), default=False))
    op.drop_column('Artist', 'looking_for_venues')
    op.alter_column('Venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               default=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'seeking_talent',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.add_column('Artist', sa.Column('looking_for_venues', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###
