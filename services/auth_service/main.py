from fastapi import FastAPI
from services.auth_service.api.routes import router
from shared.core.config import settings
from shared.db.database import engine, Base

app = FastAPI(title=settings.PROJECT_NAME)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Подключение роутов
app.include_router(router, prefix="/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Welcome to Auth Service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
