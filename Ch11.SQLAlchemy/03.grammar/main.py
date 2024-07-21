from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# FastAPI 애플리케이션 인스턴스를 생성하여 앱을 초기화합니다.
app = FastAPI()

# 데이터베이스 연결 설정으로,
# 실제 애플리케이션에서는 이 부분을 사용자의 데이터베이스 정보로 교체해야 합니다.
DATABASE_URL = "mysql+pymysql://funcoding:funcoding@localhost/db_name"
engine = create_engine(DATABASE_URL)  # SQLAlchemy 엔진 인스턴스를 생성합니다.

# SessionLocal 인스턴스를 생성하기 위한 factory를 정의합니다.
# autocommit과 autoflush를 False로 설정하여, 
# 데이터베이스 세션 관리를 더욱 세밀하게 제어할 수 있습니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy의 Base 클래스를 상속받아 모델의 기본 클래스를 생성합니다.
Base = declarative_base()

# User 모델을 정의합니다. 이 클래스는 데이터베이스의 'users' 테이블에 매핑됩니다.
class User(Base):
    __tablename__ = 'users'  # 데이터베이스의 테이블 이름을 지정합니다.
    id = Column(Integer, primary_key=True, index=True)  # 사용자의 ID로, 기본 키로 설정됩니다.
    username = Column(String(50), unique=True, index=True)  # 사용자명은 최대 50자로, 고유해야 합니다.
    email = Column(String(120))  # 사용자의 이메일 주소로, 최대 120자까지 허용됩니다.

# Pydantic 모델을 정의합니다. 이 모델은 클라이언트로부터 받은 데이터의 유효성을 검사하는 데 사용됩니다.
class UserCreate(BaseModel):
    username: str
    email: str
    
# SQLAlchemy를 사용하여 데이터베이스에 테이블을 생성합니다. 
# 만약 테이블이 이미 존재한다면, 아무런 작업도 수행하지 않습니다.
Base.metadata.create_all(bind=engine)

# '/users/' 경로에 POST 요청을 받는 엔드포인트를 생성합니다.
# 이 함수는 새로운 사용자를 생성하고 데이터베이스에 저장하는 역할을 합니다.
@app.post("/users/")
def create_user(user: UserCreate):
    # SessionLocal()을 호출하여 데이터베이스 세션을 생성합니다.
    db = SessionLocal()
    # User 인스턴스를 생성하고 초기화합니다.
    db_user = User(username=user.username, email=user.email)
    # 세션에 User 인스턴스를 추가합니다.
    db.add(db_user)
    # 변경 사항을 데이터베이스에 커밋합니다.
    db.commit()
    # 커밋된 User 인스턴스의 최신 정보를 데이터베이스로부터 불러옵니다.
    db.refresh(db_user)
    # 데이터베이스 작업이 끝났으므로 세션을 닫습니다.
    db.close()
    # 생성된 사용자의 정보를 JSON 형식으로 반환합니다.
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}
  
# 이 파일을 main.py로 저장하고, FastAPI 애플리케이션을 실행합니다.
# 터미널에서 'uvicorn main:app --reload' 명령을 사용하여 서버를 시작할 수 있습니다.