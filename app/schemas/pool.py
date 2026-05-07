from pydantic import BaseModel, Field
from uuid import UUID

class DepositRequest(BaseModel):
    group_id: UUID
    user_id : UUID
    amount  : float = Field(gt=0)

class WithdrawRequest(BaseModel):
    group_id: UUID
    user_id : UUID
    amount  : float = Field(gt=0)