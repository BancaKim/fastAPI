from typing import Optional
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, create_engine, or_, desc, func
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote_plus

# DB 설정

password = "qwe123!@#"
encoded_password =quote_plus(password)
DATABASE_URL = f"mysql+pymysql://root:{encoded_password}@localhost:3306/fastapi" # 사용자의 데이터베이스 정보로 변경해야 합니다.
engine = create_engine(DATABASE_URL)

# SQLAlchemy 모델
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # 길이를 50으로 설정
    email = Column(String(120))  # 길이를 120으로 설정

# Session 초기화 의존성
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

# DB에 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 초기화
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Create 부분 추가
@app.post("/users/")
def create_user(username: str, email: str, db: Session = Depends(get_db)):
    new_user = User(username=username, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    # db_user = db.query(User).filter(User.id == user_id).first()
    # db_users = db.query(User).all()
    # db_users = db.query(User.username).all()
    # db_users = db.query(User).filter(User.username=='gun').first()
    # db_users = db.query(User).filter(User.username=='gun').filter(User.email=='gun@naver.com').first()
    # db_users = db.query(User).filter(or_(User.username=='gun',User.email=='gun@naver.com')).first()
    
    #결과 정렬
    # db_users = db.query(User).order_by(desc(User.username)).limit(1).all()

    #결과 제한
    # db_users = db.query(User).limit(5).all()

    #결과 건너뛰기(처음 2개 건너뛰기)
    # db_users = db.query(User).offset(2).all()

    #결과 개수 세기
    count = db.query(User).count()

    #그룹핑 : 특정컬럼을 기준으로 그룹핑함
    grouped = db.query(User.username, func.count(User.id).label('user_count')).groub_by(User.username).all()

    # if db_users ==[]:
    #     return {"error": "User not found"}
    return {"count":count}

#Pydantic 모델
class UserUpdate(BaseModel):
    username: Optional[str]= None
    email : Optional[str]= None

#update 부분
@app.put("/users/{user_id}")
def update_user(user_id: int, user:UserUpdate, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        return {"error":"User not found"}
    
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
        
    db.commit()
    db.refresh(db_user)
    return {"id":db_user.id, "username": db_user.username, "email":db_user.email}

#Delete 부분
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        return {"error": "사용자를 찾을 수 없습니다"}
    db.delete(db_user)
    db.commit()
    return {"message": "사용자가 성공적으로 삭제되었습니다"}