# backend/src/app/api/foods.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# 데이터베이스 세션 의존성 주입 함수 임포트
from app.db.database import get_db

# CRUD 함수 임포트
from app.crud import crud_food, crud_menu # crud_menu는 음식 생성 시 메뉴 존재 확인 등에 사용될 수 있음

# 스키마 임포트
from app.schemas.food import Food, FoodCreate, FoodUpdate

# APIRouter 인스턴스 생성
# prefix="/foods": 이 라우터의 모든 경로는 /foods 로 시작
# tags=["foods"]: FastAPI 문서에서 API들을 'foods' 그룹으로 묶어줌
router = APIRouter(
    prefix="/foods",
    tags=["foods"],
)


# --- 음식 생성 엔드포인트 ---
# 참고: 메뉴에 종속적인 음식을 생성하는 API는 /menus/{menu_id}/foods/ 경로에
#       별도로 만드는 것이 RESTful 디자인에 더 맞을 수 있습니다.
#       여기서는 일반적인 /foods/ 경로에 생성 엔드포인트를 만듭니다.
#       이 경우 FoodCreate 스키마에 menu_id가 포함되어야 합니다.
@router.post("/", response_model=Food, status_code=status.HTTP_201_CREATED)
def create_new_food(
    food_in: FoodCreate, # 요청 본문으로 음식 생성 데이터를 받음
    db: Session = Depends(get_db)
):
    """
    새로운 음식 정보를 생성합니다.

    요청 본문에 `menu_id`가 포함되어야 합니다.
    """
    # menu_id가 유효한지 확인 (crud_food.create_food_for_menu 에서 처리하거나 여기서 확인)
    # 예시: db_menu = crud_menu.get_menu(db, menu_id=food_in.menu_id)
    #       if not db_menu:
    #           raise HTTPException(status_code=404, detail=f"Menu with id {food_in.menu_id} not found")

    # crud_food 함수를 사용하여 음식 생성
    # create_food_for_menu는 menu_id를 별도 인자로 받으므로, 해당 함수 사용 시 아래와 같이 호출
    try:
        created_food = crud_food.create_food_for_menu(db=db, food=food_in, menu_id=food_in.menu_id)
    except ValueError as e: # crud_food.create_food_for_menu 에서 메뉴를 못 찾으면 ValueError 발생
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    # 만약 menu_id 확인 로직이 crud 함수 내에 없다면,
    # FoodCreate 스키마만 사용하는 일반적인 create 함수를 crud_food에 만들고 호출할 수 있습니다.
    # 예: created_food = crud_food.create_food(db=db, food=food_in)

    return created_food


# --- 모든 음식 목록 조회 엔드포인트 ---
# response_model=List[Food]: 응답 본문이 Food 스키마 객체들의 리스트임을 명시
@router.get("/", response_model=List[Food])
def read_all_foods(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    모든 음식 정보 목록을 조회합니다. 페이지네이션을 지원합니다.
    (주의: 데이터 양이 많을 경우 성능에 영향을 줄 수 있습니다.)
    """
    foods = crud_food.get_all_foods(db, skip=skip, limit=limit)
    return foods


# --- 특정 음식 조회 엔드포인트 ---
# response_model=Food: 응답 본문의 형식을 Food 스키마로 지정
@router.get("/{food_id}", response_model=Food)
def read_food_by_id(
    food_id: int, # 경로 파라미터로 음식 ID를 받음
    db: Session = Depends(get_db)
):
    """
    주어진 ID를 가진 특정 음식의 상세 정보를 조회합니다.
    """
    db_food = crud_food.get_food(db, food_id=food_id)
    if db_food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return db_food


# --- 음식 수정 엔드포인트 ---
# response_model=Food: 응답 본문의 형식을 Food 스키마로 지정
@router.put("/{food_id}", response_model=Food)
def update_existing_food(
    food_id: int, # 경로 파라미터로 음식 ID를 받음
    food_in: FoodUpdate, # 요청 본문으로 업데이트할 데이터를 받음 (FoodUpdate 스키마)
    db: Session = Depends(get_db)
):
    """
    주어진 ID를 가진 음식의 정보를 업데이트합니다.
    요청 본문에 포함된 필드만 업데이트됩니다.
    """
    updated_food = crud_food.update_food(db=db, food_id=food_id, food_update=food_in)
    if updated_food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return updated_food


# --- 음식 삭제 엔드포인트 ---
# response_model=Food: 응답 본문의 형식을 Food 스키마로 지정 (삭제된 객체 정보 반환)
@router.delete("/{food_id}", response_model=Food)
def delete_existing_food(
    food_id: int, # 경로 파라미터로 음식 ID를 받음
    db: Session = Depends(get_db)
):
    """
    주어진 ID를 가진 음식을 삭제합니다.
    성공 시 삭제된 음식 정보를 반환합니다.
    """
    deleted_food = crud_food.delete_food(db=db, food_id=food_id)
    if deleted_food is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")
    return deleted_food

# --- (선택 사항) 음식 번역 정보 조회 엔드포인트 ---
# 예시: 특정 음식의 번역된 이름과 설명을 조회하는 API
# @router.get("/{food_id}/translated", response_model=FoodTranslated) # FoodTranslated 스키마 필요
# def read_food_translation(
#     food_id: int,
#     db: Session = Depends(get_db)
# ):
#     db_food = crud_food.get_food(db, food_id=food_id)
#     if db_food is None:
#         raise HTTPException(status_code=404, detail="Food not found")
#     # 여기에 번역 로직 또는 번역된 필드 반환 로직 추가
#     # 예: if not db_food.translated_name: call_translation_api(...)
#     return db_food # 또는 FoodTranslated 스키마 객체 반환
