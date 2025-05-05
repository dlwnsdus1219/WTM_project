# backend/src/app/core/ocr.py

# 실제 OCR 라이브러리 임포트는 주석 처리하거나 제거합니다.
# import pytesseract
# from PIL import Image
# import io
from typing import IO # 타입 힌트는 유지합니다.

# --- Tesseract 설정 부분은 제거합니다. ---

async def extract_text_from_image(image_file: IO[bytes]) -> str:
    """
    (Placeholder) 주어진 이미지 파일에서 텍스트를 추출하는 것처럼 동작합니다.
    실제 OCR 모듈이 구현되면 이 함수 내부를 교체해야 합니다.

    Args:
        image_file (IO[bytes]): 이미지 파일의 바이트 스트림.
                                현재 구현에서는 사용되지 않습니다.

    Returns:
        str: 미리 정의된 샘플 OCR 결과 텍스트.
    """
    print("--- OCR Placeholder ---")
    print("주의: 실제 OCR 처리가 아닌 샘플 텍스트를 반환합니다.")
    print("입력 이미지 데이터는 현재 사용되지 않습니다.")
    print("-----------------------")

    # TODO: 실제 OCR 모듈 구현 후 아래 샘플 텍스트 대신
    #       해당 모듈을 호출하여 결과를 반환하도록 수정해야 합니다.
    # 예시:
    # real_ocr_module = OcrModule() # 실제 OCR 모듈 인스턴스화
    # extracted_text = await real_ocr_module.process(image_file)
    # return extracted_text

    # 임시로 반환할 샘플 텍스트
    sample_text = """
    메뉴 항목 1: 맛있는 파스타 - 12,000원
    Menu Item 2: Special Pizza - $15.00
    음료 3: 콜라 - 2,000원
    """

    # 실제 OCR 모듈이 준비될 때까지 이 샘플 텍스트를 반환합니다.
    return sample_text.strip()

# --- 테스트용 예시 (선택 사항) ---
# if __name__ == "__main__":
#     import asyncio
#     # 테스트용 가짜 이미지 데이터 (실제 파일 필요 없음)
#     class FakeImageData:
#         def read(self):
#             return b"fake image data"
#
#     async def run_test():
#         fake_file = FakeImageData()
#         # Placeholder 함수는 실제 파일 내용과 무관하게 작동
#         text = await extract_text_from_image(fake_file) # type: ignore
#         print("--- 샘플 OCR 결과 ---")
#         print(text)
#         print("--------------------")
#
#     asyncio.run(run_test())
