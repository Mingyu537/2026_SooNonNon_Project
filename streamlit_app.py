import streamlit as st

# 페이지 설정
st.set_page_config(page_title="자기소개", page_icon="👋", layout="wide")

# 약간의 스타일
st.markdown("""
<style>
    .big-number {
        font-size: 28px;
        font-weight: 800;
        color: #1f6feb;
        line-height: 1.1;
    }
    .subtext {
        color: #6e7781;
        font-size: 14px;
        margin-top: -8px;
    }
</style>
""", unsafe_allow_html=True)

# ===== 기본 정보 =====
st.title("👋 나를 소개합니다")
st.caption("간단하지만 정확하게!")

# 좌우 레이아웃
left, right = st.columns([1, 2])

with left:
    # 프로필 사진이 있으면 넣어보자 (없으면 오류 없이 넘어감)
    try:
        st.image("profile.jpg", use_column_width=True)
    except Exception:
        st.info("프로필 사진은 **profile.jpg**로 프로젝트 폴더에 넣으면 자동으로 보여줘요 :)")

with right:
    name = "민규"
    age = "23"     # 숫자만 원하면 숫자로 써도 OK
    major = "사범대학 수학교육과"
    school_year = "4학년"   # 상황에 맞게 변경

    st.markdown(f"**이름** : {name}")
    st.markdown(f"**나이** : {age}세")
    st.markdown(f"**소속** : {major}")
    st.markdown(f"**학년** : {school_year}")

# ===== 자기소개 =====
st.header("🙋‍♂️ About Me")
st.write("""
저는 수학교육을 전공하면서 **학생들을 효율적으로 가르치는 방법**에 관심이 많아요.
특히 **에듀테크 / 디지털 코스웨어**를 활용해 수업의 질을 끌어올리는 것에 관심이 큽니다.
""")

# ===== 관심사 & 취미 =====
st.header("🎯 관심 분야")
st.write("""
- 수업 설계(교수설계) + 학습 효과 분석
- 에듀테크 도구를 활용한 수업 자동화/개선
- 디지털 콘텐츠 제작(예: 인터랙티브 자료)
""")

st.header("🧩 취미")
st.write("""
- 운동/헬스  
- 여행/카페 탐방  
- (옵션) 개발/데이터 분석/알고리즘 공부  
""")

# ===== 끝 =====
st.divider()
st.write("끝! 👀 필요하면 더 디테일한 섹션(프로젝트/역량/연락처)도 추가할 수 있어요.")