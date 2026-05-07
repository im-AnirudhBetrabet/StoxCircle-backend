from fastapi import APIRouter, Depends
from app.schemas.trade import BuyRequest, SellRequest
from app.services.trade_service import buy, sell
from app.api.deps import get_user

router = APIRouter()

@router.post("/buy")
def buy_api(payload: BuyRequest, user=Depends(get_user)):
    return buy(user.id, str(payload.group_id), payload.ticker, payload.quantity, payload.price, payload.buy_date)

@router.post("/sell")
def sell_api(payload: SellRequest, user=Depends(get_user)):
    return sell(user.id, str(payload.trade_id), payload.price)

