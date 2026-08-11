import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="마케팅 캠페인 분석 대시보드", layout="wide")
st.title("📊 홈핏 마케팅 캠페인 분석 대시보드")

# ===== 데이터 자동 로드 =====
df_dict = {}
data_dir = Path(__file__).parent / "data"

files_to_load = {
    'campaign_daily': 'campaign_daily.csv',
    'device_hour': 'device_hour.csv',
    'keywords': 'keywords.csv',
    'search_terms': 'search_terms.csv',
    'ad_groups': 'ad_groups.csv',
    'diagnosis': 'diagnosis.csv',
}

for name, filename in files_to_load.items():
    filepath = data_dir / filename
    try:
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        df_dict[name] = df
    except:
        pass

if not df_dict:
    st.error("데이터 파일을 찾을 수 없습니다")
    st.stop()

# ===== 로드된 데이터 표시 =====
st.sidebar.subheader(f"✅ 로드된 데이터 ({len(df_dict)}개)")
for name in df_dict.keys():
    st.sidebar.text(f"• {name}")

st.sidebar.divider()
st.sidebar.info(f"📅 분석 기간: 2026-07-06 ~ 2026-08-04")

# ===== 탭 구성 =====
tabs = st.tabs(["📈 대시보드", "📊 성과분석", "🔍 키워드분석", "⏰ 시간대분석", "💡 진단"])

