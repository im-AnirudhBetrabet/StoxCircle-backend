from typing import Dict, List
from fastapi import HTTPException, status
from app.core.supabase import supabase
from app.core.db import handle_response
from app.services.price_service import get_current_price

def get_pool(group_id: str) -> dict:
    res = supabase.table("group_pools").select("*").eq("group_id", group_id).maybe_single().execute()

    if not res.data:
         return {
             "group_id"    : group_id,
             "cash_balance": 0,
             "total_units" : 0
         }

    return res.data

def get_recent_trade_activity(group_id: str):
    res = supabase.rpc("get_recent_trade_activity", {
        "p_group_id": group_id
    }).execute()

    recent_trade_data = handle_response(res) or []
    return recent_trade_data

def get_user_units(group_id: str, user_id: str) -> float:
    res = supabase.table("user_units").select("units").eq("group_id", group_id).eq("user_id", user_id).maybe_single().execute()
    if res is None or not res.data:
        return 0.0

    return float(res.data["units"])

def get_trades(group_id: str):
    res = supabase.table("trades").select("*").eq("group_id", group_id).execute()
    return handle_response(res) or []

def compute_positions(group_id: str) -> Dict:
    """
    Returns per-ticker aggregation + totals
    - quantity
    - avg_price
    - current_price
    - market_value
    - unrealized_pnl
    """
    all_trades = get_trades(group_id)

    open_trades   = [trade for trade in all_trades if trade['status'] == "OPEN"]
    closed_trades = [trade for trade in all_trades if trade['status'] == "CLOSED"]

    realized_pnl = round(float(sum(t['realized_pnl'] for t in closed_trades)), 2) or 0.0

    aggregate: Dict[str, dict] = {}


    for t in open_trades:
        ticker = t["ticker"]
        qty    = float(t["quantity"])
        price  = float(t["buy_price"])
        id     = t["id"]
        buy_date = t["created_at"]

        if ticker not in aggregate:
            aggregate[ticker] = {
                "quantity": 0.0,
                "ticker"  : ticker,
                "cost"    : 0.0,
                "id"      : id,
                "buy_date": buy_date
            }

        aggregate[ticker]["quantity"] += qty
        aggregate[ticker]["cost"]     += qty * price

    total_invested_value         = 0.0
    total_unrealized_pnl         = 0.0
    positions                    = []
    sector_map: Dict[str, float] = {}

    for ticker, data in aggregate.items():
        qty  = data["quantity"]
        cost = data["cost"]
        id   = data["id"]

        buy_date = data["buy_date"]

        if qty == 0:
            continue

        avg_price             = cost / qty
        current_price, sector = get_current_price(ticker)
        market_value          = current_price * qty
        unrealized            = (current_price - avg_price) * qty

        total_invested_value += market_value
        total_unrealized_pnl += unrealized
        sector_map[sector]    = sector_map.get(sector, 0.0) + market_value

        positions.append({
            "unrealized_pnl": round(unrealized, 2),
            "market_value"  : round(market_value, 2),
            "current_price" : round(current_price, 2),
            "avg_price"     : round(avg_price, 2),
            "quantity"      : round(qty, 4),
            "ticker"        : ticker,
            "trade_id"      : id,
            "buy_date"      : buy_date,
            "sector"        : sector
        })

    sector_allocation = []
    if total_invested_value > 0:
        for sector, value in sector_map.items():
            sector_allocation.append({
                "sector": sector,
                "value" : round(value, 2),
                "share" : round((value / total_invested_value) * 100, 2)
            })
    sector_allocation.sort(key= lambda x: x["share"], reverse=True)
    return {
        "unrealized_pnl"   : round(total_unrealized_pnl, 2),
        "realized_pnl"     : realized_pnl,
        "invested_value"   : round(total_invested_value, 2),
        "positions"        : positions,
        "sector_allocation": sector_allocation
    }

def compute_nav(pool: dict, invested_value:float) -> float:
    total_units = float(pool["total_units"])
    cash        = float(pool["cash_balance"])

    if total_units == 0:
        return 10.0

    total_value = cash + invested_value
    return total_value / total_units

def compute_user_value(group_id: str, user_id: str, nav: float) -> dict:
    units = get_user_units(group_id, user_id)

    value = units * nav

    return {
        "units" : round(units, 4),
        "nav"   : round(nav, 4),
        "value" : round(value, 2)
    }

def get_group_metrics(group_id: str) -> dict:
    metrics_res = supabase.rpc("get_trade_statistics", {
        "p_group_id": group_id
    }).execute()

    metrics = handle_response(metrics_res) or {}

    return metrics