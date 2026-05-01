"""
Mourya Scholarium — Auth Router
POST /api/v1/auth/register
POST /api/v1/auth/login
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User
from dependencies import hash_password, verify_password, create_token

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str
    institution: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    name: str
    email: str


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        email=req.email,
        name=req.name,
        hashed_password=hash_password(req.password),
        institution=req.institution,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(str(user.id))
    return AuthResponse(token=token, user_id=str(user.id), name=user.name, email=user.email)


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(str(user.id))
    return AuthResponse(token=token, user_id=str(user.id), name=user.name, email=user.email)
