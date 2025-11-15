from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.schemas.auth import Register,RegisterResponse,Login,TokenFair,TokenData
from app.core.settings import hash_password,verify_password,create_access_token,create_refresh_token
from app.models.user import User
class AuthService:
    def __init__(self,db:Session):
        self.db = db

    def findById(self,email:str):
            user = self.db.query(User).filter_by(email=email).first()
            if not user:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not exit",
            )
            return user

    def register(self,register:Register) -> RegisterResponse:
        is_exit = self.db.query(User).filter(User.email == register.email).first()
        if is_exit:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User Already Exits with this Email",
            )
        
        passwordHash = hash_password(register.password)

        new_user = User(
            name=register.name,
            email=register.email,
            password=passwordHash
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
        except :
            self.db.rollback()
            raise 
      
        return RegisterResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
        )

    def login(self,data:Login) -> TokenFair:
        user = self.findById(data.email)
        verify_pass = verify_password(data.password,user.password)
        if not verify_pass:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password didnot matched!"
            )
        
        token_data = TokenData(
            id=user.id,
            role=user.role
        )
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        return TokenFair(
            access_token=access_token,
            refresh_token=refresh_token
        )
        

        

        

        pass

      




        


