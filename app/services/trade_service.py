from datetime import datetime

from fastapi import HTTPException, status

from app.core.supabase import supabase
from app.utils.logger import sys_logger
from app.core.db import handle_response
from app.core.security import verify_group_membership

def buy(user_id: str, group_id:str, ticker: str, quantity: float, price: float, buy_date):
    sys_logger.info(f"BUY | group={group_id} | {ticker} | qty={quantity} | price={price}")

    verify_group_membership(user_id, group_id)

    res = supabase.rpc("buy_stock", {
        "p_group_id": str(group_id),
        "p_quantity": quantity,
        "p_ticker"  : ticker,
        "p_price"   : price,
        "p_buy_date": buy_date.isoformat()
    }).execute()

    handle_response(res)

    return {
        "status": "brought"
    }

def sell(user_id: str, trade_id: str, price: float):
    sys_logger.info(f"SELL | trade={trade_id} | price={price}")

    trade = supabase.table("trades").select("group_id").eq("id", trade_id).single().execute()

    if not trade.data:
        raise HTTPException(status_code=status.HTTP_404, detail="Trade not found")

    group_id = trade.data["group_id"]

    verify_group_membership(user_id, group_id)

    res = supabase.rpc("sell_stock", {
        "p_trade_id": str(trade_id),
        "p_price"   : price
    }).execute()

    handle_response(res)

    return {
        "status": "sold"
    }
