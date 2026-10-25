from functools import lru_cache

from sqlalchemy import Engine, create_engine

from ftse_analyst.config import settings


@lru_cache
def get_engine() -> Engine:
    return create_engine(settings.database_url, pool_pre_ping=True)