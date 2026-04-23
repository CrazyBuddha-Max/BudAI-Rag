from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.user import UserService
from schemas.user import UserResponse, UserUpdate
from core.dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])


@router.get("", response_model=list[UserResponse])
async def list_users(admin=Depends(get_admin_user), db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_all()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str, admin=Depends(get_admin_user), db: AsyncSession = Depends(get_db)
):
    return await UserService(db).get_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    data: UserUpdate,
    admin=Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).update(user_id, data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, admin=Depends(get_admin_user), db: AsyncSession = Depends(get_db)
):
    return await UserService(db).delete(user_id)
