from fastapi import APIRouter, Depends
from app.api.deps import get_user
from app.core.security import verify_group_membership
from app.services.dashboard_service import get_group_dashboard

router = APIRouter()

@router.get("/{group_id}")
def dashboard(group_id: str, user=Depends(get_user)):
    verify_group_membership(user.id, group_id)

    return get_group_dashboard(group_id, user.id)