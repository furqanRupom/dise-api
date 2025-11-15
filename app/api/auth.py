from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.schemas.auth import Register,RegisterResponse,Login,TokenFair
from app.db.database import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register")
async def register_user(register:Register,db:Session = Depends(get_db)) -> RegisterResponse:
    res =  AuthService(db)
    registered_user = res.register(register)
    return registered_user


@router.post("/login")
async def login_user(login:Login,db:Session = Depends(get_db)) -> TokenFair:
    res = AuthService(db)
    logged_in_user = res.login(login)
    return logged_in_user