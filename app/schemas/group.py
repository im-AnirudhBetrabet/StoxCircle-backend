from pydantic import BaseModel, Field
from uuid import UUID

class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)

class JoinRequest(BaseModel):
    group_id: UUID

class ApproveRequest(BaseModel):
    request_id: UUID

class GroupResponse(BaseModel):
    id  : UUID
    name: str
