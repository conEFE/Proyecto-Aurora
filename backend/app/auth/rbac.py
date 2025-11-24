from fastapi import Depends, HTTPException
from app.auth.bearer import get_token_from_header, get_role_from_token

def require_role(allowed_roles: list[str]):
    def role_checker(token: str = Depends(get_token_from_header)):
        role = get_role_from_token(token)
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Role {role} not allowed")
        return role
    return role_checker

def get_current_user_role(token: str = Depends(get_token_from_header)) -> str:
    return get_role_from_token(token)