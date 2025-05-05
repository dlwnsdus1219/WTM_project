# backend/src/app/api/menus.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

# 데이터베이스 세션 의존성 주입 함수 임포트
from app.db.database import get_db

# CRUD 함수 임포트
from app.crud import crud_menu, crud_food # crud_food는 메뉴에 속한 음식 조회를 위해 필요할 수 있음

# 스키마 임포트
from app.schemas.menu import Menu, MenuCreate, MenuUpdate
from app.schemas.food import Food # 메뉴 조회 시 음식 목록을 함께 반환하기 위해 필요

# 핵심 로직 임포트 (OCR 등) - 실제 구현 시 필요
# from app.core import ocr

# APIRouter 인스턴스 생성
# prefix="/menus": 이 라우터의 모든 경로는 /menus 로 시작
# tags=["menus"]: FastAPI 문서에서 API들을 'menus' 그룹으로 묶어줌
router = APIRouter(
    prefix="/menus",
    tags=["menus"],
)


# --- 메뉴 생성 엔드포인트 ---
# status_code=status.HTTP_201_CREATED: 성공 시 201 Created 상태 코드 반환
# response_model=Menu: 응답 본문의 형식을 Menu 스키마로 지정
@router.post("/", response_model=Menu, status_code=status.HTTP_201_CREATED)
async def create_new_menu(
    *, # '*' 뒤의 파라미터는 키워드 인자로만 전달 가능
    db: Session = Depends(get_db),
    # menu_in: MenuCreate, # 기본 정보만 받을 경우
    # 또는 이미지 파일을 직접 받는 경우:
    menu_image: Optional[UploadFile] = File(None, description="메뉴판 이미지 파일"),
    # 필요에 따라 추가적인 메뉴 정보를 받을 수 있음
    # ocr_text_manual: Optional[str] = None # 사용자가 직접 OCR 텍스트 입력 등
):
    """
    새로운 메뉴를 생성합니다.

    - **menu_image**: 업로드할 메뉴판 이미지 파일 (선택 사항).
    """
    # --- 실제 구현 시나리오 ---
    # 1. 이미지 파일 처리 (저장, OCR 수행 등)
    ocr_result_text = None
    image_url = None
    if menu_image:
        # 파일 저장 로직 (예: 서버 로컬, 클라우드 스토리지)
        # image_url = save_uploaded_file(menu_image) # 유틸리티 함수 필요
        image_url = f"/static/images/{menu_image.filename}" # 임시 URL 예시

        # OCR 수행 로직 (core/ocr.py 호출)
        # ocr_result_text = await ocr.process_image(menu_image.file)
        ocr_result_text = "Sample OCR text from image" # 임시 OCR 결과

    # 2. MenuCreate 스키마 객체 생성
    menu_in = MenuCreate(
        original_image_url=image_url,
        ocr_text=ocr_result_text
        # 만약 다른 필드(예: 사용자가 입력한 이름)가 MenuCreate에 있다면 추가
    )

    # 3. CRUD 함수를 사용하여 데이터베이스에 저장
    created_menu = crud_menu.create_menu(db=db, menu=menu_in)

    # 4. 생성된 메뉴 객체 반환 (자동으로 Menu 스키마 형식으로 변환됨)
    return created_menu


# --- 메뉴 목록 조회 엔드포인트 ---
# response_model=List[Menu]: 응답 본문이 Menu 스키마 객체들의 리스트임을 명시
@router.get("/", response_model=List[Menu])
def read_menus(
    db: Session = Depends(get_db),
    skip: int = 0, # 페이지네이션: 건너뛸 항목 수
    limit: int = 100 # 페이지네이션: 한 페이지당 항목 수
):
    """
    메뉴 목록을 조회합니다. 페이지네이션을 지원합니다.
    """
    menus = crud_menu.get_menus(db, skip=skip, limit=limit)
    # SQLAlchemy 모델 객체 리스트가 자동으로 Pydantic 스키마 리스트로 변환되어 반환됨
    return menus


# --- 특정 메뉴 조회 엔드포인트 ---
# response_model=Menu: 응답 본문의 형식을 Menu 스키마로 지정
@router.get("/{menu_id}", response_model=Menu)
def read_menu(
    menu_id: int, # 경로 파라미터로 메뉴 ID를 받음
    db: Session = Depends(get_db)
):
    """
    주어진 ID를 가진 특정 메뉴의 상세 정보를 조회합니다.
    해당 메뉴에 속한 음식 목록도 함께 반환됩니다.
    """
    db_menu = crud_menu.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        # 메뉴를 찾지 못한 경우 404 Not Found 에러 발생
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    # SQLAlchemy 모델 객체가 자동으로 Pydantic 스키마로 변환되어 반환됨
    # Menu 스키마에 foods: List[Food] 가 정의되어 있으므로,
    # SQLAlchemy 관계(menu.foods)를 통해 로드된 음식 목록도 함께 변환됨
    return db_menu


# --- 메뉴 수정 엔드포인트 ---
# response_model=Menu: 응답 본문의 형식을 Menu 스키마로 지정
@router.put("/{menu_id}", response_model=Menu)
def update_existing_menu(
    menu_id: int, # 경로 파라미터로 메뉴 ID를 받음
    menu_in: MenuUpdate, # 요청 본문으로 업데이트할 데이터를 받음 (MenuUpdate 스키마)
    db: Session = Depends(get_db)
):
    """
    주어진 ID를 가진 메뉴의 정보를 업데이트합니다.
    요청 본문에 포함된 필드만 업데이트됩니다.
    """
    updated_menu = crud_menu.update_menu(db=db, menu_id=menu_id, menu_update=menu_in)
    if updated_menu is None:
        # 메뉴를 찾지 못한 경우 404 Not Found 에러 발생
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return updated_menu


# --- 메뉴 삭제 엔드포인트 ---
# response_model=Menu: 응답 본문의 형식을 Menu 스키마로 지정 (삭제된 객체 정보 반환)
@router.delete("/{menu_id}", response_model=Menu)
def delete_existing_menu(
    menu_id: int, # 경로 파라미터로 메뉴 ID를 받음
    db: Session = Depends(get_db)
):
    """
    주어진 ID를 가진 메뉴를 삭제합니다.
    성공 시 삭제된 메뉴 정보를 반환합니다.
    """
    deleted_menu = crud_menu.delete_menu(db=db, menu_id=menu_id)
    if deleted_menu is None:
        # 메뉴를 찾지 못한 경우 404 Not Found 에러 발생
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    # Menu 모델에 cascade="all, delete-orphan" 설정이 되어 있다면,
    # 메뉴 삭제 시 관련된 음식(Food) 정보도 함께 삭제됩니다.
    return deleted_menu


# --- 특정 메뉴에 속한 음식 목록 조회 엔드포인트 ---
# response_model=List[Food]: 응답 본문이 Food 스키마 객체들의 리스트임을 명시
@router.get("/{menu_id}/foods/", response_model=List[Food])
def read_foods_for_menu(
    menu_id: int, # 경로 파라미터로 메뉴 ID를 받음
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    특정 메뉴에 속한 음식 목록을 조회합니다. 페이지네이션을 지원합니다.
    """
    # 먼저 해당 메뉴가 존재하는지 확인 (선택 사항이지만 권장)
    db_menu = crud_menu.get_menu(db, menu_id=menu_id)
    if db_menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    foods = crud_food.get_foods_by_menu(db, menu_id=menu_id, skip=skip, limit=limit)
    return foods
