from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.clients.weaviate_schema import create_weaviate_schema

from app.routes.workspace import router as workspace_router
from app.routes.tagging import router as tagging_router
from app.routes.chunk import router as chunking_router
from app.routes.retrieval import router as retrieval_router
from app.routes.search_strategist import router as search_strategist


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_weaviate_schema()
        print("Weaviate schema ready")
    except Exception as e:
        print(f"Weaviate init failed: {e}")

    yield

    print("App shutting down")


app = FastAPI(lifespan=lifespan)

app.include_router(workspace_router)
app.include_router(chunking_router)
app.include_router(tagging_router, prefix="/tagging")
app.include_router(retrieval_router, prefix="/retrieval")
app.include_router(search_strategist, prefix="/search_strategist")


@app.get("/health")
def health():
    return {"status": "ok"}