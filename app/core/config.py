from pydantic_settings import BaseSettings,SettingsConfigDict
from pydantic import ConfigDict
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class Settings(BaseSettings):
  model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, '..', '..', '.env'),
        env_file_encoding='utf-8',
        case_sensitive=True,
    )
#   APP CONFIG
  APP_NAME :str =  "Dise API"
  VERSION :str = "1.0.0"

#   TOKEN CONFIG

  ALGORITHMS:str = "HS256"
  SECRET_ACCESS_TOKEN:str ="" # change to yours
  SECRET_REFRESH_TOKEN:str = "abcdefg"
  ACCESS_TOKEN_EXPIRE_MINUTES:int=15
  REFRESH_TOKEN_EXPIRE_DAYS:int=30


# DB
  DATABASE_URL:str = "postgresql://diseuser:disepassword@localhost:5432/disedb"

    
settings = Settings()