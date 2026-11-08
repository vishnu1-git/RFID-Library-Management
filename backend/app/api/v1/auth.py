from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, SmartCardLoginRequest, Token, UserResponse
from app.core.security import verify_password, create_access_token
from app.core.permissions import get_current_active_user
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(credentials: LoginRequest, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    role_names = [ur.role.name for ur in user.roles if ur.role]
    primary_role = role_names[0] if role_names else ("Admin" if user.is_superuser else "Operator")
    
    access_token = create_access_token(subject=user.username, role=primary_role)
    
    AuditService.log_action(
        db=db,
        user_id=user.id,
        action="LOGIN_PASSWORD",
        entity_type="USER",
        entity_id=str(user.id),
        details={"username": user.username}
    )

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        smart_card_uid=user.smart_card_uid,
        created_at=user.created_at,
        roles=role_names
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user_resp}


@router.post("/smartcard-login", response_model=Token)
def smartcard_login(req: SmartCardLoginRequest, db: Session = Depends(get_db)) -> Any:
    # AISYS Scenario AC 07: Smart-card login
    user = db.query(User).filter(User.smart_card_uid == req.smart_card_uid, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Smart card UID '{req.smart_card_uid}' is not mapped to any authorized staff member.",
        )

    role_names = [ur.role.name for ur in user.roles if ur.role]
    primary_role = role_names[0] if role_names else ("Admin" if user.is_superuser else "Operator")
    access_token = create_access_token(subject=user.username, role=primary_role)

    AuditService.log_action(
        db=db,
        user_id=user.id,
        action="LOGIN_SMARTCARD",
        entity_type="USER",
        entity_id=str(user.id),
        details={"smart_card_uid": req.smart_card_uid}
    )

    user_resp = UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        smart_card_uid=user.smart_card_uid,
        created_at=user.created_at,
        roles=role_names
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user_resp}


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> Any:
    role_names = [ur.role.name for ur in current_user.roles if ur.role]
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        smart_card_uid=current_user.smart_card_uid,
        created_at=current_user.created_at,
        roles=role_names
    )
