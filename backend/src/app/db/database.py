# backend/src/app/db/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv # python-dotenv 사용 시

# .env 파일 로드 (환경 변수 관리를 위해)
# 프로젝트 루트에 .env 파일이 있다고 가정합니다.
# 예: DATABASE_URL=sqlite:///./wtm_app.db
load_dotenv()

# 데이터베이스 URL 설정
# 환경 변수에서 DATABASE_URL 값을 가져옵니다. 없으면 기본값으로 SQLite 사용
# 실제 운영 환경에서는 PostgreSQL, MySQL 등의 데이터베이스 URL을 사용합니다.
db_directory = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'db') # database.py 기준에서 경로 계산
db_file_path = os.path.join(db_directory, "wtm_app.db")
default_db_url = f"sqlite:///{db_file_path}"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", default_db_url)
# 예시: PostgreSQL
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host:port/database"
# 예시: MySQL
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@host:port/database"

# SQLAlchemy 엔진 생성
# connect_args는 SQLite 사용 시에만 필요합니다 (쓰레드 관련 설정).
# 다른 데이터베이스 사용 시에는 제거해도 됩니다.
engine_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, **engine_args
)

# 데이터베이스 세션 생성기 (SessionLocal) 설정
# autocommit=False: 변경 사항을 명시적으로 commit 해야 함
# autoflush=False: 세션 내 객체 변경 시 자동으로 flush 하지 않음 (필요시 수동 flush)
# bind=engine: 이 세션 생성기가 사용할 데이터베이스 엔진 지정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 클래스들이 상속받을 기본 클래스 (Declarative Base) 생성
# 이 Base 클래스를 상속받는 모든 클래스(Menu, Food 등)는 SQLAlchemy에 의해
# 데이터베이스 테이블과 매핑됩니다.
Base = declarative_base()

# 데이터베이스 세션을 생성하고 관리하는 함수 (의존성 주입용)
def get_db():
    """
    FastAPI 의존성 주입을 통해 데이터베이스 세션을 제공하는 함수.
    요청 처리 시작 시 세션을 생성하고, 처리가 끝나면 (성공/실패 여부 관계없이)
    세션을 닫아 리소스를 반환합니다.
    """
    db = SessionLocal()
    try:
        yield db # API 함수에 세션 객체(db)를 전달
    finally:
        db.close() # 요청 처리가 끝나면 세션 닫기

# 참고: 데이터베이스 테이블 생성
# 일반적으로 애플리케이션 시작 시점 (예: main.py) 또는
# Alembic과 같은 마이그레이션 도구를 사용하여 테이블을 생성합니다.
# 예시 (main.py 에 추가):
# from app.db import Base, engine
# Base.metadata.create_all(bind=engine)
