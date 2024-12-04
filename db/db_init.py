import pymysql
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
rds_host = os.getenv("DB_HOST")
db_username = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")


def create_database_and_user(user_index):
    user_name = f"user_{user_index:03d}"
    db_name = f"db_{user_index:03d}"
    user_password = f"pw_{user_index:03d}"

    try:
        conn = pymysql.connect(host=rds_host, user=db_username, password=db_password)
        with conn.cursor() as cursor:
            # 데이터베이스 생성
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")

            # 사용자 생성 및 권한 부여
            cursor.execute(
                f"CREATE USER IF NOT EXISTS '{user_name}'@'%' IDENTIFIED BY '{user_password}';"
            )
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user_name}'@'%';")

            # 데이터베이스 선택
            cursor.execute(f"USE {db_name};")

            # items 테이블 생성 - description 필드 추가
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    factory VARCHAR(255) NOT NULL,
                    stock INT NOT NULL
                );
            """
            )

            # order_logs 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS order_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at DATETIME NOT NULL,
                    order_by VARCHAR(255) NOT NULL,
                    item_id INT NOT NULL,
                    quantity INT NOT NULL,
                    store VARCHAR(255) NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items(id)
                );
            """
            )

            # inventory_logs 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS inventory_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    created_at DATETIME NOT NULL,
                    item_id INT NOT NULL,
                    quantity INT NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items(id)
                );
            """
            )

            # 새로운 상품 데이터
            items_data = [
                (
                    "클라우드 머그컵",
                    "구름 모양 손잡이가 특징인 350ml 도자기 머그컵",
                    "서울공장",
                    10,
                ),
                (
                    "넥스트 보틀",
                    "무선 온도 표시 기능이 있는 스마트 보온병",
                    "인천공장",
                    15,
                ),
                ("데브옵스 키보드", "개발자를 위한 기계식 RGB 키보드", "수원공장", 8),
                (
                    "클라우드 무드등",
                    "구름 모양의 수면등, 색상 변경 가능",
                    "부산공장",
                    20,
                ),
                ("코딩 후드티", "프로그래머를 위한 편안한 후드 티셔츠", "대구공장", 25),
            ]

            cursor.executemany(
                "INSERT INTO items (name, description, factory, stock) VALUES (%s, %s, %s, %s)",
                items_data,
            )

            # Inventory logs 데이터 - 다양한 시간대로 생성
            inventory_logs_data = []
            start_date = datetime(2024, 1, 1)

            for i in range(100):
                random_days = random.randint(0, 300)
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                random_seconds = random.randint(0, 59)

                inventory_date = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes,
                    seconds=random_seconds,
                )

                inventory_logs_data.append(
                    (
                        inventory_date,
                        random.randint(1, 5),  # item_id
                        random.randint(-10, 10),  # quantity
                    )
                )

            # 시간순 정렬
            inventory_logs_data.sort(key=lambda x: x[0])

            cursor.executemany(
                "INSERT INTO inventory_logs (created_at, item_id, quantity) VALUES (%s, %s, %s)",
                inventory_logs_data,
            )

            conn.commit()
            print(f"데이터베이스 {db_name} 생성 완료")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # 데이터베이스 생성 실행
    number_of_users = 20  # 20개의 데이터베이스만 생성
    for i in range(1, number_of_users + 1):
        print(f"{i} 번째 유저의 데이터베이스 정보 생성중...\n")
        create_database_and_user(i)

    print("모든 데이터베이스 생성 완료")
