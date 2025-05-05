# backend/src/app/db/models/food.py

# vector dimension
EMBEDDING_DIM = 768

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey
)
from sqlalchemy.orm import relationship

# Vector 타입을 사용하기 위해 pgvector.sqlalchemy 임포트
# (pgvector 사용 시 필요, pip install pgvector-sqlalchemy)
from pgvector.sqlalchemy import Vector

# Base 클래스를 database.py 에서 가져옵니다. (..)
from ..database import Base

# Sentence Transformer 모델의 벡터 차원 (예시: 768)
# 실제 사용하는 모델의 차원과 일치시켜야 합니다.
# EMBEDDING_DIM = 768 # 실제 차원으로 변경 필요

class Food(Base):
    """
    개별 음식 정보를 저장하는 SQLAlchemy 모델
    """
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    # menus 테이블의 id 컬럼을 외래 키로 지정합니다.
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False, comment="이 음식이 속한 메뉴의 ID (외래 키)")

    name = Column(String, index=True, nullable=False, comment="음식 이름")
    description = Column(Text, nullable=True, comment="음식 설명")
    image_url = Column(String, nullable=True, comment="대표 음식 이미지 URL")

    # --- 추가된 컬럼 ---
    ingredients = Column(Text, nullable=True, comment="주요 재료 목록 (쉼표 구분 또는 JSON 문자열)") # 재료 정보 컬럼
    # embedding = Column(Vector(EMBEDDING_DIM), nullable=True, comment="음식 이름+재료 임베딩 벡터 (pgvector)") # 임베딩 벡터 컬럼
    # embedding 컬럼은 실제 사용하는 모델의 차원(EMBEDDING_DIM)을 지정해야 합니다.
    # 만약 EMBEDDING_DIM 변수를 사용하지 않으려면 직접 숫자를 넣으세요 (예: Vector(768))
    # pgvector를 사용하지 않을 경우 JSON 또는 LargeBinary 타입 고려
    embedding = Column(Vector(EMBEDDING_DIM), nullable=True, comment=f"음식 이름+재료 임베딩 벡터 (pgvector, {EMBEDDING_DIM}차원 예시)") 

    # --- 기존 컬럼 계속 ---
    # 영양 정보
    calories = Column(Float, nullable=True, comment="칼로리 (kcal)")
    protein = Column(Float, nullable=True, comment="단백질 (g)")
    carbs = Column(Float, nullable=True, comment="탄수화물 (g)")
    fat = Column(Float, nullable=True, comment="지방 (g)")
    allergens = Column(String, nullable=True, comment="알레르기 유발 물질 정보")

    # 번역 정보
    translated_name = Column(String, nullable=True, comment="번역된 음식 이름")
    translated_description = Column(Text, nullable=True, comment="번역된 음식 설명")

    # 관계 설정: Food는 하나의 Menu에 속합니다.
    # "Menu" 문자열 참조는 SQLAlchemy가 Menu 모델을 찾도록 합니다.
    menu = relationship("Menu", back_populates="foods")

    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.name}', menu_id={self.menu_id})>"
