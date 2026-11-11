from fastapi import APIRouter

from app.api.routers import categories, health, leads, products, shop

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(leads.router)
api_router.include_router(shop.router)
