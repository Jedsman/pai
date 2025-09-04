# === main.py ===
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import tasks, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Task Manager API starting up...")
    yield
    print("📴 Task Manager API shutting down...")

app = FastAPI(
    title="AI Task Manager",
    description="A FastAPI demo with Pydantic AI integration",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
