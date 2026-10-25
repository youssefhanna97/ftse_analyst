import logging

from ftse_analyst.ingestion.prices import ingest_universe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

ingest_universe()