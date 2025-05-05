# backend/src/app/core/food_info.py

import re
from typing import List, Dict, Any, Optional, Tuple

# 데이터베이스 상호작용
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, text # text() 함수 사용 예시
from app.db.models.food import Food # Food 모델 임포트 (ingredients, embedding 컬럼 추가 가정)

# Sentence Transformer 라이브러리
from sentence_transformers import SentenceTransformer, util # util.cos_sim 사용 가능

# --- 설정 ---
# 사용할 Sentence Transformer 모델 이름
# 한국어 및 다국어 지원, 짧은 텍스트 처리에 적합한 모델 선택 (예시)
MODEL_NAME = "jhgan/ko-sroberta-multitask"
# 유사도 임계값 (코사인 유사도 기준, 0~1 사이 값)
SIMILARITY_THRESHOLD = 0.7 # 예시 임계값 (조정 필요)
# DB에서 벡터 검색 시 상위 몇 개를 가져올지
TOP_K_RESULTS = 3

# --- 모델 로드 ---
# 애플리케이션 시작 시 한 번만 로드하는 것이 효율적입니다.
# (실제 앱에서는 main.py나 별도 설정 파일에서 관리)
try:
    print(f"Loading Sentence Transformer model: {MODEL_NAME}...")
    embedding_model = SentenceTransformer(MODEL_NAME)
    print("Model loaded successfully.")
    # 임베딩 벡터 차원 확인 (DB 컬럼 정의 시 필요)
    EMBEDDING_DIM = embedding_model.get_sentence_embedding_dimension()
    print(f"Embedding dimension: {EMBEDDING_DIM}")
except Exception as e:
    print(f"Error loading Sentence Transformer model: {e}")
    embedding_model = None
    EMBEDDING_DIM = None # 모델 로드 실패 시 차원 알 수 없음

# --- 헬퍼 함수: 텍스트 임베딩 ---
def get_embedding(text: str) -> Optional[List[float]]:
    """주어진 텍스트의 임베딩 벡터를 계산합니다."""
    if embedding_model is None:
        print("Error: Embedding model is not loaded.")
        return None
    try:
        # 모델을 사용하여 텍스트를 벡터로 변환
        vector = embedding_model.encode(text, convert_to_tensor=False) # numpy 배열 반환
        return vector.tolist() # 리스트 형태로 반환
    except Exception as e:
        print(f"Error generating embedding for '{text}': {e}")
        return None

# --- 1단계: 텍스트에서 음식 항목 정보 파싱 ---
def parse_food_items_from_text(ocr_text: str) -> List[Dict[str, Any]]:
    """
    OCR 텍스트에서 정규 표현식 등을 사용하여 기본적인 음식 이름과 가격 텍스트를 파싱합니다.
    (이전 코드와 동일)
    """
    parsed_items = []
    lines = ocr_text.strip().split('\n')
    pattern = re.compile(r"^(.*?)\s*[:—-]\s*(.*?)\s*$", re.MULTILINE)

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        item = {}
        if match:
            item["name"] = match.group(1).strip()
            item["price_text"] = match.group(2).strip()
            # print(f"파싱 성공: 이름='{item['name']}', 가격='{item['price_text']}'") # 로그 줄임
        else:
            item["name"] = line
            item["price_text"] = None
            # print(f"패턴 매칭 실패: '{line}' -> 이름으로 간주") # 로그 줄임

        if item.get("name"):
             parsed_items.append({
                 "name": item["name"],
                 "price_text": item.get("price_text")
             })

    return parsed_items

