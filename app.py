import streamlit as st
from database import (
    get_items,
    record_order,
    update_inventory,
    get_orders,
    get_inventory_logs,
)

st.set_page_config(
    page_title="Nxtcloud 쇼핑몰", layout="wide", initial_sidebar_state="collapsed"
)


def main():
    st.title("Nxtcloud 쇼핑몰")

    page = st.sidebar.selectbox("페이지 선택", ["구매 페이지", "관리자 페이지"])

    if page == "구매 페이지":
        shopping_page()
    else:
        admin_page()


def shopping_page():
    st.header("🛍️ Nxtcloud 쇼핑몰에 오신 것을 환영합니다")

    items_df = get_items()

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

    st.divider()

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
                st.balloons()
                st.success(message)
            else:
                st.error(message)

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

    st.markdown(
        """
        <div style='text-align: center; padding: 20px; color: #666;'>
        🌟 지금 주문하시면 무료 배송! 🌟
        </div>
        """,
        unsafe_allow_html=True,
    )


def admin_page():
    st.header("관리자 페이지")

    items_df = get_items()
    st.subheader("현재 재고 현황")
    st.dataframe(items_df)

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

    st.subheader("주문 내역")
    st.dataframe(get_orders())

    st.subheader("재고 변동 내역")
    st.dataframe(get_inventory_logs())


if __name__ == "__main__":
    main()
