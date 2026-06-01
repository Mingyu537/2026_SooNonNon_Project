import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.express as px

# -----------------------------------
# 한글 폰트 설정
# -----------------------------------
KOREAN_FONT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "fonts",
    "NotoSansKR-VariableFont_wght.ttf"
)

if os.path.exists(KOREAN_FONT_PATH):
    fm.fontManager.addfont(KOREAN_FONT_PATH)
    KOREAN_FONT_NAME = fm.FontProperties(fname=KOREAN_FONT_PATH).get_name()
    plt.rc("font", family=KOREAN_FONT_NAME)
else:
    KOREAN_FONT_NAME = "Malgun Gothic"
    plt.rc("font", family=KOREAN_FONT_NAME)

plt.rcParams["axes.unicode_minus"] = False

# -----------------------------------
# 페이지 설정
# -----------------------------------
st.set_page_config(page_title="데이터 시각화", layout="wide")

st.title("데이터 입력형 시각화 대시보드")
st.write("표의 셀 값을 직접 수정하면 아래 분석 결과와 그래프가 바로 반영됩니다.")

# -----------------------------------
# 기본 데이터
# -----------------------------------
if "edited_df" not in st.session_state:
    st.session_state.edited_df = pd.DataFrame({
        "월": ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"],
        "매출(억원)": [88, 102, 95, 110, 120, 98, 130, 125, 140, 138, 145, 150],
        "방문자수(명)": [1200, 1450, 1700, 1600, 2100, 1950, 2500, 2400, 2700, 2650, 2900, 3100],
        "이탈률(%)": [18.2, 17.5, 16.8, 15.9, 14.8, 15.1, 13.9, 13.5, 12.7, 12.9, 11.8, 11.2]
    })

# -----------------------------------
# 데이터 편집
# -----------------------------------
st.subheader("데이터 입력 표")

edited_df = st.data_editor(
    st.session_state.edited_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "월": st.column_config.TextColumn("월"),
        "매출(억원)": st.column_config.NumberColumn("매출(억원)", format="%.1f"),
        "방문자수(명)": st.column_config.NumberColumn("방문자수(명)", format="%d"),
        "이탈률(%)": st.column_config.NumberColumn("이탈률(%)", format="%.1f")
    },
    key="data_editor"
)

# 세션 상태 업데이트
st.session_state.edited_df = edited_df.copy()

# -----------------------------------
# 숫자형 컬럼 처리
# -----------------------------------
df = edited_df.copy()

numeric_cols = ["매출(억원)", "방문자수(명)", "이탈률(%)"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["월"]).reset_index(drop=True)

# -----------------------------------
# 데이터가 비어 있을 때 예외 처리
# -----------------------------------
if df.empty:
    st.warning("표에 데이터가 없습니다. 최소 1행 이상 입력하세요.")
    st.stop()

valid_numeric_df = df.dropna(subset=numeric_cols)

if valid_numeric_df.empty:
    st.warning("숫자 데이터가 없어 분석을 진행할 수 없습니다. 숫자 열에 값을 입력하세요.")
    st.stop()

# -----------------------------------
# 요약 통계
# -----------------------------------
st.subheader("분석 결과 요약")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("총매출", f"{valid_numeric_df['매출(억원)'].sum():.1f} 억원")
    st.metric("평균 매출", f"{valid_numeric_df['매출(억원)'].mean():.1f} 억원")

with col2:
    st.metric("총 방문자수", f"{int(valid_numeric_df['방문자수(명)'].sum()):,} 명")
    st.metric("평균 방문자수", f"{int(valid_numeric_df['방문자수(명)'].mean()):,} 명")

with col3:
    st.metric("평균 이탈률", f"{valid_numeric_df['이탈률(%)'].mean():.1f}%")
    max_month_idx = valid_numeric_df["매출(억원)"].idxmax()
    st.metric(
        "최고 매출 월",
        f"{valid_numeric_df.loc[max_month_idx, '월']} / {valid_numeric_df.loc[max_month_idx, '매출(억원)']:.1f}억원"
    )

# -----------------------------------
# 기초 통계표
# -----------------------------------
st.subheader("기초 통계표")

summary_df = pd.DataFrame({
    "항목": ["매출(억원)", "방문자수(명)", "이탈률(%)"],
    "평균": [
        valid_numeric_df["매출(억원)"].mean(),
        valid_numeric_df["방문자수(명)"].mean(),
        valid_numeric_df["이탈률(%)"].mean()
    ],
    "최댓값": [
        valid_numeric_df["매출(억원)"].max(),
        valid_numeric_df["방문자수(명)"].max(),
        valid_numeric_df["이탈률(%)"].max()
    ],
    "최솟값": [
        valid_numeric_df["매출(억원)"].min(),
        valid_numeric_df["방문자수(명)"].min(),
        valid_numeric_df["이탈률(%)"].min()
    ]
})

st.dataframe(
    summary_df.style.format({
        "평균": "{:.1f}",
        "최댓값": "{:.1f}",
        "최솟값": "{:.1f}"
    }),
    use_container_width=True
)

# -----------------------------------
# matplotlib 그래프
# -----------------------------------
st.subheader("matplotlib 그래프")

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(valid_numeric_df["월"], valid_numeric_df["매출(억원)"], marker="o")
ax1.set_title("월별 매출 추이")
ax1.set_xlabel("월")
ax1.set_ylabel("매출(억원)")
ax1.grid(True, alpha=0.3)
st.pyplot(fig1)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.bar(valid_numeric_df["월"], valid_numeric_df["방문자수(명)"])
ax2.set_title("월별 방문자수")
ax2.set_xlabel("월")
ax2.set_ylabel("방문자수(명)")
st.pyplot(fig2)

# -----------------------------------
# plotly 그래프
# -----------------------------------
st.subheader("plotly 그래프")

fig3 = px.scatter(
    valid_numeric_df,
    x="방문자수(명)",
    y="매출(억원)",
    size="이탈률(%)",
    hover_name="월",
    title="방문자수와 매출의 관계",
    labels={
        "방문자수(명)": "방문자수(명)",
        "매출(억원)": "매출(억원)",
        "이탈률(%)": "이탈률(%)"
    }
)
fig3.update_layout(font=dict(family=KOREAN_FONT_NAME))
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(
    valid_numeric_df,
    x="월",
    y=["매출(억원)", "이탈률(%)"],
    markers=True,
    title="월별 매출 및 이탈률 추이",
    labels={"value": "값", "variable": "항목"}
)
fig4.update_layout(font=dict(family=KOREAN_FONT_NAME))
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------------
# 상관관계 분석
# -----------------------------------
st.subheader("상관관계 분석")

corr_df = valid_numeric_df[numeric_cols].corr().round(2)
st.dataframe(corr_df, use_container_width=True)

fig5 = px.imshow(
    corr_df,
    text_auto=True,
    aspect="auto",
    title="수치형 데이터 상관관계"
)
fig5.update_layout(font=dict(family=KOREAN_FONT_NAME))
st.plotly_chart(fig5, use_container_width=True)