# --- 2단계: 의미 기반 유사 메뉴 검색 (DB 벡터 검색 활용) ---
def find_similar_food_by_meaning(
    db: Session,
    parsed_name: str,
    # parsed_ingredients: Optional[List[str]] = None, # OCR에서 재료 추론 시 사용
    top_k: int = TOP_K_RESULTS,
    threshold: float = SIMILARITY_THRESHOLD
) -> List[Tuple[Food, float]]:
    """
    파싱된 음식 이름(+재료)의 의미 벡터와 가장 유사한 음식을 DB에서 검색합니다.
    (DB에 벡터 컬럼 및 인덱스가 설정되어 있다고 가정)

    Args:
        db (Session): 데이터베이스 세션.
        parsed_name (str): OCR에서 파싱된 음식 이름.
        # parsed_ingredients (Optional[List[str]]): 추론된 재료 목록 (선택 사항).
        top_k (int): 반환할 최대 유사 메뉴 수.
        threshold (float): 유사 메뉴로 간주할 최소 코사인 유사도 점수 (0~1).

    Returns:
        List[Tuple[Food, float]]: 유사한 Food 객체와 유사도 점수(코사인 유사도) 튜플 리스트.
                                  유사도가 높은 순서로 정렬됩니다.
    """
    if embedding_model is None or EMBEDDING_DIM is None:
        print("유사도 검색 불가: 임베딩 모델 로드 실패.")
        return []

    # 1. 입력 텍스트 생성 (이름 + 재료)
    # TODO: parsed_ingredients가 있다면 여기에 포함시키는 로직 추가
    # 예: input_text = f"{parsed_name}: {', '.join(parsed_ingredients)}"
    input_text = parsed_name # 현재는 이름만 사용

    # 2. 입력 텍스트의 임베딩 벡터 계산
    input_vector = get_embedding(input_text)
    if input_vector is None:
        print(f"입력 벡터 생성 실패: '{input_text}'")
        return []

    # 3. DB에서 유사 벡터 검색 (pgvector 사용 예시)
    #    - Food 모델에 'embedding' (Vector 타입) 컬럼이 있다고 가정합니다.
    #    - 코사인 유사도 = 1 - 코사인 거리
    #    - 효율적인 검색을 위해 DB에 벡터 인덱스(HNSW, IVFFlat 등) 생성이 필수적입니다.
    print(f"DB에서 '{input_text}'와(과) 유사한 벡터 검색 (유사도 > {threshold})...")
    try:
        # pgvector의 코사인 거리 연산자 '<=>' 사용
        # 유사도 = 1 - 거리 이므로, 거리 < (1 - threshold) 조건 사용
        vector_str = str(input_vector) # 벡터를 문자열로 변환하여 쿼리에 전달
        distance_limit = 1 - threshold

        # SQLAlchemy 쿼리 구성
        # 코사인 거리를 계산하고 'distance' 레이블로 가져옴
        query = db.query(
                    Food,
                    Food.embedding.cosine_distance(vector_str).label('distance')
                ).filter(
                    # 임계값보다 거리가 작은 (즉, 유사도가 높은) 항목만 필터링
                    Food.embedding.cosine_distance(vector_str) < distance_limit
                ).order_by(
                    # 거리가 가장 가까운 순서로 정렬
                    Food.embedding.cosine_distance(vector_str)
                ).limit(top_k) # 상위 K개 결과만 가져옴

        results = query.all() # 쿼리 실행

        # 결과 처리: (Food 객체, 코사인 유사도) 튜플 리스트로 변환
        similar_foods = []
        for food, distance in results:
            similarity = 1 - distance # 코사인 유사도로 변환
            similar_foods.append((food, similarity))
            print(f"  - 찾음: '{food.name}' (ID: {food.id}), 유사도: {similarity:.4f}")

        if not similar_foods:
            print("유사한 메뉴를 찾지 못했습니다.")

        return similar_foods

    except Exception as e:
        # 실제 운영 시에는 DB 관련 오류를 더 상세히 로깅/처리해야 합니다.
        print(f"DB 벡터 검색 중 오류 발생: {e}")
        print("  - DB에 'embedding' 벡터 컬럼과 pgvector 확장이 올바르게 설정되었는지 확인하세요.")
        print("  - 기존 데이터에 대한 임베딩 벡터가 미리 계산되어 저장되었는지 확인하세요.")
        return []


