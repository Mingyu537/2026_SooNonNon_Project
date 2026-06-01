# 2026 SOONONNON Streamlit Project

Apps Script로 만든 `플레이리스트로 순열 살펴보기` 활동을 Streamlit으로 옮긴 버전입니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

학생 화면은 기본 화면에서 시작합니다. 교사용 대시보드는 앱 안의 버튼 또는 `?page=teacher`로 접근합니다.

교사용 비밀번호는 Streamlit secrets 또는 환경 변수로 설정하세요. 설정하지 않으면 안전한 placeholder인 `change-me`가 사용됩니다.

```toml
# .streamlit/secrets.toml
TEACHER_PASSWORD = "새비밀번호"
```

## 구현된 기능

- 학생 기본 정보 입력 및 이름/반/조 기준 이전 세션 복원
- 6단계 학생 활동 흐름
- 순열 개념 확인, 7곡 입력, 조건별 경우의 수 작성, 질문 표시
- 2가지 이상 조건을 결합한 문제 만들기
- 같은 반 다른 조 문제 확인
- 발표 정리, 학습 정리, 자기 점검, 최종 제출
- 교사용 통계, 필터, 상세 조회, CSV 다운로드, 세션 삭제
- Apps Script의 `upsertSession`, `getSubmissions`, `deleteSession`, `getSavedSessionByIdentity`에 대응하는 SQLite 저장소
- 원본 학생 화면이 호출했지만 `Code.gs`에는 없던 `getProblemBoard` 동작을 Streamlit에서 구현

## 데이터 저장

기본 저장소는 `data/submissions.db` SQLite 파일입니다. Streamlit Cloud처럼 파일 시스템이 재시작될 수 있는 환경에서는 영구 저장소를 별도로 연결해야 합니다.
