# backend/src/app/db/models/__init__.py

# menu.py 파일에서 Menu 클래스를 임포트합니다.
from .menu import Menu
# food.py 파일에서 Food 클래스를 임포트합니다.
from .food import Food

# __all__ 리스트를 정의하면 'from .models import *' 사용 시
# 여기에 명시된 객체들만 임포트됩니다. (선택 사항이지만 좋은 습관입니다)
__all__ = ["Menu", "Food"]

# 이 파일을 통해 다른 모듈에서는 다음과 같이 모델을 임포트할 수 있습니다:
# from app.db.models import Menu, Food
