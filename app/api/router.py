from fastapi import APIRouter
from app.api.routes import pool, trades, groups, dashboard, auth, stock

api_router = APIRouter()

api_router.include_router(pool.router     , prefix="/pool"     , tags=["Investment Pool"]  )
api_router.include_router(trades.router   , prefix="/trade"    , tags=["Trades"]           )
api_router.include_router(groups.router   , prefix="/groups"   , tags=["Investment Groups"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Group Investment Dashboard"])
api_router.include_router(auth.router     , prefix="/auth"     , tags=["Authentication"])
api_router.include_router(stock.router    , prefix="/stock"    , tags=["Stock Price History"])