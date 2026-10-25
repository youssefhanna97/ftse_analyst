from sqlalchemy import text

from ftse_analyst.db.connection import get_engine


def test_can_connect_and_see_companies():
    with get_engine().connect() as conn:
        count = conn.execute(text("SELECT count(*) FROM companies")).scalar_one()
    assert count == 25