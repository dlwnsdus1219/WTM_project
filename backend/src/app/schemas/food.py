# backend/src/app/schemas/food.py

from typing import Optional
from pydantic import BaseModel, ConfigDict # Pydantic v2에서는 ConfigDict 사용

# --- 기본 Food 스키마 ---
# 데이터베이스 모델의 공통 필드를 정의합니다.
class FoodBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    allergens: Optional[str] = None
    translated_name: Optional[str] = None
    translated_description: Optional[str] = None

# --- Food 생성 스키마 ---
# API를 통해 Food를 생성할 때 필요한 데이터를 정의합니다.
# menu_id는 API 경로에서 받거나 다른 방식으로 처리될 수 있으므로,
# 여기서는 필수 필드로 포함하지 않을 수 있습니다. (API 구현에 따라 다름)
# 하지만 여기서는 명확성을 위해 포함합니다.
class FoodCreate(FoodBase):
    menu_id: int # 어떤 메뉴에 속하는지 명시

# --- Food 업데이트 스키마 ---
# Food 정보를 업데이트할 때 사용될 스키마. 모든 필드는 선택 사항입니다.
class FoodUpdate(FoodBase):
    name: Optional[str] = None # 업데이트 시 이름은 필수가 아닐 수 있음
    # menu_id는 일반적으로 업데이트하지 않으므로 제외하거나 Optional로 처리
    menu_id: Optional[int] = None

# --- API 응답용 Food 스키마 ---
# 데이터베이스에서 읽어온 데이터를 API 응답으로 변환할 때 사용됩니다.
# id 필드와 menu_id 필드를 포함합니다.
class Food(FoodBase):
    id: int
    menu_id: int

    # Pydantic V2 설정: SQLAlchemy 모델 객체로부터 스키마 인스턴스를 생성할 수 있도록 함
    model_config = ConfigDict(from_attributes=True)

    # Pydantic V1 설정 (참고용):
    # class Config:
    #     orm_mode = True
