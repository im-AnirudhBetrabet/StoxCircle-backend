from app.services.portfolio_service import compute_positions, compute_nav, compute_user_value, get_pool, \
    get_recent_trade_activity, get_group_metrics


def get_group_dashboard(group_id: str, user_id: str):
    try:
        pool          = get_pool(group_id)
        portfolio     = compute_positions(group_id)
        nav           = compute_nav(pool, portfolio["invested_value"])
        user_value    = compute_user_value(group_id, user_id, nav)
        recent_trades = get_recent_trade_activity(group_id)
        metrics       = get_group_metrics(group_id)

        return {
            "portfolio": portfolio,
            "user"     : user_value,
            "pool": {
                "total_units": round(float(pool["total_units"]), 4),
                "cash"       : round(float(pool["cash_balance"]), 2),
                "nav"        : round(nav, 4)
            },
            "recent_trades": recent_trades,
            "group_metrics": metrics
        }
    except Exception as e:
        return {
            "portfolio": [],
            "user": {
                    "units" : 0.0,
                    "nav"   : 0.0,
                    "value" : 0.0
                },
            "pool": {
                "total_units": 0.0,
                "cash"       : 0.0,
                "nav"        : 0.0
            },
            "recent_trades": [],
            "group_metrics": []
        }