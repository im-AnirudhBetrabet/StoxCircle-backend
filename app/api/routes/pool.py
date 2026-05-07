from fastapi import APIRouter, Depends
from app.schemas.pool import DepositRequest, WithdrawRequest
from app.services.pool_service import deposit, withdraw
from app.api.deps import get_user

router = APIRouter()

@router.post("/deposit")
def deposit_api(payload: DepositRequest, user=Depends(get_user)):
    return deposit(str(payload.user_id), str(payload.group_id), payload.amount)

@router.post("/withdraw")
def withdraw_api(payload: WithdrawRequest, user=Depends(get_user)):
    return withdraw(str(payload.user_id), str(payload.group_id), payload.amount)
