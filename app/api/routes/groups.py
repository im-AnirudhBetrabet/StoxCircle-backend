from fastapi import APIRouter, Depends, Query
from app.api.deps import get_user
from app.core.security import verify_group_membership
from app.schemas.group import CreateGroupRequest, JoinRequest, ApproveRequest, GroupResponse
from app.services.group_service import create_group, request_to_join, approve_join_request, get_user_groups, \
    get_pending_join_requests, search_groups, group_members, reject_join_request, group_info
from typing import List

router = APIRouter()

@router.post("/create", response_model=GroupResponse)
def create_group_api(payload: CreateGroupRequest, user = Depends(get_user)):
    return create_group(user.id, payload.name)

@router.post("/join")
def request_join_api(payload: JoinRequest, user=Depends(get_user)):
    return request_to_join(user.id, str(payload.group_id))

@router.post("/approve")
def approve_join_api(payload: ApproveRequest, user = Depends(get_user)):
    return approve_join_request(user.id, str(payload.request_id))

@router.post("/reject")
def reject_join_api(payload: ApproveRequest, user = Depends(get_user)):
    return reject_join_request(user.id, str(payload.request_id))

@router.get("/")
def get_user_groups_api(user=Depends(get_user)):
    return get_user_groups(str(user.id))

@router.get("/{group_id}/pending-requests")
def get_pending_join_requests_api(group_id: str, user=Depends(get_user)):
    verify_group_membership(user.id, group_id, require_admin=True)
    return get_pending_join_requests(group_id)

@router.get("/search")
def search_groups_api(query: str = Query("", min_length=1), user = Depends(get_user)):
    return search_groups(user.id, query)

@router.get("/{group_id}/members")
def get_group_members_api(group_id: str, user = Depends(get_user)):
    role = verify_group_membership(str(user.id), group_id=group_id)
    return group_members(group_id, role)

@router.get("/{group_id}/info")
def get_group_info_api(group_id: str, user = Depends(get_user)):
    role = verify_group_membership(str(user.id), group_id)
    return group_info(group_id, role)