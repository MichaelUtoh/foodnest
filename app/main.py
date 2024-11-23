from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.accounts.routes import router as accounts_router
from app.products.routes import router as products_router
from app.orders.routes import router as orders_router
from app.core.database import init_db

app = FastAPI(docs_url="/swagger", title="Foodnest")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    await init_db()
