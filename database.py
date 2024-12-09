import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def get_db_engine():
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")


def get_db_connection():
    engine = get_db_engine()
    return engine.connect()


def get_items():
    engine = get_db_engine()
    query = "SELECT * FROM items"
    return pd.read_sql(query, engine)


def record_order(item_id, quantity, store, order_by):
    engine = get_db_engine()
    connection = engine.connect()
    transaction = connection.begin()

    try:
        result = connection.execute(
            text("SELECT stock FROM items WHERE id = :id"), {"id": item_id}
        ).fetchone()

        if not result:
            return False, "상품을 찾을 수 없습니다."

        current_stock = result[0]

        if current_stock >= quantity:
            connection.execute(
                text(
                    """
                INSERT INTO order_logs (created_at, order_by, item_id, quantity, store)
                VALUES (NOW(), :order_by, :item_id, :quantity, :store)
                """
                ),
                {
                    "order_by": order_by,
                    "item_id": item_id,
                    "quantity": quantity,
                    "store": store,
                },
            )

            connection.execute(
                text("UPDATE items SET stock = stock - :quantity WHERE id = :id"),
                {"quantity": quantity, "id": item_id},
            )

            connection.execute(
                text(
                    """
                INSERT INTO inventory_logs (created_at, item_id, quantity)
                VALUES (NOW(), :item_id, :quantity)
                """
                ),
                {"item_id": item_id, "quantity": -quantity},
            )

            transaction.commit()
            return True, "주문이 성공적으로 처리되었습니다."
        else:
            return False, "재고가 부족합니다. 나중에 다시 시도해주세요."
    except Exception as e:
        transaction.rollback()
        return False, f"오류가 발생했습니다: {str(e)}"
    finally:
        connection.close()


def update_inventory(item_id, quantity):
    engine = get_db_engine()
    connection = engine.connect()
    transaction = connection.begin()

    try:
        connection.execute(
            text("UPDATE items SET stock = stock + :quantity WHERE id = :id"),
            {"quantity": quantity, "id": item_id},
        )

        connection.execute(
            text(
                """
            INSERT INTO inventory_logs (created_at, item_id, quantity)
            VALUES (NOW(), :item_id, :quantity)
            """
            ),
            {"item_id": item_id, "quantity": quantity},
        )

        transaction.commit()
        return True, "재고가 성공적으로 업데이트되었습니다."
    except Exception as e:
        transaction.rollback()
        return False, f"오류가 발생했습니다: {str(e)}"
    finally:
        connection.close()


def get_orders():
    engine = get_db_engine()
    query = """
        SELECT o.*, i.name as item_name
        FROM order_logs o
        JOIN items i ON o.item_id = i.id
        ORDER BY created_at DESC
    """
    return pd.read_sql(query, engine)


def get_inventory_logs():
    engine = get_db_engine()
    query = """
        SELECT l.*, i.name as item_name
        FROM inventory_logs l
        JOIN items i ON l.item_id = i.id
        ORDER BY created_at DESC
    """
    return pd.read_sql(query, engine)
