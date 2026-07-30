from fastapi import FastAPI,status
from app.api.auth import router as auth_router
app = FastAPI()

app.include_router(auth_router)

@app.get("/",status_code=status.HTTP_200_OK)
async def hello():
    return {
        "statusCode":status.HTTP_200_OK,
        "message":"successfully running!",
        "docs":"/docs",
        "data":{
            "greetings":"Hello!"
        }
    }
           