# ===== TAB 1: 대시보드 =====
with tabs[0]:
    st.subheader("📈 캠페인 주요 지표")

    if 'campaign_daily' in df_dict:
        df = df_dict['campaign_daily']

        # KPI 메트릭
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("총 노출수", f"{df['노출수'].sum():,.0f}")

        with col2:
            st.metric("총 클릭수", f"{df['클릭수'].sum():,.0f}")

        with col3:
            imp = df['노출수'].sum()
            clk = df['클릭수'].sum()
            ctr = (clk / imp * 100) if imp > 0 else 0
            st.metric("평균 CTR", f"{ctr:.2f}%")

        with col4:
            st.metric("총 비용", f"₩{df['비용'].sum():,.0f}")

        with col5:
            st.metric("총 전환", f"{df['구독 신청'].sum():.0f}")

        # 일별 차트
        st.subheader("📅 일별 성과 추이")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=df['노출수'],
            name='노출수',
            mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy'
        ))
        fig.add_trace(go.Scatter(
            y=df['클릭수'],
            name='클릭수',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2)
        ))
        fig.update_layout(
            title="일별 노출수 및 클릭수 추이",
            xaxis_title="날짜",
            yaxis_title="수량",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # 요일별 성과
        st.subheader("📊 요일별 성과")
        weekday_order = ['월', '화', '수', '목', '금', '토', '일']
        weekday_data = df.groupby('요일')[['노출수', '클릭수', '비용', '구독 신청']].sum()
        weekday_data = weekday_data.reindex([d for d in weekday_order if d in weekday_data.index])

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(weekday_data, use_container_width=True)
        with col2:
            fig = px.bar(weekday_data.reset_index(), x='요일', y='클릭수',
                        title='요일별 클릭수', color='클릭수', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

# ===== TAB 2: 성과분석 =====
with tabs[1]:
    st.subheader("📊 성과 분석")

    col1, col2 = st.columns(2)

    with col1:
        if 'ad_groups' in df_dict:
            st.write("**광고그룹별 성과**")
            st.dataframe(df_dict['ad_groups'], use_container_width=True)

    with col2:
        if 'campaign_daily' in df_dict:
            df = df_dict['campaign_daily']
            st.write("**주요 지표 요약**")
            summary = pd.DataFrame({
                '지표': ['평균 노출수', '평균 클릭수', '평균 CPC', '평균 CTR'],
                '값': [
                    f"{df['노출수'].mean():.0f}",
                    f"{df['클릭수'].mean():.0f}",
                    f"₩{df['평균 CPC'].mean():.0f}",
                    f"{df['CTR'].str.rstrip('%').astype(float).mean():.2f}%"
                ]
            })
            st.dataframe(summary, use_container_width=True, hide_index=True)

    # 기기별 성과
    if 'device_hour' in df_dict:
        st.subheader("📱 기기별 성과")
        df = df_dict['device_hour']
        device_df = df[df['구분'] == '기기']

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(device_df, use_container_width=True)
        with col2:
            fig = px.pie(device_df, values='클릭수', names='값', title='기기별 클릭수 비율')
            st.plotly_chart(fig, use_container_width=True)

# ===== TAB 3: 키워드분석 =====
with tabs[2]:
    st.subheader("🔍 키워드 성과 분석")

    if 'keywords' in df_dict:
        df = df_dict['keywords']
        st.write("**성과 TOP 10 키워드**")
        top_keywords = df.nlargest(10, '클릭수')[['키워드', '노출수', '클릭수', 'CTR', '평균 CPC', '비용', '구독 신청']]
        st.dataframe(top_keywords, use_container_width=True)

        # 키워드별 효율성
        st.subheader("💰 키워드별 효율성")
        fig = px.scatter(
            df,
            x='비용',
            y='구독 신청',
            size='클릭수',
            hover_name='키워드',
            color='CTR',
            title='비용 vs 전환',
            labels={'비용': '비용 (₩)', '구독 신청': '전환 수'},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # 무관어 분석
    if 'search_terms' in df_dict:
        st.subheader("🔴 무관어로 인한 예산 낭비")
        df = df_dict['search_terms']

        # 관련도별 비용 분석
        if '관련도' in df.columns:
            relevance_cost = df.groupby('관련도')['비용'].sum().sort_values(ascending=False)
            total_cost = df['비용'].sum()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("🔴 무관어 낭비", f"₩{relevance_cost.get('무관', 0):,.0f}")
            with col2:
                st.metric("💸 전체 대비", f"{relevance_cost.get('무관', 0) / total_cost * 100:.1f}%")

            st.write("**무관어 TOP 10** (예산 낭비)")
            waste = df[df['관련도'] == '무관'].nlargest(10, '비용')[['검색어', '노출수', '클릭수', '비용']]
            st.dataframe(waste, use_container_width=True)

            # 관련도별 파이 차트
            st.write("**관련도별 비용 분포**")
            fig = px.pie(
                relevance_cost.reset_index(),
                values='비용',
                names='관련도',
                title='관련도별 비용 분포',
                color_discrete_map={'정확 일치': '#2ecc71', '관련': '#3498db', '느슨함': '#f39c12', '무관': '#e74c3c'}
            )
            st.plotly_chart(fig, use_container_width=True)

# ===== TAB 4: 시간대분석 =====
with tabs[3]:
    st.subheader("⏰ 시간대별 성과 분석")

    if 'device_hour' in df_dict:
        df = df_dict['device_hour']
        hour_df = df[df['구분'] == '시간대'].copy()

        # 시간대별 추이
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hour_df['값'],
            y=hour_df['노출수'],
            name='노출수',
            mode='lines+markers',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=hour_df['값'],
            y=hour_df['클릭수'],
            name='클릭수',
            mode='lines+markers',
            line=dict(color='red'),
            yaxis='y2'
        ))
        fig.update_layout(
            title="시간대별 노출수 및 클릭수",
            xaxis_title="시간대",
            yaxis=dict(title="노출수"),
            yaxis2=dict(title="클릭수", overlaying="y", side="right"),
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # 시간대별 상세 데이터
        st.subheader("📊 시간대별 상세 데이터")
        st.dataframe(hour_df, use_container_width=True)

        # 최고 성과 시간대
        col1, col2, col3 = st.columns(3)
        with col1:
            best_time = hour_df.loc[hour_df['노출수'].idxmax(), '값']
            st.metric("🔝 최고 노출 시간", best_time)
        with col2:
            best_click_time = hour_df.loc[hour_df['클릭수'].idxmax(), '값']
            st.metric("🔝 최고 클릭 시간", best_click_time)
        with col3:
            best_ctr = hour_df.loc[hour_df['CTR'].str.rstrip('%').astype(float).idxmax(), '값']
            st.metric("🔝 최고 CTR 시간", best_ctr)

# ===== TAB 5: 진단 =====
with tabs[4]:
    st.subheader("💡 캠페인 진단 결과")

    if 'diagnosis' in df_dict:
        df = df_dict['diagnosis']

        for _, row in df.iterrows():
            severity = str(row.get('심각도', '')).strip()
            issue = str(row.get('문제', '')).strip()
            desc = str(row.get('설명', '')).strip()
            action = str(row.get('조치', '')).strip()

            if issue and issue != 'nan':
                if severity == '높음':
                    st.error(f"🔴 **{issue}**")
                elif severity == '보통':
                    st.warning(f"🟡 **{issue}**")
                else:
                    st.success(f"🟢 **{issue}**")

                st.write(f"**설명**: {desc}")
                st.write(f"**조치**: {action}")
                st.divider()

# ===== 푸터 =====
st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.write(
    """
    ### 📌 대시보드 정보
    - **분석 기간**: 2026-07-06 ~ 2026-08-04 (30일)
    - **총 예산**: ₩1,080,000
    - **총 전환**: 2건
    - **데이터 출처**: Google Ads
    """
)
