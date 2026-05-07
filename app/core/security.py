from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import supabase
from app.utils.logger import sys_logger

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    try:
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        return response.user
    except Exception as e:
        sys_logger.exception("Unable to authenticate user due to error: ", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token."
        )

def verify_group_membership(user_id: str, group_id: str, require_admin: bool = False) -> str:
    """
    Verifies that the user is part of the group.
    Optionally enforces admin access.
    """

    res = supabase.table("group_members").select("role").eq("group_id", group_id).eq("user_id", user_id).single().execute()

    if not res.data:
        raise HTTPException(403, "You do not have access to this group.")

    user_role = res.data["role"]

    if require_admin and user_role != "admin":
        raise HTTPException(403, "Admin privileges required.")

    return user_role