"""Autorización por rol. El rol se lee del usuario en la BD, nunca del token."""

from fastapi import Depends, HTTPException, status

from app.auth.bearer import get_current_user
from app.db.models.user import User, UserRole


def require_roles(*roles: UserRole):
    allowed = {r.value if isinstance(r, UserRole) else str(r) for r in roles}

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return user

    checker.allowed_roles = sorted(allowed)  # usado por scripts/gen_docs.py
    return checker
