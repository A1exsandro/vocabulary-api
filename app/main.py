from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.modules import router as modules_router
from app.core.config import db

origins=["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    await db.create_all()
    await db.warmup()
    yield
    if db.engine:
        await db.engine.dispose()
        

app = FastAPI(
    title="Vocabulary Api",
    description="Vocabulary",
    version="1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(modules_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
