from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger

from src.api.jupyter import router as planet_ns
from src.config import SystemConfig
from src.storage.cache import Cache


app = FastAPI(
    title="Ganimede",
    description="Deploy Jupyter notebooks as ReST endpoints",
    version="1.0-beta"
)

logger.info("Adding notebook namespace route")
app.include_router(planet_ns)


@app.on_event("startup")
def startup():
    logger.info("Initializing application : ganimede")
    logger.info("Loading configuration from env")
    SystemConfig.load()
    logger.remove(0)
    logger.add("./logs/ganimede.log", rotation="5 MB", level=SystemConfig.get("LOG_LEVEL", "WARN"))
    logger.info("Starting cache systems")
    Cache.start()


@app.on_event("shutdown")
def startup():
    logger.info("System shutdown initiated")


@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs")

