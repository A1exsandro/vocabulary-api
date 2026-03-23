from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import db
from app.core.exception_handlers import register_exception_handlers
from app.modules import router as modules_router

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

register_exception_handlers(app)

app.include_router(modules_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
