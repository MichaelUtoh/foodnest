from fastapi import FastAPI

from app.accounts.routes import router as accounts_router
from app.products.routes import router as products_router
from app.core.database import init_db

app = FastAPI(docs_url="/swagger", title="Foodnest")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    await init_db()
