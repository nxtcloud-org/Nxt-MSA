
# Nxtcloud Shopping Mall

간단한 재고 관리 시스템이 포함된 쇼핑몰 웹 애플리케이션입니다.

## 주요 기능

### 구매 페이지 🛍️

- 상품 목록 카드 형식 표시
- 상품 주문 기능
  - 상품 선택
  - 수량 지정
  - 매장 선택
  - 주문자 정보 입력
- 주문 처리 및 재고 자동 업데이트
- 쇼핑 가이드 제공

### 관리자 페이지 👨‍💼

- 실시간 재고 현황 모니터링
- 재고 관리 기능
  - 입/출고 수량 조정
  - 재고 업데이트
- 주문 내역 조회
- 재고 변동 이력 조회

## 기술 스택

- Frontend: Streamlit
- Backend: Python
- Database: MySQL (AWS RDS)
- ORM: SQLAlchemy

## 프로젝트 구조

```
├── README.md
├── requirements.txt
├── .env
├── app.py                  # 메인 애플리케이션 코드
├── database.py             # 데이터베이스 관련 코드
└── db/
    ├── db_init.py         # 데이터베이스 초기화 스크립트
    └── reset_database.py  # 데이터베이스 리셋 스크립트
```

## 설치 및 실행 방법

1. 저장소 복제

```bash
git clone [repository-url]
cd [project-directory]
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정

- 프로젝트 루트에 `.env` 파일 생성:

```env
DB_HOST=your-rds-endpoint
DB_USER=admin
DB_PASSWORD=your-password
DB_NAME=db_001
```

5. 데이터베이스 초기화

```bash
python db/reset_database.py  # 기존 데이터베이스 초기화 (필요한 경우)
python db/db_init.py        # 새 데이터베이스 생성 및 초기 데이터 설정
```

6. 애플리케이션 실행

```bash
streamlit run app.py
```

## 데이터베이스 구조

### items 테이블

- id: 상품 ID
- name: 상품명
- description: 상품 설명
- factory: 제조 공장
- stock: 재고 수량

### order_logs 테이블

- id: 주문 ID
- created_at: 주문 시각
- order_by: 주문자
- item_id: 상품 ID
- quantity: 주문 수량
- store: 주문 매장

### inventory_logs 테이블

- id: 로그 ID
- created_at: 기록 시각
- item_id: 상품 ID
- quantity: 수량 변동

## 주의사항

- 데이터베이스 초기화 시 기존 데이터가 모두 삭제됩니다.
- AWS RDS 접속 정보는 보안을 위해 반드시 .env 파일에 저장하여 관리하세요.
- .env 파일은 절대 깃허브에 커밋하지 마세요.

## 개발자 참고사항

- 코드 수정 시 database.py의 SQL 쿼리와 app.py의 UI 로직을 분리하여 관리하세요.
- 새로운 기능 추가 시 기존 데이터베이스 구조를 고려하여 설계하세요.
- Streamlit의 session_state를 활용하여 상태 관리를 할 수 있습니다.
