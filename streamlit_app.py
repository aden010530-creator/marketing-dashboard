import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

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

if not uploaded_files:
    st.info("👈 사이드바에서 CSV 파일을 업로드하세요")
    st.stop()

# 파일 로드
for uploaded_file in uploaded_files:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
        file_key = uploaded_file.name.replace('.csv', '')
        df_dict[file_key] = df
    except Exception as e:
        st.error(f"❌ {uploaded_file.name} 로드 오류: {str(e)}")

if not df_dict:
    st.error("데이터를 로드할 수 없습니다.")
    st.stop()

# 파일 목록 표시
st.sidebar.divider()
st.sidebar.subheader(f"✅ 로드된 파일 ({len(df_dict)}개)")
for name in df_dict.keys():
    st.sidebar.text(f"• {name}")

# 메인 탭
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 대시보드", "📊 성과분석", "🔍 키워드분석", "⏰ 시간대분석", "💡 진단"])

with tab1:
    st.subheader("📈 캠페인 주요 지표")

    if 'campaign_daily' in df_dict:
        try:
            daily_df = df_dict['campaign_daily'].copy()

            # KPI 계산
            kpi_cols = {}
            if '노출수' in daily_df.columns:
                kpi_cols['impressions'] = daily_df['노출수'].sum()
            if '클릭수' in daily_df.columns:
                kpi_cols['clicks'] = daily_df['클릭수'].sum()
            if '비용' in daily_df.columns:
                kpi_cols['cost'] = daily_df['비용'].sum()
            if '구독 신청' in daily_df.columns:
                kpi_cols['conversions'] = daily_df['구독 신청'].sum()

            # 메트릭 표시
            cols = st.columns(min(5, len(kpi_cols)))
            col_idx = 0

            if 'impressions' in kpi_cols:
                with cols[col_idx]:
                    st.metric("총 노출수", f"{kpi_cols['impressions']:,.0f}")
                col_idx += 1

            if 'clicks' in kpi_cols:
                with cols[col_idx]:
                    st.metric("총 클릭수", f"{kpi_cols['clicks']:,.0f}")
                col_idx += 1

            if 'impressions' in kpi_cols and 'clicks' in kpi_cols:
                ctr = (kpi_cols['clicks'] / kpi_cols['impressions'] * 100) if kpi_cols['impressions'] > 0 else 0
                with cols[col_idx]:
                    st.metric("평균 CTR", f"{ctr:.2f}%")
                col_idx += 1

            if 'cost' in kpi_cols:
                with cols[col_idx]:
                    st.metric("총 비용", f"₩{kpi_cols['cost']:,.0f}")
                col_idx += 1

            if 'conversions' in kpi_cols:
                with cols[col_idx]:
                    st.metric("총 전환", f"{kpi_cols['conversions']:.0f}")

            # 일별 차트
            st.subheader("📅 일별 성과 추이")
            if '노출수' in daily_df.columns and '클릭수' in daily_df.columns:
                fig = px.line(
                    daily_df,
                    y=['노출수', '클릭수'],
                    title="일별 노출수 및 클릭수",
                    markers=True,
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"대시보드 생성 오류: {str(e)}")

with tab2:
    st.subheader("📊 성과 분석")

    col1, col2 = st.columns(2)

    with col1:
        if 'ad_groups' in df_dict:
            try:
                st.write("**광고그룹 성과**")
                st.dataframe(df_dict['ad_groups'], use_container_width=True)
            except Exception as e:
                st.error(f"광고그룹 데이터 오류: {str(e)}")

    with col2:
        if 'campaign_daily' in df_dict:
            try:
                daily_df = df_dict['campaign_daily'].copy()
                if '요일' in daily_df.columns:
                    st.write("**요일별 성과**")
                    cols_to_sum = [col for col in ['노출수', '클릭수', '비용', '구독 신청'] if col in daily_df.columns]
                    if cols_to_sum:
                        weekday_data = daily_df.groupby('요일')[cols_to_sum].sum()
                        st.dataframe(weekday_data, use_container_width=True)
            except Exception as e:
                st.error(f"요일별 분석 오류: {str(e)}")

    if 'device_hour' in df_dict:
        try:
            st.subheader("📱 기기별 성과")
            device_df = df_dict['device_hour'].copy()

            if '구분' in device_df.columns:
                device_perf = device_df[device_df['구분'] == '기기']
            else:
                device_perf = device_df

            if len(device_perf) > 0 and '값' in device_perf.columns and '클릭수' in device_perf.columns:
                fig = px.bar(device_perf, x='값', y='클릭수', color='값', title='기기별 클릭수')
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"기기별 분석 오류: {str(e)}")

