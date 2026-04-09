from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.presentation.api.routers.auth import router as auth_router
from app.presentation.api.routers.ping import router as ping_router
from app.presentation.api.routers.query import router as query_router
from app.presentation.streams.app import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    yield
    await broker.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Algo Solver",
        version="0.1.0",
        root_path="/api",
        lifespan=lifespan,
    )
    app.include_router(ping_router)
    app.include_router(auth_router)
    app.include_router(query_router)
    return app


app = create_app()
