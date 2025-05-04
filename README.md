# WTM_project

> 외국인 관광객이 낮선 메뉴판을 찍으면 메뉴명을 추출하고(OCR), 해당 음식의 이미지 + 영양정보 + 알레르기 성분, 다국어 번역 + 지역 특산품 여부까지 알려주는 **AI 기반의 음식 정보 통합 솔루션**


## 문제 정의
우리가 해외여행을 하는 중, 현지의 메뉴판을 이해하지 못해 식사 선택에 어려움을 겪고 있습니다. 
1️⃣ 현지 언어로만 표기된 메뉴: 음식의 


## 주요 기능 요약
\begin{table}[h!]
\centering
\begin{tabular}{|c|p{11cm}|}
\hline
\textbf{기능} & \textbf{설명} \\
\hline
📸 메뉴판 인식 (OCR) & 사용자가 메뉴판을 사진으로 찍으면, 이미지 전처리 후 텍스트를 자동 추출 (Google ML Kit, Tesseract 등 사용) \\
\hline
🔍 음식 이름 매칭 및 이미지 제공 & 추출된 음식명을 CNN 기반 모델이나 음식 DB와 매칭하여 대표 이미지 제공 (Google Custom Search 등 활용) \\
\hline
🧠 OCR 보정 및 유사 텍스트 인식 & 텍스트 유사도 기반 오류 보정 (예: cosine similarity 사용) \\
\hline
🥗 영양 정보 분석 & USDA, OpenFoodFacts 같은 공개 데이터셋을 기반으로 음식의 영양 성분 추정 (rule-based 혹은 성분 매핑) \\
\hline
🌐 다국어 번역 + 음식 설명 생성 & Google Translate / Papago로 메뉴명을 번역하고, GPT나 DB를 통해 간단한 음식 설명 생성 \\
\hline
⚠️ 알레르기 성분 안내 & 사용자 필터링 기반으로 해당 음식에 포함된 위험 성분 표시 \\
\hline
📱 통합 UI 제공 & 위 기능을 한 번에 볼 수 있는 직관적인 모바일/웹 인터페이스 제공 (사진 → 결과 화면까지 원스톱) \\
\hline
\end{tabular}
\caption{WTM의 주요 기능 요약}
\end{table}



## 기술 스택 요약


## Contributors
| Name        | Role                 | Affiliation            | GitHub ID     |
|-------------|----------------------|-------------------------|----------------|
| **이준연**    | Team Leader / AI     | IoT 인공지능 융합전공  | junylee00@naver.com   |
| **정지윤**    | Design & AI       | 빅데이터융합학과 | jyunniyss@gmail.com   |
| **신상헌**    | Front End    | 산업공학과 | sangheonsin8@gmail.com   |
| **김지인**    | Back End    | 컴퓨터정보통신공학과 | jlib245@naver.com   |
