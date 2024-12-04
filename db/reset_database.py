import pymysql
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def reset_databases():
    try:
        # MySQL 연결
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)

        with conn.cursor() as cursor:
            # 1부터 20까지의 데이터베이스 삭제
            for i in range(1, 21):
                db_name = f"db_{i:03d}"
                user_name = f"user_{i:03d}"

                try:
                    # 데이터베이스 삭제
                    cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
                    print(f"데이터베이스 {db_name} 삭제 완료")

                    # 사용자 삭제
                    cursor.execute(f"DROP USER IF EXISTS '{user_name}'@'%';")
                    print(f"사용자 {user_name} 삭제 완료")

                except Exception as e:
                    print(f"Error deleting {db_name}: {e}")

            conn.commit()
            print("\n모든 데이터베이스와 사용자 삭제 완료")

    except Exception as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    print("데이터베이스 초기화를 시작합니다...\n")
    reset_databases()
