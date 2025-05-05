# backend/src/app/crud/crud_food.py

from typing import List, Optional

from sqlalchemy.orm import Session

# 데이터베이스 모델 임포트
from app.db.models.food import Food
# 연관된 Menu 모델도 필요할 수 있습니다 (예: menu 존재 여부 확인 등)
from app.db.models.menu import Menu

# Pydantic 스키마 임포트
from app.schemas.food import FoodCreate, FoodUpdate


# --- 음식 생성 ---
def create_food_for_menu(db: Session, food: FoodCreate, menu_id: int) -> Food:
    """
    특정 메뉴에 새로운 음식 레코드를 생성합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        food (FoodCreate): 생성할 음식의 데이터 (Pydantic 스키마).
                           스키마에 menu_id가 포함되어 있더라도,
                           경로 파라미터 등에서 받은 menu_id를 사용하는 것이 명확합니다.
        menu_id (int): 음식이 속할 메뉴의 ID.

    Returns:
        Food: 생성된 Food 객체.

    Raises:
        ValueError: 해당 menu_id를 가진 메뉴가 존재하지 않을 경우.
    """
    # 메뉴 존재 여부 확인 (선택 사항이지만, 데이터 무결성을 위해 권장)
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise ValueError(f"Menu with id {menu_id} not found")

    # FoodCreate 스키마 데이터와 menu_id를 사용하여 Food 모델 인스턴스 생성
    # **food.model_dump()는 Pydantic v2 방식
    db_food = Food(**food.model_dump(), menu_id=menu_id)
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food


# --- 단일 음식 조회 ---
def get_food(db: Session, food_id: int) -> Optional[Food]:
    """
    주어진 ID를 가진 음식을 데이터베이스에서 조회합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        food_id (int): 조회할 음식의 ID.

    Returns:
        Optional[Food]: 조회된 Food 객체 또는 찾지 못한 경우 None.
    """
    return db.query(Food).filter(Food.id == food_id).first()


# --- 특정 메뉴의 음식 목록 조회 ---
def get_foods_by_menu(db: Session, menu_id: int, skip: int = 0, limit: int = 100) -> List[Food]:
    """
    특정 메뉴 ID에 속한 음식 목록을 조회합니다 (페이지네이션 지원).

    Args:
        db (Session): 데이터베이스 세션 객체.
        menu_id (int): 조회할 메뉴의 ID.
        skip (int): 건너뛸 레코드 수. 기본값 0.
        limit (int): 반환할 최대 레코드 수. 기본값 100.

    Returns:
        List[Food]: 해당 메뉴에 속한 Food 객체들의 리스트.
    """
    return db.query(Food).filter(Food.menu_id == menu_id).offset(skip).limit(limit).all()


# --- 모든 음식 조회 (선택 사항) ---
def get_all_foods(db: Session, skip: int = 0, limit: int = 100) -> List[Food]:
    """
    데이터베이스의 모든 음식 레코드를 조회합니다 (페이지네이션 지원).
    (주의: 데이터가 많을 경우 성능에 영향을 줄 수 있음)

    Args:
        db (Session): 데이터베이스 세션 객체.
        skip (int): 건너뛸 레코드 수. 기본값 0.
        limit (int): 반환할 최대 레코드 수. 기본값 100.

    Returns:
        List[Food]: 조회된 Food 객체들의 리스트.
    """
    return db.query(Food).offset(skip).limit(limit).all()


# --- 음식 업데이트 ---
def update_food(db: Session, food_id: int, food_update: FoodUpdate) -> Optional[Food]:
    """
    주어진 ID를 가진 음식을 업데이트합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        food_id (int): 업데이트할 음식의 ID.
        food_update (FoodUpdate): 업데이트할 데이터 (Pydantic 스키마).
                                   None이 아닌 필드만 업데이트합니다.

    Returns:
        Optional[Food]: 업데이트된 Food 객체 또는 음식을 찾지 못한 경우 None.
    """
    db_food = get_food(db, food_id)
    if not db_food:
        return None

    # FoodUpdate 스키마에서 제공된 데이터만 업데이트
    # model_dump(exclude_unset=True)는 Pydantic v2 방식
    update_data = food_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_food, key, value)

    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food


# --- 음식 삭제 ---
def delete_food(db: Session, food_id: int) -> Optional[Food]:
    """
    주어진 ID를 가진 음식을 데이터베이스에서 삭제합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        food_id (int): 삭제할 음식의 ID.

    Returns:
        Optional[Food]: 삭제된 Food 객체 또는 음식을 찾지 못한 경우 None.
    """
    db_food = get_food(db, food_id)
    if not db_food:
        return None

    db.delete(db_food)
    db.commit()
    return db_food # 삭제된 객체 반환
