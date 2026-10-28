import logging

from ftse_analyst.ingestion.fundamentals import ingest_universe_fundamentals

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

ingest_universe_fundamentals()