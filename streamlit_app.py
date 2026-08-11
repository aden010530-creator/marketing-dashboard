import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="마케팅 캠페인 분석 대시보드", layout="wide")
st.title("📊 마케팅 캠페인 분석 대시보드")
st.markdown("CSV 파일을 업로드하면 자동으로 분석합니다 🚀")

# ===== 파일 업로드 =====
st.sidebar.header("📤 CSV 파일 업로드")
uploaded_files = st.sidebar.file_uploader(
    "분석할 CSV 파일을 선택하세요:",
    type=['csv'],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("👈 사이드바에서 CSV 파일을 업로드하세요")
    st.stop()

# ===== 데이터 로드 =====
df_dict = {}
for file in uploaded_files:
    try:
        df = pd.read_csv(file, encoding='utf-8-sig')
        name = file.name.replace('.csv', '')
        df_dict[name] = df
    except Exception as e:
        st.error(f"❌ {file.name}: {str(e)}")

if not df_dict:
    st.error("파일을 로드할 수 없습니다")
    st.stop()

# ===== 로드된 파일 표시 =====
st.sidebar.divider()
st.sidebar.subheader(f"✅ 로드된 파일 ({len(df_dict)}개)")
for name in df_dict.keys():
    st.sidebar.text(f"• {name}")

# ===== 탭 구성 =====
tabs = st.tabs(["📈 대시보드", "📊 성과분석", "🔍 키워드분석", "⏰ 시간대분석", "💡 진단"])

# ===== TAB 1: 대시보드 =====
with tabs[0]:
    st.subheader("📈 주요 지표")

    if 'campaign_daily' in df_dict:
        df = df_dict['campaign_daily']

        # KPI 계산
        try:
            col1, col2, col3, col4, col5 = st.columns(5)

            if '노출수' in df.columns:
                with col1:
                    st.metric("총 노출수", f"{df['노출수'].sum():,.0f}")

            if '클릭수' in df.columns:
                with col2:
                    st.metric("총 클릭수", f"{df['클릭수'].sum():,.0f}")

            if '노출수' in df.columns and '클릭수' in df.columns:
                imp = df['노출수'].sum()
                clk = df['클릭수'].sum()
                ctr = (clk / imp * 100) if imp > 0 else 0
                with col3:
                    st.metric("평균 CTR", f"{ctr:.2f}%")

            if '비용' in df.columns:
                with col4:
                    st.metric("총 비용", f"₩{df['비용'].sum():,.0f}")

            if '구독 신청' in df.columns:
                with col5:
                    st.metric("총 전환", f"{df['구독 신청'].sum():.0f}")
        except Exception as e:
            st.error(f"KPI 계산 오류: {str(e)}")

        # 일별 차트
        st.subheader("📅 일별 성과")
        try:
            if '노출수' in df.columns and '클릭수' in df.columns and len(df) > 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=df['노출수'],
                    name='노출수',
                    mode='lines+markers',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    y=df['클릭수'],
                    name='클릭수',
                    mode='lines+markers',
                    line=dict(color='red')
                ))
                fig.update_layout(title="일별 노출수 및 클릭수", height=400, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"차트 생성 오류: {str(e)}")

# ===== TAB 2: 성과분석 =====
with tabs[1]:
    st.subheader("📊 성과 분석")

    col1, col2 = st.columns(2)

    with col1:
        if 'ad_groups' in df_dict:
            st.write("**광고그룹 성과**")
            st.dataframe(df_dict['ad_groups'], use_container_width=True)

    with col2:
        if 'campaign_daily' in df_dict:
            df = df_dict['campaign_daily']
            if '요일' in df.columns:
                st.write("**요일별 성과**")
                cols = [c for c in ['노출수', '클릭수', '비용', '구독 신청'] if c in df.columns]
                if cols:
                    st.dataframe(df.groupby('요일')[cols].sum(), use_container_width=True)

    if 'device_hour' in df_dict:
        st.subheader("📱 기기별 성과")
        df = df_dict['device_hour']
        if '구분' in df.columns:
            device_df = df[df['구분'] == '기기']
        else:
            device_df = df

        if len(device_df) > 0 and '값' in device_df.columns and '클릭수' in device_df.columns:
            fig = px.bar(device_df, x='값', y='클릭수', color='값', title='기기별 클릭수')
            st.plotly_chart(fig, use_container_width=True)

# ===== TAB 3: 키워드분석 =====
with tabs[2]:
    st.subheader("🔍 키워드 분석")

    if 'keywords' in df_dict:
        df = df_dict['keywords']
        if '클릭수' in df.columns:
            st.write("**성과 TOP 10 키워드**")
            cols = [c for c in ['키워드', '노출수', '클릭수', 'CTR', '비용', '구독 신청'] if c in df.columns]
            st.dataframe(df.nlargest(10, '클릭수')[cols], use_container_width=True)

    if 'search_terms' in df_dict:
        st.subheader("🔴 무관어 낭비")
        df = df_dict['search_terms']
        if '관련도' in df.columns and '비용' in df.columns:
            waste = df[df['관련도'] == '무관']
            if len(waste) > 0:
                wasted = waste['비용'].sum()
                total = df['비용'].sum()
                ratio = (wasted / total * 100) if total > 0 else 0
                st.metric("💸 무관어 낭비 비용", f"₩{wasted:,.0f} ({ratio:.1f}%)")

                cols = [c for c in ['검색어', '노출수', '클릭수', '비용'] if c in waste.columns]
                st.dataframe(waste.nlargest(10, '비용')[cols], use_container_width=True)

# ===== TAB 4: 시간대분석 =====
with tabs[3]:
    st.subheader("⏰ 시간대별 분석")

    if 'device_hour' in df_dict:
        df = df_dict['device_hour']
        if '구분' in df.columns:
            hour_df = df[df['구분'] == '시간대']
        else:
            hour_df = df

        if len(hour_df) > 0:
            st.dataframe(hour_df, use_container_width=True)

            cols = [c for c in ['노출수', '클릭수'] if c in hour_df.columns]
            if cols and '값' in hour_df.columns:
                fig = px.line(hour_df, x='값', y=cols, markers=True, title="시간대별 추이")
                st.plotly_chart(fig, use_container_width=True)

# ===== TAB 5: 진단 =====
with tabs[4]:
    st.subheader("💡 진단 결과")

    if 'diagnosis' in df_dict:
        df = df_dict['diagnosis']
        if '심각도' in df.columns and '문제' in df.columns:
            for _, row in df.iterrows():
                severity = str(row.get('심각도', '')).strip()
                issue = str(row.get('문제', '')).strip()
                desc = str(row.get('설명', '')).strip()

                if issue and issue != 'nan':
                    if severity == '높음':
                        st.error(f"🔴 {issue}\n\n{desc}")
                    elif severity == '보통':
                        st.warning(f"🟡 {issue}\n\n{desc}")
                    else:
                        st.info(f"🟢 {issue}\n\n{desc}")
                    st.divider()
    else:
        st.info("진단 데이터가 없습니다")

# ===== 사이드바: 다운로드 =====
st.sidebar.divider()
st.sidebar.subheader("💾 다운로드")
for name, df in df_dict.items():
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.sidebar.download_button(
        f"📥 {name}.csv",
        csv,
        f"analyzed_{name}.csv",
        "text/csv",
        key=f"dl_{name}"
    )
