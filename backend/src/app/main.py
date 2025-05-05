# backend/src/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 데이터베이스 관련 임포트 (테이블 생성용)
from app.db.database import engine, Base
# 모델 임포트 (Base가 참조하는 모델들을 인식시키기 위해 필요)
# models/__init__.py 덕분에 이렇게 임포트 가능
from app.db import models

# API 라우터 임포트
from app.api import menus, foods

# --- 데이터베이스 테이블 생성 ---
# 애플리케이션 시작 시 SQLAlchemy 모델에 정의된 모든 테이블을 생성합니다.
# 주의: 프로덕션 환경에서는 Alembic과 같은 마이그레이션 도구를 사용하는 것이 좋습니다.
#       개발 초기 단계나 간단한 애플리케이션에서는 유용할 수 있습니다.
# Base.metadata.create_all(bind=engine)
# print("Database tables created (if they didn't exist).") # 생성 확인 로그

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="WTM; What The Menu? API",
    description="메뉴판 이미지 분석 및 음식 정보 제공 API",
    version="0.1.0",
    # 여기에 추가적인 FastAPI 설정을 할 수 있습니다. (예: docs_url, redoc_url)
)

# --- CORS 미들웨어 설정 ---
# 웹 브라우저에서 다른 도메인(origin)의 프론트엔드 애플리케이션(예: React Native 웹뷰, 웹 앱)이
# 이 API 서버와 통신할 수 있도록 허용합니다.

# 허용할 출처 목록 (개발 중에는 모든 출처 허용 '*' 또는 프론트엔드 주소 명시)
# 프로덕션 환경에서는 실제 프론트엔드 도메인만 명시하는 것이 안전합니다.
origins = [
    "http://localhost",         # 로컬 개발 환경
    "http://localhost:8081",    # React Native Metro Bundler 기본 포트
    "http://localhost:3000",    # React 웹 개발 서버 기본 포트
    # "https://your-frontend-domain.com", # 실제 배포된 프론트엔드 주소
    "*", # 모든 출처 허용 (가장 개방적, 개발 시 편리)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # origins 목록에 있는 출처의 요청만 허용
    allow_credentials=True, # 요청에 쿠키 포함 허용 여부
    allow_methods=["*"],    # 모든 HTTP 메소드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],    # 모든 HTTP 헤더 허용
)


# --- API 라우터 등록 ---
# /menus 경로로 들어오는 요청은 menus.router 가 처리
app.include_router(menus.router)
# /foods 경로로 들어오는 요청은 foods.router 가 처리
app.include_router(foods.router)


# --- 루트 엔드포인트 ---
# API 서버가 정상적으로 실행 중인지 확인하기 위한 간단한 엔드포인트
@app.get("/", tags=["Root"])
async def read_root():
    """
    API 서버의 루트 경로. 서버 상태 확인용 메시지를 반환합니다.
    """
    return {"message": "Welcome to WTM API!"}

# --- 애플리케이션 실행 ---
# 이 파일이 직접 실행될 때 (예: python src/app/main.py) Uvicorn 서버를 실행하는 코드 (선택 사항)
# 일반적으로는 터미널에서 'uvicorn app.main:app --reload' 명령어로 실행합니다.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

