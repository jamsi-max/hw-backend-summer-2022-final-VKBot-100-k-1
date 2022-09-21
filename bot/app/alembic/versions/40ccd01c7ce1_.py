"""empty message

Revision ID: 40ccd01c7ce1
Revises: 924414ab8882
Create Date: 2022-09-20 16:17:08.856426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40ccd01c7ce1'
down_revision = '924414ab8882'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('games_responder_fkey', 'games', type_='foreignkey')
    op.drop_constraint('games_winner_fkey', 'games', type_='foreignkey')
    op.create_foreign_key(None, 'games', 'players', ['winner'], ['vk_user_id'])
    op.create_foreign_key(None, 'games', 'players', ['responder'], ['vk_user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'games', type_='foreignkey')
    op.drop_constraint(None, 'games', type_='foreignkey')
    op.create_foreign_key('games_winner_fkey', 'games', 'players', ['winner'], ['id'])
    op.create_foreign_key('games_responder_fkey', 'games', 'players', ['responder'], ['id'])
    # ### end Alembic commands ###
