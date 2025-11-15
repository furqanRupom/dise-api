from app.db.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,func,Enum
from sqlalchemy.orm import Mapped,mapped_column
import enum


class UserRole(str,enum.Enum):
  USER = "user"
  ADMIN = "admin"
  
class User(Base):
  __tablename__ = "users"

  id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
  name:Mapped[str] = mapped_column(String,nullable=False)
  password:Mapped[str] = mapped_column(String,nullable=False)
  email:Mapped[str] = mapped_column(String,unique=True,index=True,nullable=False)
  role:Mapped[UserRole] = mapped_column(Enum(UserRole),default=UserRole.USER,nullable=False,index=True)
  is_active:Mapped[bool] = mapped_column(Boolean,default=False)
  created_at:Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now())
  updated_at:Mapped[DateTime] = mapped_column(DateTime(timezone=True),onupdate=func.now())