# --- (예시) 전체 처리 흐름 함수 ---
def process_ocr_text_and_get_food_details_nlp(db: Session, ocr_text: str) -> List[Dict[str, Any]]:
    """
    OCR 텍스트를 처리하여 각 항목에 대해 의미 기반 유사도 검사를 수행하고
    최종 정보를 구성하는 예시 함수.

    Args:
        db (Session): 데이터베이스 세션.
        ocr_text (str): OCR 결과 텍스트.

    Returns:
        List[Dict[str, Any]]: 각 음식 항목에 대한 최종 정보 딕셔너리 리스트.
                               'parsed_name', 'price_text', 'similar_foods' 키 포함.
    """
    parsed_items = parse_food_items_from_text(ocr_text)
    results = []

    for item in parsed_items:
        parsed_name = item["name"]
        price_text = item["price_text"]

        # 의미 기반 유사 메뉴 검색 함수 호출
        similar_foods_with_scores = find_similar_food_by_meaning(db, parsed_name)

        result_item = {
            "parsed_name": parsed_name,
            "price_text": price_text,
            # 유사도 높은 순으로 정렬된 (Food 객체, 유사도 점수) 튜플 리스트
            "similar_foods": similar_foods_with_scores,
            # TODO: 찾은 유사 메뉴 정보를 바탕으로 영양 정보, 이미지 등 추가 정보 구성
            # 예: best_match = similar_foods_with_scores[0][0] if similar_foods_with_scores else None
            #     "nutrition_info": best_match.calories if best_match else None
        }
        results.append(result_item)

    return results


# --- 중요: 사전 준비 사항 ---
# 1. DB 설정:
#    - Food 모델에 'ingredients' (Text), 'embedding' (Vector(EMBEDDING_DIM)) 컬럼 추가.
#    - PostgreSQL 사용 시 pgvector 확장 기능 설치 및 활성화.
#    - 'embedding' 컬럼에 효율적인 인덱스 생성 (예: USING hnsw (embedding vector_cosine_ops)).
# 2. 데이터 준비:
#    - DB의 모든 Food 데이터에 대해 'ingredients' 정보 채우기.
#    - 별도 스크립트를 사용하여 모든 Food 데이터의 "이름: 재료" 텍스트에 대한
#      임베딩 벡터를 미리 계산하고 'embedding' 컬럼에 저장. (매우 중요!)
# 3. 모델 로딩:
#    - embedding_model = SentenceTransformer(MODEL_NAME) 코드가 애플리케이션 시작 시
#      한 번만 실행되도록 구성 (예: FastAPI의 startup 이벤트 핸들러 사용).

# --- 테스트용 예시 (직접 실행 시) ---
# if __name__ == "__main__":
#     # 이 테스트 코드는 DB 설정 및 데이터 사전 준비가 완료되었다고 가정합니다.
#     from app.db.database import SessionLocal
#     db = SessionLocal()
#     try:
#         sample_ocr_text = """
#         돼지 김치찌개 : 8,000원
#         돈까스 - 9,000원
#         후라이드 치킨 : 18,000원
#         참치 찌개 : 7,500원
#         소고기 스테이크
#         """
#
#         final_results = process_ocr_text_and_get_food_details_nlp(db, sample_ocr_text)
#
#         print("\n--- 최종 처리 결과 (NLP 기반) ---")
#         for result in final_results:
#             print(f"  파싱된 이름: {result['parsed_name']}")
#             print(f"  가격 텍스트: {result['price_text']}")
#             if result['similar_foods']:
#                 print("  DB 유사 제안:")
#                 for food, score in result['similar_foods']:
#                     print(f"    - '{food.name}' (ID: {food.id}), 유사도: {score:.4f}")
#             else:
#                 print("  DB 정보 없음 / 유사 항목 없음")
#             print("-" * 10)
#         print("-----------------------------")
#
#     finally:
#         db.close()
