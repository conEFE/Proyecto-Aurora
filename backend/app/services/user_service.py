from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.db.models.user import User, UserRole
from app.schemas.users import UserCreate, UserUpdate
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError, ValidationError


def list_users(db: Session, role: UserRole | None = None, active: bool | None = None) -> list[User]:
    q = db.query(User)
    if role is not None:
        q = q.filter(User.role == role)
    if active is not None:
        q = q.filter(User.is_active == active)
    return q.order_by(User.id.desc()).all()


def create_user(db: Session, data: UserCreate, actor: User, ip: str | None = None) -> User:
    if db.query(User).filter(User.rut == data.rut).first():
        raise ConflictError("Ya existe un usuario con ese RUT")
    if db.query(User).filter(User.email == data.email).first():
        raise ConflictError("Ya existe un usuario con ese email")
    user = User(
        rut=data.rut,
        email=data.email,
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    audit(db, actor, "CREATE", "user", user.id, {"role": user.role.value}, ip, commit=False)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate, actor: User, ip: str | None = None) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado")
    changes = data.model_dump(exclude_unset=True)
    if user.id == actor.id and (
        changes.get("is_active") is False or changes.get("role", UserRole.ADMIN) != UserRole.ADMIN
    ):
        raise ValidationError("No puede desactivarse ni quitarse el rol de administrador a sí mismo")
    if "email" in changes and changes["email"] != user.email:
        if db.query(User).filter(User.email == changes["email"], User.id != user.id).first():
            raise ConflictError("Ya existe un usuario con ese email")
    changed_fields = []
    for field, value in changes.items():
        if value is None:
            continue
        if field == "password":
            user.password_hash = hash_password(value)
        else:
            setattr(user, field, value)
        changed_fields.append(field)
    detail = {"fields": changed_fields}
    if "role" in changes and changes["role"] is not None:
        detail["role"] = changes["role"].value
    if "is_active" in changes:
        detail["is_active"] = changes["is_active"]
    audit(db, actor, "UPDATE", "user", user.id, detail, ip, commit=False)
    db.commit()
    db.refresh(user)
    return user
