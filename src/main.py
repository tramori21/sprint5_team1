from fastapi import FastAPI

from src.api.v1.routers import api_router
from src.lifespan import lifespan

app = FastAPI(title="movies", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
