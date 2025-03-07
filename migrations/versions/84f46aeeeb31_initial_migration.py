"""Initial migration

Revision ID: 84f46aeeeb31
Revises: 
Create Date: 2025-03-05 09:37:04.742822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84f46aeeeb31'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('production',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quarter_1_production', sa.Integer(), nullable=False),
    sa.Column('quarter_2_production', sa.Integer(), nullable=False),
    sa.Column('quarter_3_production', sa.Integer(), nullable=False),
    sa.Column('quarter_4_production', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('energy_well',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('api_well_number', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('well_type', sa.String(length=5), nullable=False),
    sa.Column('oil_id', sa.Integer(), nullable=True),
    sa.Column('gas_id', sa.Integer(), nullable=True),
    sa.Column('brine_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['brine_id'], ['production.id'], ),
    sa.ForeignKeyConstraint(['gas_id'], ['production.id'], ),
    sa.ForeignKeyConstraint(['oil_id'], ['production.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('api_well_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('energy_well')
    op.drop_table('production')
    # ### end Alembic commands ###
