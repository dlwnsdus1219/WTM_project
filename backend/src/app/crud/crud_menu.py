# backend/src/app/crud/crud_menu.py

from typing import List, Optional

from sqlalchemy.orm import Session

# 데이터베이스 모델 임포트
# models 폴더 구조를 반영하여 임포트 경로 수정
from app.db.models.menu import Menu

# Pydantic 스키마 임포트 (아직 생성 전이지만, 필요하므로 임포트 구문 추가)
# 스키마는 API 계층과 CRUD 계층 간의 데이터 전달에 사용됩니다.
from app.schemas.menu import MenuCreate, MenuUpdate


# --- 메뉴 생성 ---
def create_menu(db: Session, menu: MenuCreate) -> Menu:
    """
    새로운 메뉴 레코드를 데이터베이스에 생성합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        menu (MenuCreate): 생성할 메뉴의 데이터 (Pydantic 스키마).

    Returns:
        Menu: 생성된 Menu 객체 (SQLAlchemy 모델 인스턴스).
    """
    # MenuCreate 스키마의 데이터를 사용하여 Menu 모델 인스턴스 생성
    # **menu.model_dump()는 Pydantic v2 방식, 이전 버전은 **menu.dict()
    db_menu = Menu(**menu.model_dump())
    db.add(db_menu) # 세션에 객체 추가
    db.commit() # 변경 사항을 데이터베이스에 커밋
    db.refresh(db_menu) # 생성된 객체의 최신 상태 (예: 자동 생성된 ID) 로드
    return db_menu


# --- 단일 메뉴 조회 ---
def get_menu(db: Session, menu_id: int) -> Optional[Menu]:
    """
    주어진 ID를 가진 메뉴를 데이터베이스에서 조회합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        menu_id (int): 조회할 메뉴의 ID.

    Returns:
        Optional[Menu]: 조회된 Menu 객체 또는 찾지 못한 경우 None.
    """
    # 기본 키(id)를 기준으로 첫 번째 일치하는 레코드를 조회
    return db.query(Menu).filter(Menu.id == menu_id).first()


# --- 여러 메뉴 조회 (페이지네이션 포함) ---
def get_menus(db: Session, skip: int = 0, limit: int = 100) -> List[Menu]:
    """
    데이터베이스에서 여러 메뉴 레코드를 조회합니다 (페이지네이션 지원).

    Args:
        db (Session): 데이터베이스 세션 객체.
        skip (int): 건너뛸 레코드 수 (페이지네이션 시작점). 기본값 0.
        limit (int): 반환할 최대 레코드 수 (페이지 크기). 기본값 100.

    Returns:
        List[Menu]: 조회된 Menu 객체들의 리스트.
    """
    # skip 만큼 건너뛰고 limit 만큼 조회하여 리스트로 반환
    return db.query(Menu).offset(skip).limit(limit).all()


# --- 메뉴 업데이트 ---
def update_menu(db: Session, menu_id: int, menu_update: MenuUpdate) -> Optional[Menu]:
    """
    주어진 ID를 가진 메뉴를 업데이트합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        menu_id (int): 업데이트할 메뉴의 ID.
        menu_update (MenuUpdate): 업데이트할 데이터 (Pydantic 스키마).
                                   None이 아닌 필드만 업데이트합니다.

    Returns:
        Optional[Menu]: 업데이트된 Menu 객체 또는 메뉴를 찾지 못한 경우 None.
    """
    db_menu = get_menu(db, menu_id) # 먼저 해당 메뉴를 조회
    if not db_menu:
        return None # 메뉴가 없으면 None 반환

    # MenuUpdate 스키마에서 제공된 데이터만 업데이트
    # model_dump(exclude_unset=True)는 Pydantic v2 방식
    # 이전 버전은 dict(exclude_unset=True)
    update_data = menu_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # db_menu 객체의 속성(key) 값을 value로 설정
        setattr(db_menu, key, value)

    db.add(db_menu) # 변경된 객체를 세션에 추가 (이미 존재하므로 update)
    db.commit() # 변경 사항 커밋
    db.refresh(db_menu) # 업데이트된 상태 로드
    return db_menu


# --- 메뉴 삭제 ---
def delete_menu(db: Session, menu_id: int) -> Optional[Menu]:
    """
    주어진 ID를 가진 메뉴를 데이터베이스에서 삭제합니다.

    Args:
        db (Session): 데이터베이스 세션 객체.
        menu_id (int): 삭제할 메뉴의 ID.

    Returns:
        Optional[Menu]: 삭제된 Menu 객체 또는 메뉴를 찾지 못한 경우 None.
    """
    db_menu = get_menu(db, menu_id) # 삭제할 메뉴 조회
    if not db_menu:
        return None # 메뉴가 없으면 None 반환

    db.delete(db_menu) # 세션에서 객체 삭제 요청
    db.commit() # 변경 사항 커밋
    # 삭제된 객체는 더 이상 접근할 수 없으므로, 삭제된 객체 자체를 반환
    return db_menu

