from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

def get_current_username(credentials:HTTPBasicCredentials = Depends(security)):
    if credentials.username != "alice" or credentials.password != "password":
        raise HTTPException(status_code=401, detail = "Unauthorized")
    return credentials.username

@app.get("/users/me")
def read_current_user(username: str = Depends(get_current_username)):
    return {"username": username} 