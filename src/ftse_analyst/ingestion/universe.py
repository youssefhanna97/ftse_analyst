import logging
import time
from collections.abc import Callable

from sqlalchemy import text

from ftse_analyst.db.connection import get_engine

log = logging.getLogger(__name__)


def active_tickers() -> list[str]:
    """The universe, read from the companies table."""
    with get_engine().connect() as conn:
        rows = conn.execute(text("SELECT ticker FROM companies WHERE is_active ORDER BY ticker"))
        return list(rows.scalars())


def run_for_universe(job: Callable[[str], int], job_name: str, pause_seconds: float = 1.0) -> dict[str, int]:
    """Run job(ticker) for every active ticker. Keeps going on failure, raises at the end if any failed."""
    loaded: dict[str, int] = {}
    failed: dict[str, str] = {}
    for ticker in active_tickers():
        try:
            loaded[ticker] = job(ticker)
            log.info("%s %s: %d rows", job_name, ticker, loaded[ticker])
        except Exception as exc:
            failed[ticker] = str(exc)
            log.exception("%s %s: failed", job_name, ticker)
        time.sleep(pause_seconds)

    log.info("%s finished: %d succeeded, %d failed", job_name, len(loaded), len(failed))
    if failed:
        raise RuntimeError(f"{job_name} failed for: {sorted(failed)}")
    return loaded