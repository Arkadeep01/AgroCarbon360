## backend/src/auth/permissions.py
from fastapi import Depends, HTTPException, status
from .auth_service import get_current_user
from . import models

def require_role(role_name: str):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role is None or current_user.role.name != role_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {role_name} role",
            )
        return current_user
    return role_checker