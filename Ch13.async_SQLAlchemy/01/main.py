from typing import Optional
from urllib.parse import quote_plus
from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, MetaData, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from sqlalchemy.future import select
from contextlib import asynccontextmanager

#비동기 데이터베이스 설정을 위한 문자열을 정의. 
password = "qwe123!@#"
encoded_password =quote_plus(password)
DATABASE_URL = f"mysql+aiomysql://root:{encoded_password}@localhost:3306/fastapi" # 사용자의 데이터베이스 정보로 변경해야 합니다.

#SQLAlchemy의 비동기 엔진을 생성
engine = create_async_engine(DATABASE_URL,echo=True)

#비동기 세션 생성을 위한 세션메이커를 정의
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
# 1. DB 접속 2. 세션 정의 3. 세션 생성 4. 테이블 정의

@asynccontextmanager  # python contextlib 모듈에서 제공하는 데코레이터 / 데코레이터는 비동기 컨텍스트 매니저를 쉽게 생성할 수 있게 해주는 기능 제공
async def app_lifespan(app: FastAPI):
    #애플리케이션 시작 시 실행될 로직
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    #애플리케이션 종료 시 실행될 로직(필요한 경우)

app = FastAPI(lifespan=app_lifespan)

#SQLAlchemy의 모델 기본 클래스를 선언. 이 클래스를 상속받아 데이터베이스 테이블을 정의할 수 있음
Base = declarative_base()

class User(Base):
    #'users' 테이블을 정의
    __tablename__ = 'users'
    #각 열(column)을 정의합니다. id는 기본 키(primary key)로 설정
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50),unique=True, index=True)
    email = Column(String(120)) #이메일 주소, 길이는 120자로 제한

class UserCreate(BaseModel):
    username: str
    email: str

@app.get("/")
async def read_root():
    #루트 경로에 접근했을 때 비동기적으로 메시지를 반환합니다
    return {"message": "Hello, World!"}

#사용자를 생성하는 Post API 엔드포인트를 추가. 비동기 방식 사용
@app.post("/users/")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(username=user.username, email=user.email)
    db.add(new_user) #생성된 User 인스턴스를 데이터베이스 세션에 추가
    await db.commit() 
    await db.refresh(new_user)

    return {"id":new_user.id, "username":new_user.username, "email": new_user.email}

@app.get("/users/{user_id}")
async def read_user(user_id:int, db:AsyncSession = Depends(get_db)):
    #비동기 세션을 사용하여 데이터베이스 쿼리를 실행합니다
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if db_user is None:
        return {"error": "User not found"}
    return {"id":db_user.id, "username": db_user.username, "email":db_user.email}

@app.get("/count")
async def count_user(db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(func.count()).select_from(User))
    count = result.scalars().one()
    return {"count": count}

#Pydantic 모델 정의
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email : Optional[str] = None
    
#Update 부분을 비동기로 변환
@app.put("/users/{user_id}")
async def update_user(user_id:int, user:UserUpdate, db:AsyncSession=Depends(get_db)):
    #비동기 쿼리 실행
    result = await db.execute(select(User).filter(User.id==user_id))
    db_user = result.scalars().first()

    if db_user is None:
        return {"error": "User not found"}
    
    #사용자 정보 업데이트
    if user.username is not None:
        db_user.username = user.username
    if user.email is not None:
        db_user.email = user.email
    
    #데이터베이스 커밋 및 객체 새로고침
    await db.commit()
    await db.refresh(db_user)

    return {"id":db_user.id, "username": db_user.username, "email": db_user.email}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    #비동기 쿼리 실행하여 사용자 찾기
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()

    if db_user is None:
        return {"error":"사용자를 찾을 수 없습니다"}
    
    #사용자 삭제 및 데이터베이스 커밋
    await db.delete(db_user)
    await db.commit()
    return {"message": "사용자가 성공적으로 삭제되었습니다"}