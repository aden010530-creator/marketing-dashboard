import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io

st.set_page_config(page_title="마케팅 캠페인 분석 대시보드", layout="wide")

st.title("📊 마케팅 캠페인 분석 대시보드")
st.markdown("CSV 파일을 업로드하면 자동으로 분석합니다 🚀")

# 파일 업로드
st.sidebar.header("📤 CSV 파일 업로드")
uploaded_files = st.sidebar.file_uploader(
    "분석할 CSV 파일을 선택하세요 (복수 선택 가능):",
    type=['csv'],
    accept_multiple_files=True
)

df_dict = {}

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            df_dict[uploaded_file.name.replace('.csv', '')] = df
        except Exception as e:
            st.error(f"❌ {uploaded_file.name} 로드 오류: {str(e)}")
else:
    st.info("👈 사이드바에서 CSV 파일을 업로드하세요")
    st.stop()

if not df_dict:
    st.error("데이터를 찾을 수 없습니다.")
    st.stop()

# 파일 목록 표시
st.sidebar.divider()
st.sidebar.subheader(f"✅ 로드된 파일 ({len(df_dict)}개)")
for name in df_dict.keys():
    st.sidebar.text(f"• {name}")

# 메인 콘텐츠
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 대시보드", "📊 성과분석", "🔍 키워드분석", "⏰ 시간대분석", "💡 진단"])

