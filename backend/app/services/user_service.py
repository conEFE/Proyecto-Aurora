import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.db.models.user import User, UserRole, compose_full_name, split_full_name
from app.schemas.users import UserCreate, UserUpdate
from app.services import activation_service
from app.services.audit_service import audit
from app.services.errors import ConflictError, NotFoundError, ValidationError
from app.services.password_policy import ensure_valid_password


def list_users(db: Session, role: UserRole | None = None, active: bool | None = None) -> list[User]:
    q = db.query(User)
    if role is not None:
        q = q.filter(User.role == role)
    if active is not None:
        q = q.filter(User.is_active == active)
    return q.order_by(User.id.desc()).all()


def create_user(
    db: Session, data: UserCreate, actor: User, ip: str | None = None
) -> tuple[User, str | None]:
    """Crea el usuario. Devuelve también el token de activación (en claro) si corresponde enviarlo por email."""
    if db.query(User).filter(User.rut == data.rut).first():
        raise ConflictError("Ya existe un usuario con ese RUT")
    if db.query(User).filter(User.email == data.email).first():
        raise ConflictError("Ya existe un usuario con ese email")
    if data.password:
        ensure_valid_password(data.password, data.rut)
        password = data.password
    else:
        # Contraseña aleatoria que nadie conoce: el usuario define la suya desde el link de activación
        password = secrets.token_urlsafe(32)
    user = User(
        rut=data.rut,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        full_name=compose_full_name(data.first_name, data.last_name),
        specialty=data.specialty,
        password_hash=hash_password(password),
        role=data.role,
        is_active=True,
        # La contraseña la define el ADMIN: el usuario debe cambiarla en su primer ingreso
        must_change_password=True,
        password_changed_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.flush()
    detail = {"role": user.role.value}
    if user.specialty is not None:
        detail["specialty"] = user.specialty.value
    audit(db, actor, "CREATE", "user", user.id, detail, ip, commit=False)
    token = None
    if data.send_activation or not data.password:
        token = activation_service.issue_activation_token(db, user)
    db.commit()
    db.refresh(user)
    return user, token


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
    if changes.get("password"):
        ensure_valid_password(changes["password"], user.rut)
    # Nombre: si llega full_name sin nombre/apellido, se divide; si llega nombre o apellido, se recompone
    if changes.get("full_name") and not (changes.get("first_name") or changes.get("last_name")):
        changes["first_name"], changes["last_name"] = split_full_name(changes.pop("full_name"))
    else:
        changes.pop("full_name", None)
    if changes.get("first_name") or changes.get("last_name"):
        changes["full_name"] = compose_full_name(
            changes.get("first_name") or user.first_name, changes.get("last_name") or user.last_name
        )
    # Cambio de email: queda sin verificar hasta que vuelva a activarse
    email_changed = "email" in changes and changes["email"] is not None and changes["email"] != user.email
    if (changes.get("role") or user.role) != UserRole.MEDICO:
        if changes.get("specialty") is not None:
            raise ValidationError("Solo los médicos tienen especialidad")
        user.specialty = None
    changed_fields = []
    for field, value in changes.items():
        if value is None:
            continue
        if field == "password":
            user.password_hash = hash_password(value)
            # Restablecimiento: revoca sus sesiones, quita el bloqueo y exige cambiarla al ingresar
            user.password_changed_at = datetime.now(timezone.utc)
            user.must_change_password = True
            user.failed_login_attempts = 0
            user.locked_until = None
        else:
            setattr(user, field, value)
        changed_fields.append(field)
    if email_changed:
        user.email_verified_at = None
    detail = {"fields": changed_fields}
    if "role" in changes and changes["role"] is not None:
        detail["role"] = changes["role"].value
    if "is_active" in changes:
        detail["is_active"] = changes["is_active"]
    audit(db, actor, "UPDATE", "user", user.id, detail, ip, commit=False)
    db.commit()
    db.refresh(user)
    return user


def unlock_user(db: Session, user_id: int, actor: User, ip: str | None = None) -> User:
    """Quita el bloqueo por intentos fallidos antes de que expire."""
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Usuario no encontrado")
    user.failed_login_attempts = 0
    user.locked_until = None
    audit(
        db, actor, "UPDATE", "user", user.id, {"fields": ["locked_until"], "unlock": True}, ip, commit=False
    )
    db.commit()
    db.refresh(user)
    return user
