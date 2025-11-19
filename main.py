from fastapi import FastAPI, Depends
from presentation.api import router
from infrastructure.db.session import init_db
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Инициализация базы данных...")
    init_db()
    logger.info("База данных инициализирована")
    yield
    logger.info("Завершение работы приложения")

app = FastAPI(
    title="Новостной сайт",
    description="CRUD-сервис новостей с REST API и Swagger",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}