with tab3:
    st.subheader("🔍 키워드 분석")

    if 'keywords' in df_dict:
        try:
            keywords_df = df_dict['keywords'].copy()

            if '클릭수' in keywords_df.columns:
                st.write("**성과 TOP 10 키워드**")
                cols_to_show = [col for col in ['키워드', '노출수', '클릭수', 'CTR', '비용', '구독 신청'] if col in keywords_df.columns]
                top_keywords = keywords_df.nlargest(10, '클릭수')[cols_to_show]
                st.dataframe(top_keywords, use_container_width=True)
        except Exception as e:
            st.error(f"키워드 분석 오류: {str(e)}")

    if 'search_terms' in df_dict:
        try:
            st.subheader("🔴 무관어 분석")
            search_df = df_dict['search_terms'].copy()

            if '관련도' in search_df.columns and '비용' in search_df.columns:
                irrelevant = search_df[search_df['관련도'] == '무관']
                if len(irrelevant) > 0:
                    wasted_cost = irrelevant['비용'].sum()
                    total_cost = search_df['비용'].sum()
                    waste_ratio = (wasted_cost / total_cost * 100) if total_cost > 0 else 0

                    st.metric("💸 무관어 낭비 비용", f"₩{wasted_cost:,.0f} ({waste_ratio:.1f}%)")

                    cols = [col for col in ['검색어', '노출수', '클릭수', '비용'] if col in irrelevant.columns]
                    st.dataframe(irrelevant.nlargest(10, '비용')[cols], use_container_width=True)
        except Exception as e:
            st.error(f"무관어 분석 오류: {str(e)}")

with tab4:
    st.subheader("⏰ 시간대별 분석")

    if 'device_hour' in df_dict:
        try:
            device_df = df_dict['device_hour'].copy()

            if '구분' in device_df.columns:
                hour_df = device_df[device_df['구분'] == '시간대'].copy()
            else:
                hour_df = device_df

            if len(hour_df) > 0:
                st.write("**시간대별 성과**")
                st.dataframe(hour_df, use_container_width=True)

                cols_available = [col for col in ['노출수', '클릭수'] if col in hour_df.columns]
                if cols_available and '값' in hour_df.columns:
                    fig = px.line(hour_df, x='값', y=cols_available, markers=True, title="시간대별 추이")
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"시간대 분석 오류: {str(e)}")

with tab5:
    st.subheader("💡 진단")

    if 'diagnosis' in df_dict:
        try:
            diagnosis_df = df_dict['diagnosis'].copy()

            for idx, row in diagnosis_df.iterrows():
                if '심각도' in diagnosis_df.columns and '문제' in diagnosis_df.columns:
                    severity = str(row.get('심각도', '')).strip()
                    issue = str(row.get('문제', '')).strip()
                    description = str(row.get('설명', '')).strip()

                    if issue and issue != 'nan':
                        if severity == '높음':
                            st.error(f"🔴 **{issue}**\n\n{description}")
                        elif severity == '보통':
                            st.warning(f"🟡 **{issue}**\n\n{description}")
                        else:
                            st.info(f"🟢 **{issue}**\n\n{description}")
                        st.divider()
        except Exception as e:
            st.error(f"진단 표시 오류: {str(e)}")
    else:
        st.info("진단 데이터 파일을 업로드하세요.")

# 사이드바 요약
st.sidebar.divider()
st.sidebar.subheader("📋 데이터 요약")
for name, df in df_dict.items():
    st.sidebar.text(f"**{name}**: {len(df):,} 행")

# 다운로드
st.sidebar.divider()
st.sidebar.subheader("💾 다운로드")
for file_name, df in df_dict.items():
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        label=f"📥 {file_name}.csv",
        data=csv,
        file_name=f"analyzed_{file_name}.csv",
        mime="text/csv",
        key=f"download_{file_name}"
    )
