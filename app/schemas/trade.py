from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class BuyRequest(BaseModel):
    group_id: UUID
    quantity: float = Field(gt=0)
    price   : float = Field(gt=0)
    ticker  : str
    buy_date: datetime

class SellRequest(BaseModel):
    trade_id: UUID
    price   : float = Field(gt=0)