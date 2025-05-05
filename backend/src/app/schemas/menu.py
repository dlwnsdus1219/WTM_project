# backend/src/app/schemas/menu.py

from typing import List, Optional
from pydantic import BaseModel, ConfigDict # Pydantic v2에서는 ConfigDict 사용
from datetime import datetime

# 위에서 정의한 Food 스키마를 임포트합니다.
from .food import Food # API 응답 시 Menu에 포함될 Food 목록을 위해 필요

# --- 기본 Menu 스키마 ---
# 데이터베이스 모델의 공통 필드를 정의합니다.
class MenuBase(BaseModel):
    original_image_url: Optional[str] = None
    ocr_text: Optional[str] = None
    # translated_text: Optional[str] = None # 필요시 추가

# --- Menu 생성 스키마 ---
# API를 통해 Menu를 생성할 때 필요한 데이터를 정의합니다.
# Menu 생성 시점에는 OCR 텍스트 등이 없을 수 있으므로 Optional로 둡니다.
class MenuCreate(MenuBase):
    # Menu 생성 시 특별히 더 필요한 필드가 있다면 여기에 추가
    # 예: 사용자가 직접 입력하는 메뉴 이름 등
    # 여기서는 MenuBase와 동일하게 가정
    pass # MenuBase의 필드만 사용

# --- Menu 업데이트 스키마 ---
# Menu 정보를 업데이트할 때 사용될 스키마. 모든 필드는 선택 사항입니다.
class MenuUpdate(MenuBase):
    # 모든 필드가 Optional이므로 MenuBase를 그대로 사용해도 무방
    # 또는 명시적으로 Optional로 재정의할 수도 있습니다.
    original_image_url: Optional[str] = None
    ocr_text: Optional[str] = None
    # translated_text: Optional[str] = None

# --- API 응답용 Menu 스키마 ---
# 데이터베이스에서 읽어온 데이터를 API 응답으로 변환할 때 사용됩니다.
# id, created_at 필드와 관련된 foods 목록을 포함합니다.
class Menu(MenuBase):
    id: int
    created_at: datetime
    foods: List[Food] = [] # 해당 메뉴에 속한 음식 목록 (Food 스키마 사용)

    # Pydantic V2 설정: SQLAlchemy 모델 객체로부터 스키마 인스턴스를 생성할 수 있도록 함
    model_config = ConfigDict(from_attributes=True)

    # Pydantic V1 설정 (참고용):
    # class Config:
    #     orm_mode = True

