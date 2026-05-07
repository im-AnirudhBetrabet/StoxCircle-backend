from fastapi import Depends
from app.core.security import get_current_user

def get_user(user=Depends(get_current_user)):
    return user
