import pymysql
import random
from datetime import datetime, timedelta
import boto3

# RDS 연결 정보
rds_host = "database endpoint"
db_username = "username"
db_password = "password"


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

            # 샘플 데이터 생성
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

            # Order logs 데이터
            stores = ["A's Store", "B's Store", "C's Store", "D's Store"]
            users = [f"user{i}" for i in range(1, 6)]

            order_logs_data = []
            start_date = datetime(2024, 11, 1)

            for i in range(20):
                order_date = start_date + timedelta(days=random.randint(0, 30))
                order_logs_data.append(
                    (
                        order_date,
                        random.choice(users),
                        random.randint(1, 5),  # item_id
                        random.randint(1, 5),  # quantity
                        random.choice(stores),
                    )
                )

            cursor.executemany(
                "INSERT INTO order_logs (created_at, order_by, item_id, quantity, store) VALUES (%s, %s, %s, %s, %s)",
                order_logs_data,
            )

            # Inventory logs 데이터
            inventory_logs_data = []

            for i in range(15):
                inventory_date = start_date + timedelta(days=random.randint(0, 30))
                inventory_logs_data.append(
                    (
                        inventory_date,
                        random.randint(1, 5),  # item_id
                        random.randint(1, 10),  # quantity
                    )
                )

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
