from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.audit import AuditLog
from app.models.user import User, Role, UserRole
from app.schemas.report import AuditLogResponse
from app.schemas.auth import UserResponse, UserCreate
from app.core.security import get_password_hash
from app.core.permissions import require_roles

router = APIRouter()


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    logs = q.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
    results = []
    for l in logs:
        results.append(AuditLogResponse(
            id=l.id,
            user_id=l.user_id,
            username=l.user.username if l.user else None,
            action=l.action,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            details=l.details,
            ip_address=l.ip_address,
            timestamp=l.timestamp
        ))
    return results


@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    users = db.query(User).all()
    out = []
    for u in users:
        role_names = [ur.role.name for ur in u.roles if ur.role]
        out.append(UserResponse(
            id=u.id,
            email=u.email,
            username=u.username,
            full_name=u.full_name,
            is_active=u.is_active,
            is_superuser=u.is_superuser,
            smart_card_uid=u.smart_card_uid,
            created_at=u.created_at,
            roles=role_names
        ))
    return out


@router.post("/users", response_model=UserResponse)
def create_staff_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin"]))
):
    existing = db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered.")

    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        smart_card_uid=user_in.smart_card_uid
    )
    db.add(new_user)
    db.flush()

    for r_name in user_in.role_names:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name)
            db.add(role)
            db.flush()
        db.add(UserRole(user_id=new_user.id, role_id=role.id))

    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        smart_card_uid=new_user.smart_card_uid,
        created_at=new_user.created_at,
        roles=user_in.role_names
    )

