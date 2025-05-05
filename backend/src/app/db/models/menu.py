# backend/src/app/db/models/menu.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey # ForeignKey는 Food 모델에서 사용되므로 여기서는 필요 없을 수 있지만, 일반적으로 함께 임포트합니다.
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Base 클래스를 database.py 에서 가져옵니다.
# 이제 models 폴더 안에 있으므로 상위 폴더(db)의 database 모듈을 참조해야 합니다. (..)
from ..database import Base

class Menu(Base):
    """
    메뉴 정보를 저장하는 SQLAlchemy 모델
    """
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    original_image_url = Column(String, nullable=True, comment="업로드된 원본 메뉴 이미지 URL")
    ocr_text = Column(Text, nullable=True, comment="OCR로 추출된 텍스트")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성 타임스탬프")

    # 관계 설정: Menu는 여러 Food를 가질 수 있습니다.
    # "Food" 문자열 참조는 SQLAlchemy가 Food 모델을 찾도록 합니다.
    # cascade 옵션은 메뉴 삭제 시 관련 음식들도 삭제되도록 합니다.
    foods = relationship("Food", back_populates="menu", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Menu(id={self.id}, created_at={self.created_at})>"