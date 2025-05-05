# backend/src/app/db/models/food.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey # Menu 테이블의 ID를 참조하기 위해 필요합니다.
)
from sqlalchemy.orm import relationship

# Base 클래스를 database.py 에서 가져옵니다. (..)
from ..database import Base

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
