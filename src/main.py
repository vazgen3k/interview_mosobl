from fastapi import FastAPI

from src.router import router as router_uuid

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Подключение роутера к приложению
app.include_router(router_uuid)
