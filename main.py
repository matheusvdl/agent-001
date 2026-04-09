import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server is up and running")
    yield
    logger.info("Server is shutting down")


app = FastAPI(title="AI Agent API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
