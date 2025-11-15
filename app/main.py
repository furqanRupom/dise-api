from fastapi import FastAPI,Request,Query,Cookie,Header,Response,status,HTTPException,Depends
from pydantic import BaseModel,Field
from typing import Annotated
from app.utils.enums import Tags
from app.api.auth import router as auth_router
app = FastAPI()

app.include_router(auth_router)

@app.get("/",status_code=status.HTTP_200_OK)
async def hello():
    return {
        "statusCode":status.HTTP_200_OK,
        "message":"successfully running!",
        "data":{
            "greetings":"Hello!"
        }
    }
           

