from app.utils.logger import sys_logger
from fastapi import HTTPException, status
from app.core.supabase import supabase
from app.core.db import handle_response
from app.core.security import verify_group_membership

def deposit(user_id: str, group_id: str, amount: float):
    sys_logger.info(f"Deposit requested | user={user_id} | group={group_id}| amount={amount}")

    verify_group_membership(user_id, group_id)

    res = supabase.rpc("deposit_to_pool", {
        "p_group_id": group_id,
        "p_user_id" : user_id,
        "p_amount"  : amount,
    }).execute()

    handle_response(res)

    sys_logger.info(f"Deposit successful: user={user_id}, amount={amount}")

    return {
        "status": "success"
    }

def withdraw(user_id: str, group_id: str, amount: float):
    sys_logger.info(f"Withdraw requested | user={user_id} | amount={amount}")

    verify_group_membership(user_id, group_id)

    res = supabase.rpc("withdraw_from_pool", {
        "p_group_id": group_id,
        "p_user_id" : user_id,
        "p_amount" : amount
    }).execute()

    handle_response(res)

    sys_logger.info(f"Withdraw successful: user={user_id}, amount={amount}")

    return {
        "status": "success"
    }

