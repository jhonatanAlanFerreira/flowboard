from fastapi import FastAPI

from app.routes.workspace import router as workspace_router
from app.routes.tagging import router as tagging_router
# from app.routes.embedding import router as embedding_router

app = FastAPI()

app.include_router(workspace_router)
app.include_router(tagging_router, prefix="/tagging")
# app.include_router(embedding_router, prefix="/embedding")


@app.get("/health")
def health():
    return {"status": "ok"}