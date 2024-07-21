from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="verysecret")

#세션 설정 코드 예시
@app.post("/set/")
async def set_session(request: Request):
    request.session["username"] = "john"
    return {"message": "Session value set"}

#세션 조회 코드 예시
@app.get("/get/")
async def get_session(request: Request):
    username = request.session.get("username", "Guest")
    return {"username": username}

@app.post("/login/")
async def login(request: Request, username: str, password: str):
    if username == "john" and password=="1234":
        request.session["username"] = username
        return {"message": "Suceessfully logged in"}
    else : 
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/dashboard/")
async def dashboard(request: Request):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authorized")
    return {"messsage": f"Welcome to the dashboard, {username}"}