
from fastapi import APIRouter
from app.api.v1 import auth, refs, price_list, sales, reconciliation, store_coefficients, bonus_grids, shipments, imports, moves, inventory

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(refs.router)
api_router.include_router(price_list.router)
api_router.include_router(sales.router)
api_router.include_router(reconciliation.router)
api_router.include_router(store_coefficients.router)
api_router.include_router(bonus_grids.router)
api_router.include_router(shipments.router)
api_router.include_router(imports.router)
api_router.include_router(moves.router)
api_router.include_router(inventory.router)
