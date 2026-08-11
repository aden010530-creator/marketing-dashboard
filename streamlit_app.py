import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="마케팅 대시보드", layout="wide")

st.title("📊 마케팅 데이터 분석 대시보드")

# 사이드바 설정
st.sidebar.header("📁 데이터 관리")
data_dir = st.sidebar.text_input("데이터 폴더 경로:", value="./")

# 데이터 파일 목록
data_path = Path(data_dir)
csv_files = sorted(list(data_path.glob("*.csv")))
excel_files = sorted(list(data_path.glob("*.xlsx")))
all_files = csv_files + excel_files

st.sidebar.subheader("📄 사용 가능한 파일")

if not all_files:
    st.sidebar.warning("데이터 파일을 찾을 수 없습니다.")
    st.info("👈 올바른 폴더 경로를 입력하세요.")
    st.stop()

selected_file = st.sidebar.selectbox(
    "분석할 파일 선택:",
    [f.name for f in all_files]
)

# 선택된 파일 로드
df = None
if selected_file:
    filepath = data_path / selected_file
    try:
        if selected_file.endswith('.csv'):
            df = pd.read_csv(filepath, encoding='utf-8-sig')
        else:
            df = pd.read_excel(filepath)
    except Exception as e:
        st.error(f"❌ 파일 로드 오류: {str(e)}")

if df is not None:
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📈 개요", "📊 분석", "🔍 상세", "💾 다운로드"])

    with tab1:
        st.subheader(f"📄 {selected_file} 개요")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("행 수", len(df))
        with col2:
            st.metric("열 수", len(df.columns))
        with col3:
            st.metric("NULL 값", df.isnull().sum().sum())
        with col4:
            st.metric("중복 행", df.duplicated().sum())

        st.subheader("📋 처음 5개 행")
        st.dataframe(df.head(), use_container_width=True)

        st.subheader("📊 데이터 타입")
        dtype_df = pd.DataFrame({
            "컬럼": df.columns,
            "타입": [str(t) for t in df.dtypes.values]
        })
        st.dataframe(dtype_df, use_container_width=True)

    with tab2:
        st.subheader("📊 통계 분석")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if numeric_cols:
            st.write("**수치형 데이터 요약:**")
            st.dataframe(df[numeric_cols].describe().round(2), use_container_width=True)

            st.subheader("차트")
            selected_col = st.selectbox("시각화할 컬럼:", numeric_cols)
            if selected_col:
                fig = px.histogram(
                    df,
                    x=selected_col,
                    nbins=30,
                    title=f"{selected_col} 분포"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("수치형 데이터가 없습니다.")

    with tab3:
        st.subheader("🔍 상세 데이터 탐색")

        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("검색어 입력:")
        with col2:
            rows_to_show = st.number_input("표시 행 수:", min_value=5, max_value=100, value=10)

        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            st.dataframe(df[mask].head(rows_to_show), use_container_width=True)
        else:
            st.dataframe(df.head(rows_to_show), use_container_width=True)

    with tab4:
        st.subheader("💾 데이터 내보내기")

        col1, col2 = st.columns(2)

        with col1:
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"exported_{selected_file.replace('.xlsx', '.csv')}",
                mime="text/csv"
            )

        with col2:
            excel_file = "temp_export.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')

            with open(excel_file, "rb") as f:
                st.download_button(
                    label="📥 Excel 다운로드",
                    data=f.read(),
                    file_name=f"exported_{selected_file.replace('.csv', '.xlsx')}",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
else:
    st.warning("⚠️ 파일을 로드할 수 없습니다.")
