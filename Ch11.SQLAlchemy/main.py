from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime,Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from urllib.parse import quote_plus
from datetime import datetime

#데이터베이스 설정을 위한 문자열을 정의합니다. 이 문자열에는 사용자 이름, 비밀번호, 서버 주, 데이터베이스 이름이 포함되어 있습니다.

password = "qwe123!@#"
encoded_password =quote_plus(password)
DATABASE_URL = f"mysql+pymysql://root:{encoded_password}@localhost:3306/fastapi" # 사용자의 데이터베이스 정보로 변경해야 합니다.
engine = create_engine(DATABASE_URL)

#SQLAlchemy의 모델 기본 클래스를 선언합니다. 이 클래스를 상속받아 데이터베이스 테이블을 정의할 수 있습니다.
Base = declarative_base()

class User(Base):
    #'users' 테이블을 정의한다.
    __tablename__ = 'users'
    #각 열(column)을 정의합니다. id는 기본 키(primary key)로 설정됩니다. 
    id = Column(Integer, primary_key= True, autoincrement=True, index=True, comment="기본 키")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="사용자 이름") #사용자 이름, 중복 불가능하고 인덱싱 합니다
    email = Column(String(120)) #이메일 주소, 길이는 120자로 제한
    is_active = Column(Boolean, default=True, comment="활성상태")
    #'created_at" 필드는 DateTime 타입으로, 레코드 생성 시각을 나타냅니다.
    # 기본값으로 현재 시각(UTC)이 사용
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성 타임스탬프")
    # grade 필드는 Float 타입으로, 사용자 등급이나 점수 등을 저장할 수 있음
    grade = Column(Float, comment="사용자 등급")
 
 #pydantic 모델을 정의함. 이 모델은 클라이언트로부터 받은 데이터의 유효성을 검사하는데 사용 
class UserCreate(BaseModel):
    username:str
    email:str

#데이터베이스 세션을 생성하고 관리하는 의존성 함수를 정의
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()

#데이터베이스 엔진을 사용하여 모델을 기반으로 테이블을 생성 / db에 테이블이 없으면 생성 / 기존에 테이블이 있다면 그냥 무시함
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root(request:Request):
    return {"message","Hello, World!"}

#사용자를 생성하는 POST API 엔드포인트를 추가 
@app.post("/users/")
def create_user(user:UserCreate, db:Session = Depends(get_db)):
    #Pydantic 모델을 이용하여 전달받은 데이터의 유효성을 검증하고, 새 User 인스턴스를 생성
    new_user = User(username=user.username, email=user.email)
    db.add(new_user) #생성된 User 인스턴스를 데이터베이스의 세션에 추가
    db.commit() # 데이터베이스에 대한 변경사항을 커밋합니다
    db.refresh(new_user) #데이터베이스로부터 새 User 인스턴스의 최신 정보를 가져옵니다
    # 새로 생성된 사용자의 정보를 반환
    return {"id":new_user.id, "username":new_user.username, "email":new_user.email}