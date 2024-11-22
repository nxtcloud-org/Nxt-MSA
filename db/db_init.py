import pymysql
import random
from datetime import datetime, timedelta

# RDS 연결 정보
rds_host = "db endpoint"
db_username = "username"
db_password = "password"


def create_database_and_user(user_index):
    user_name = f"user_{user_index:03d}"
    db_name = f"db_{user_index:03d}"
    user_password = f"pw_{user_index:03d}"

    try:
        conn = pymysql.connect(host=rds_host, user=db_username, password=db_password)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
            cursor.execute(
                f"CREATE USER IF NOT EXISTS '{user_name}'@'%' IDENTIFIED BY '{user_password}';"
            )
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user_name}'@'%';")
            cursor.execute(f"USE {db_name};")

            # items 테이블 생성
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    factory VARCHAR(255) NOT NULL,
                    location VARCHAR(255) NOT NULL,
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

            # Items 데이터
            items_data = [
                ("A", "A Factory", "인천", 10),
                ("B", "B Factory", "대구", 10),
                ("C", "C Factory", "부산", 10),
                ("D", "D Factory", "서울", 15),
                ("E", "E Factory", "광주", 20),
            ]

            cursor.executemany(
                "INSERT INTO items (name, factory, location, stock) VALUES (%s, %s, %s, %s)",
                items_data,
            )

            # Inventory logs 데이터 - 다양한 시간대로 생성
            inventory_logs_data = []
            start_date = datetime(2024, 1, 1)  # 1월부터 시작

            for i in range(5):  # 더 많은 인벤토리 로그 생성
                # 랜덤한 날짜와 시간 생성
                random_days = random.randint(0, 300)  # 약 10개월 범위
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
                        random.randint(0, 10),  # quantity (음수는 출고, 양수는 입고)
                    )
                )

            # 시간순으로 정렬
            inventory_logs_data.sort(key=lambda x: x[0])

            cursor.executemany(
                "INSERT INTO inventory_logs (created_at, item_id, quantity) VALUES (%s, %s, %s)",
                inventory_logs_data,
            )

            conn.commit()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# 데이터베이스 생성 실행
number_of_users = 40
for i in range(1, number_of_users + 1):
    print(f"{i} 번째 유저의 데이터베이스 정보 생성중...\n")
    create_database_and_user(i)

print("데이터베이스 생성 완료")
