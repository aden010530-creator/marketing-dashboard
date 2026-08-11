import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io

st.set_page_config(page_title="마케팅 캠페인 분석 대시보드", layout="wide")

st.title("📊 마케팅 캠페인 분석 대시보드")

# 사이드바 설정
st.sidebar.header("📁 데이터 관리")

# 탭으로 파일 선택 방식 나누기
upload_mode = st.sidebar.radio(
    "파일 선택 방식:",
    ["📤 파일 업로드", "📂 기본 데이터"]
)

data_files = {
    'campaign_daily.csv': 'data/campaign_daily.csv',
    'device_hour.csv': 'data/device_hour.csv',
    'diagnosis.csv': 'data/diagnosis.csv',
    'keywords.csv': 'data/keywords.csv',
    'search_terms.csv': 'data/search_terms.csv',
    'ad_groups.csv': 'data/ad_groups.csv',
}

df_dict = {}

if upload_mode == "📤 파일 업로드":
    st.sidebar.subheader("파일 업로드")
    uploaded_files = st.sidebar.file_uploader(
        "CSV 파일 선택 (복수 선택 가능):",
        type=['csv'],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                df_dict[uploaded_file.name] = df
            except Exception as e:
                st.error(f"❌ {uploaded_file.name} 로드 오류: {str(e)}")
else:
    st.sidebar.subheader("📂 기본 데이터")
    for name, path in data_files.items():
        try:
            if Path(path).exists():
                df = pd.read_csv(path, encoding='utf-8-sig')
                df_dict[name] = df
        except Exception as e:
            st.warning(f"⚠️ {name} 로드 오류")

if not df_dict:
    st.error("📁 데이터를 찾을 수 없습니다. 파일을 업로드하거나 기본 데이터를 선택하세요.")
    st.stop()

# 메인 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 대시보드", "📊 성과분석", "🔍 키워드분석", "⏰ 시간대분석", "💡 진단"])

with tab1:
    st.subheader("캠페인 주요 지표")

    if 'campaign_daily.csv' in df_dict:
        daily_df = df_dict['campaign_daily.csv']

        # 주요 KPI
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_impressions = daily_df['노출수'].sum()
            st.metric("총 노출수", f"{total_impressions:,.0f}")

        with col2:
            total_clicks = daily_df['클릭수'].sum()
            st.metric("총 클릭수", f"{total_clicks:,.0f}")

        with col3:
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            st.metric("평균 CTR", f"{avg_ctr:.2f}%")

        with col4:
            total_cost = daily_df['비용'].sum()
            st.metric("총 비용", f"₩{total_cost:,.0f}")

        with col5:
            conversions = daily_df['구독 신청'].sum()
            st.metric("총 전환", f"{conversions:.0f}")

        # 일별 트렌드
        st.subheader("일별 성과 추이")

        # 날짜 형식 변환
        daily_df['날짜'] = pd.to_datetime(daily_df['날짜'])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_df['날짜'], y=daily_df['노출수'],
            name='노출수', mode='lines+markers', yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=daily_df['날짜'], y=daily_df['클릭수'],
            name='클릭수', mode='lines+markers', yaxis='y'
        ))

        fig.update_layout(
            title="일별 노출수 및 클릭수",
            xaxis_title="날짜",
            yaxis_title="수량",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("성과 상세 분석")

    col1, col2 = st.columns(2)

    with col1:
        if 'ad_groups.csv' in df_dict:
            st.write("**광고그룹 성과**")
            st.dataframe(df_dict['ad_groups.csv'], use_container_width=True)

    with col2:
        if 'campaign_daily.csv' in df_dict:
            daily_df = df_dict['campaign_daily.csv']
            st.write("**요일별 성과**")
            weekday_data = daily_df.groupby('요일')[['노출수', '클릭수', '비용', '구독 신청']].sum()
            st.dataframe(weekday_data, use_container_width=True)

    if 'device_hour.csv' in df_dict:
        st.subheader("기기별 성과")
        device_df = df_dict['device_hour.csv']
        device_perf = device_df[device_df['구분'] == '기기']

        fig = px.bar(
            device_perf,
            x='값',
            y='클릭수',
            color='값',
            title='기기별 클릭수',
            labels={'값': '기기', '클릭수': '클릭수'}
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("키워드 성과 분석")

    if 'keywords.csv' in df_dict:
        keywords_df = df_dict['keywords.csv']

        # 성과가 좋은 키워드 TOP 10
        top_keywords = keywords_df.nlargest(10, '클릭수')[['키워드', '노출수', '클릭수', 'CTR', '비용', '구독 신청']]
        st.write("**성과 TOP 10 키워드**")
        st.dataframe(top_keywords, use_container_width=True)

        # 키워드별 ROI
        st.subheader("키워드별 효율성")
        fig = px.scatter(
            keywords_df,
            x='비용',
            y='구독 신청',
            size='클릭수',
            hover_name='키워드',
            title='키워드별 비용 대비 전환',
            labels={'비용': '비용 (₩)', '구독 신청': '구독 신청'}
        )
        st.plotly_chart(fig, use_container_width=True)

    if 'search_terms.csv' in df_dict:
        st.subheader("검색어 분석")
        search_df = df_dict['search_terms.csv']

        # 무관어 비용 분석
        irrelevant = search_df[search_df['관련도'] == '무관']
        if len(irrelevant) > 0:
            wasted_cost = irrelevant['비용'].sum()
            total_cost = search_df['비용'].sum()
            waste_ratio = (wasted_cost / total_cost * 100) if total_cost > 0 else 0

            st.metric("무관어 낭비 비용", f"₩{wasted_cost:,.0f} ({waste_ratio:.1f}%)")

            st.write("**무관어 TOP 10**")
            irrelevant_top = irrelevant.nlargest(10, '비용')[['검색어', '노출수', '클릭수', '비용']]
            st.dataframe(irrelevant_top, use_container_width=True)

with tab4:
    st.subheader("시간대별 성과 분석")

    if 'device_hour.csv' in df_dict:
        device_df = df_dict['device_hour.csv']
        hour_df = device_df[device_df['구분'] == '시간대']

        # 시간대별 추이
        fig = px.line(
            hour_df,
            x='값',
            y=['노출수', '클릭수'],
            title='시간대별 노출수 및 클릭수',
            labels={'값': '시간대', 'value': '수량', 'variable': '지표'},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # 시간대별 상세 데이터
        st.write("**시간대별 성과 데이터**")
        st.dataframe(hour_df, use_container_width=True)

with tab5:
    st.subheader("캠페인 진단 결과")

    if 'diagnosis.csv' in df_dict:
        diagnosis_df = df_dict['diagnosis.csv']

        # 진단 결과 표시
        for idx, row in diagnosis_df.iterrows():
            severity = row.get('심각도', '')
            issue = row.get('문제', '')
            description = row.get('설명', '')

            if pd.notna(issue):
                if severity == '높음':
                    st.error(f"🔴 **{issue}**\n\n{description}")
                elif severity == '보통':
                    st.warning(f"🟡 **{issue}**\n\n{description}")
                else:
                    st.info(f"🟢 **{issue}**\n\n{description}")
                st.divider()

# 데이터 다운로드
st.sidebar.divider()
st.sidebar.subheader("💾 데이터 다운로드")

for file_name, df in df_dict.items():
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label=f"📥 {file_name}",
        data=csv,
        file_name=f"exported_{file_name}",
        mime="text/csv"
    )
