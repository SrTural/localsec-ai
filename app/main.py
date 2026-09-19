from fastapi import FastAPI
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Local AI Log Analyzer for Cybersecurity",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} API is running!"}
