import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy import text

# .env 파일 로드
load_dotenv()

# 환경 변수에서 데이터베이스 연결 정보 가져오기
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


# SQLAlchemy 엔진 생성
def get_db_engine():
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")


# 데이터베이스 연결용 커넥션 생성
def get_db_connection():
    engine = get_db_engine()
    return engine.connect()


# 상품 목록 가져오기
def get_items():
    engine = get_db_engine()
    query = "SELECT * FROM items"
    return pd.read_sql(query, engine)


# 관리자 페이지 수정
def admin_page():
    st.header("관리자 페이지")

    # 상품 목록 및 재고 현황
    items_df = get_items()
    st.subheader("현재 재고 현황")
    st.dataframe(items_df)

    # 재고 관리
    with st.form("inventory_form"):
        st.subheader("재고 업데이트")
        item_id = st.selectbox(
            "상품 선택",
            items_df["id"].tolist(),
            format_func=lambda x: items_df[items_df["id"] == x]["name"].iloc[0],
        )
        quantity = st.number_input("수량 (입고: 양수, 출고: 음수)", value=0)

        submitted = st.form_submit_button("재고 업데이트")
        if submitted:
            success, message = update_inventory(item_id, quantity)
            if success:
                st.success(message)
            else:
                st.error(message)

    # 주문 내역 조회
    engine = get_db_engine()
    orders_df = pd.read_sql(
        """
        SELECT o.*, i.name as item_name
        FROM order_logs o
        JOIN items i ON o.item_id = i.id
        ORDER BY created_at DESC
        """,
        engine,
    )

    st.subheader("주문 내역")
    st.dataframe(orders_df)

    # 재고 변동 내역 조회
    inventory_df = pd.read_sql(
        """
        SELECT l.*, i.name as item_name
        FROM inventory_logs l
        JOIN items i ON l.item_id = i.id
        ORDER BY created_at DESC
        """,
        engine,
    )

    st.subheader("재고 변동 내역")
    st.dataframe(inventory_df)


# record_order와 update_inventory 함수도 SQLAlchemy를 사용하도록 수정
def record_order(item_id, quantity, store, order_by):
    engine = get_db_engine()
    connection = engine.connect()
    transaction = connection.begin()

    try:
        # 재고 확인
        result = connection.execute(
            text("SELECT stock FROM items WHERE id = :id"), {"id": item_id}
        ).fetchone()

        if not result:
            return False, "상품을 찾을 수 없습니다."

        current_stock = result[0]

        if current_stock >= quantity:
            # 주문 기록
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

            # 재고 업데이트
            connection.execute(
                text("UPDATE items SET stock = stock - :quantity WHERE id = :id"),
                {"quantity": quantity, "id": item_id},
            )

            # 재고 로그 기록
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
            return False, "재고가 부족합니다."
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
        # 재고 업데이트
        connection.execute(
            text("UPDATE items SET stock = stock + :quantity WHERE id = :id"),
            {"quantity": quantity, "id": item_id},
        )

        # 재고 로그 기록
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


# 메인 페이지
def main():
    st.title("간단한 쇼핑몰")

    # 페이지 선택
    page = st.sidebar.selectbox("페이지 선택", ["구매 페이지", "관리자 페이지"])

    if page == "구매 페이지":
        shopping_page()
    else:
        admin_page()


def shopping_page():
    st.header("🛍️ Nxtcloud 쇼핑몰에 오신 것을 환영합니다")

    # 상품 목록 표시
    items_df = get_items()

    # 상품 카드 형식으로 표시
    st.subheader("✨ 우리 제품을 소개합니다")
    cols = st.columns(3)

    for idx, item in items_df.iterrows():
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div style='padding: 15px; border: 1px solid #f0f0f0; border-radius: 10px; margin: 10px; background-color: white;'>
                    <h3 style='color: #1E88E5;'>{item['name']} ✨</h3>
                    <p style='color: #666; min-height: 60px;'>{item['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 구분선 추가
    st.divider()

    # 주문 폼 (하나만 유지)
    st.subheader("🛒 주문하기")
    with st.form(key="order_form"):
        col1, col2 = st.columns(2)

        with col1:
            item_id = st.selectbox(
                "상품 선택 🏷️",
                items_df["id"].tolist(),
                format_func=lambda x: items_df[items_df["id"] == x]["name"].iloc[0],
            )

            store = st.selectbox(
                "매장 선택 🏪", ["넥클상점1", "넥클상점2", "넥클상점3"]
            )

        with col2:
            quantity = st.number_input("수량 📦", min_value=1, value=1)
            order_by = st.text_input("주문자명 👤")

        submitted = st.form_submit_button("✨ 주문하기")

        if submitted:
            if not order_by:
                st.error("주문자 이름을 입력해주세요!")
                return

            success, message = record_order(item_id, quantity, store, order_by)
            if success:
                st.balloons()  # 주문 성공시 풍선 효과
                st.success(message)
            else:
                st.error(message)

    # 추가 정보 표시
    with st.expander("💡 쇼핑 가이드"):
        st.markdown(
            """
            **주문 방법:**
            1. 원하시는 상품을 선택해주세요
            2. 구매하실 수량을 입력해주세요
            3. 가까운 매장을 선택해주세요
            4. 주문자 이름을 입력해주세요
            5. '주문하기' 버튼을 클릭해주세요

            문의사항이 있으신가요? 
            고객센터: 1588-1588
            이메일: help@nxtcloud.com
            """
        )

    # 추가 마케팅 문구
    st.markdown(
        """
        <div style='text-align: center; padding: 20px; color: #666;'>
        🌟 지금 주문하시면 무료 배송! 🌟
        </div>
        """,
        unsafe_allow_html=True,
    )


# 관리자 페이지
def admin_page():
    st.header("관리자 페이지")

    # 상품 목록 및 재고 현황
    items_df = get_items()
    st.subheader("현재 재고 현황")
    st.dataframe(items_df)

    # 재고 관리
    with st.form("inventory_form"):
        st.subheader("재고 업데이트")
        item_id = st.selectbox(
            "상품 선택",
            items_df["id"].tolist(),
            format_func=lambda x: items_df[items_df["id"] == x]["name"].iloc[0],
        )
        quantity = st.number_input("수량 (입고: 양수, 출고: 음수)", value=0)

        submitted = st.form_submit_button("재고 업데이트")
        if submitted:
            success, message = update_inventory(item_id, quantity)
            if success:
                st.success(message)
            else:
                st.error(message)

    # 주문 내역 조회
    conn = get_db_connection()
    orders_df = pd.read_sql(
        """
        SELECT o.*, i.name as item_name
        FROM order_logs o
        JOIN items i ON o.item_id = i.id
        ORDER BY created_at DESC
    """,
        conn,
    )

    st.subheader("주문 내역")
    st.dataframe(orders_df)

    # 재고 변동 내역 조회
    inventory_df = pd.read_sql(
        """
        SELECT l.*, i.name as item_name
        FROM inventory_logs l
        JOIN items i ON l.item_id = i.id
        ORDER BY created_at DESC
    """,
        conn,
    )

    st.subheader("재고 변동 내역")
    st.dataframe(inventory_df)

    conn.close()


if __name__ == "__main__":
    main()
