from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.kvstore_router import kvstore_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n # ========== KVStore Started ========== #")
    yield
    print("\n # ==========  KVStore Ended  ========== #")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kvstore_router)