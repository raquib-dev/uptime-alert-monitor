from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User
from app.utils.security import verify_password
from app.utils.token import create_access_token

router = APIRouter()

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(hours=12)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer"}