with tab1:
    st.subheader("캠페인 주요 지표")

    if 'campaign_daily' in df_dict:
        daily_df = df_dict['campaign_daily'].copy()

        # 날짜 컬럼 자동 감지
        date_col = None
        for col in ['날짜', '일자', 'date', 'Date']:
            if col in daily_df.columns:
                date_col = col
                break

        if date_col:
            daily_df[date_col] = pd.to_datetime(daily_df[date_col])

        # 주요 KPI
        col1, col2, col3, col4, col5 = st.columns(5)

        # 노출수
        if '노출수' in daily_df.columns:
            total_impressions = daily_df['노출수'].sum()
            with col1:
                st.metric("총 노출수", f"{total_impressions:,.0f}")

        # 클릭수
        if '클릭수' in daily_df.columns:
            total_clicks = daily_df['클릭수'].sum()
            with col2:
                st.metric("총 클릭수", f"{total_clicks:,.0f}")

        # CTR
        if '노출수' in daily_df.columns and '클릭수' in daily_df.columns:
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            with col3:
                st.metric("평균 CTR", f"{avg_ctr:.2f}%")

        # 비용
        if '비용' in daily_df.columns:
            total_cost = daily_df['비용'].sum()
            with col4:
                st.metric("총 비용", f"₩{total_cost:,.0f}")

        # 전환
        if '구독 신청' in daily_df.columns or '전환' in daily_df.columns:
            conv_col = '구독 신청' if '구독 신청' in daily_df.columns else '전환'
            conversions = daily_df[conv_col].sum()
            with col5:
                st.metric("총 전환", f"{conversions:.0f}")

        # 일별 트렌드
        if date_col and '노출수' in daily_df.columns and '클릭수' in daily_df.columns:
            st.subheader("일별 성과 추이")

            daily_sorted = daily_df.sort_values(date_col)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_sorted[date_col], y=daily_sorted['노출수'],
                name='노출수', mode='lines+markers', yaxis='y'
            ))
            fig.add_trace(go.Scatter(
                x=daily_sorted[date_col], y=daily_sorted['클릭수'],
                name='클릭수', mode='lines+markers', yaxis='y2'
            ))

            fig.update_layout(
                title="일별 노출수 및 클릭수",
                xaxis_title="날짜",
                yaxis=dict(title="노출수"),
                yaxis2=dict(title="클릭수", overlaying="y", side="right"),
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("성과 상세 분석")

    col1, col2 = st.columns(2)

    with col1:
        if 'ad_groups' in df_dict:
            st.write("**광고그룹 성과**")
            st.dataframe(df_dict['ad_groups'], use_container_width=True)

    with col2:
        if 'campaign_daily' in df_dict:
            daily_df = df_dict['campaign_daily'].copy()
            if '요일' in daily_df.columns:
                st.write("**요일별 성과**")
                cols_to_sum = [col for col in ['노출수', '클릭수', '비용', '구독 신청'] if col in daily_df.columns]
                if cols_to_sum:
                    weekday_data = daily_df.groupby('요일')[cols_to_sum].sum()
                    st.dataframe(weekday_data, use_container_width=True)

    if 'device_hour' in df_dict:
        st.subheader("기기별 성과")
        device_df = df_dict['device_hour'].copy()

        # 기기별 데이터 필터링
        if '구분' in device_df.columns:
            device_perf = device_df[device_df['구분'] == '기기']
        else:
            device_perf = device_df

        if len(device_perf) > 0 and '값' in device_perf.columns and '클릭수' in device_perf.columns:
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

    if 'keywords' in df_dict:
        keywords_df = df_dict['keywords'].copy()

        # 성과가 좋은 키워드 TOP 10
        if '클릭수' in keywords_df.columns:
            st.write("**성과 TOP 10 키워드**")
            cols_to_show = [col for col in ['키워드', '노출수', '클릭수', 'CTR', '비용', '구독 신청'] if col in keywords_df.columns]
            top_keywords = keywords_df.nlargest(10, '클릭수')[cols_to_show]
            st.dataframe(top_keywords, use_container_width=True)

            # 키워드별 효율성
            if '비용' in keywords_df.columns and '구독 신청' in keywords_df.columns and '키워드' in keywords_df.columns:
                st.subheader("키워드별 비용 효율성")
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

    if 'search_terms' in df_dict:
        st.subheader("검색어 분석")
        search_df = df_dict['search_terms'].copy()

        # 무관어 비용 분석
        if '관련도' in search_df.columns and '비용' in search_df.columns:
            irrelevant = search_df[search_df['관련도'] == '무관']
            if len(irrelevant) > 0:
                wasted_cost = irrelevant['비용'].sum()
                total_cost = search_df['비용'].sum()
                waste_ratio = (wasted_cost / total_cost * 100) if total_cost > 0 else 0

                st.metric("🔴 무관어 낭비 비용", f"₩{wasted_cost:,.0f} ({waste_ratio:.1f}%)")

                st.write("**무관어 TOP 10** (예산 낭비)")
                cols = [col for col in ['검색어', '노출수', '클릭수', '비용'] if col in irrelevant.columns]
                irrelevant_top = irrelevant.nlargest(10, '비용')[cols]
                st.dataframe(irrelevant_top, use_container_width=True)

with tab4:
    st.subheader("시간대별 성과 분석")

    if 'device_hour' in df_dict:
        device_df = df_dict['device_hour'].copy()

        # 시간대 데이터 필터링
        if '구분' in device_df.columns:
            hour_df = device_df[device_df['구분'] == '시간대'].copy()
        else:
            hour_df = device_df

        if len(hour_df) > 0 and '값' in hour_df.columns:
            # 시간대별 추이
            cols_available = [col for col in ['노출수', '클릭수'] if col in hour_df.columns]
            if cols_available:
                fig = px.line(
                    hour_df,
                    x='값',
                    y=cols_available,
                    title='시간대별 성과',
                    labels={'값': '시간대', 'value': '수량'},
                    markers=True,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            # 시간대별 상세 데이터
            st.write("**시간대별 성과 데이터**")
            st.dataframe(hour_df, use_container_width=True)

with tab5:
    st.subheader("캠페인 진단 결과")

    if 'diagnosis' in df_dict:
        diagnosis_df = df_dict['diagnosis'].copy()

        # 진단 결과 표시
        for idx, row in diagnosis_df.iterrows():
            if '심각도' in diagnosis_df.columns and '문제' in diagnosis_df.columns:
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
    else:
        st.info("진단 데이터가 없습니다.")

# 데이터 요약
st.sidebar.divider()
st.sidebar.subheader("📋 데이터 요약")
for name, df in df_dict.items():
    st.sidebar.text(f"**{name}**: {len(df):,} 행 × {len(df.columns)} 열")

# 데이터 다운로드
st.sidebar.divider()
st.sidebar.subheader("💾 분석 결과 다운로드")

for file_name, df in df_dict.items():
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label=f"📥 {file_name}.csv",
        data=csv,
        file_name=f"analyzed_{file_name}.csv",
        mime="text/csv",
        key=f"download_{file_name}"
    )
