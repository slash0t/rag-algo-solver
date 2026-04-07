from fastapi import FastAPI

from app.presentation.api.routers.ping import router as ping_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG Algo Solver",
        version="0.1.0",
    )
    app.include_router(ping_router)
    return app


app = create_app()
