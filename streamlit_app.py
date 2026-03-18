import streamlit as st

st.set_page_config(
    page_title="자기소개 페이지",
    page_icon="👋",
    layout="wide"
)

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1000px;
}

.hero {
    padding: 2.5rem 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #f8fafc, #e9f2ff);
    margin-bottom: 1.5rem;
}

.card {
    padding: 1.5rem;
    border-radius: 20px;
    background-color: #f8f9fa;
    margin-bottom: 1rem;
}

.name {
    font-size: 2.4rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.one-line {
    font-size: 1.1rem;
    color: #555;
    margin-bottom: 1rem;
}

.label {
    font-size: 0.95rem;
    color: #777;
    margin-bottom: 0.2rem;
}

.value {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.tag {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
    border-radius: 999px;
    background-color: #eef2ff;
    font-size: 0.95rem;
}

.footer {
    text-align: center;
    color: #888;
    margin-top: 2rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 상단 소개
# -----------------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.image(
        "https://via.placeholder.com/300x300.png?text=Profile+Image",
        use_container_width=True
    )

with col2:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<div class="name">[김민규]</div>', unsafe_allow_html=True)
    st.markdown('<div class="one-line">[한 줄 소개를 입력하세요]</div>', unsafe_allow_html=True)

    st.markdown('<div class="label">소속</div>', unsafe_allow_html=True)
    st.markdown('<div class="value">[인천대학교 / 수학교육과]</div>', unsafe_allow_html=True)

    st.markdown('<div class="label">관심 분야</div>', unsafe_allow_html=True)
    st.markdown('<div class="value">[관심 분야 입력]</div>', unsafe_allow_html=True)

    st.markdown("""
    <span class="tag">#키워드1</span>
    <span class="tag">#키워드2</span>
    <span class="tag">#키워드3</span>
    <span class="tag">#키워드4</span>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 자기소개 문장
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("About Me")
st.write("""
여기에 자기소개 내용을 자유롭게 작성하면 됩니다.

예시:
- 나는 어떤 사람인지
- 어떤 공부를 하고 있는지
- 무엇에 관심이 있는지
- 앞으로 어떤 목표가 있는지
""")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 경험 / 활동
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Experience")
st.write("""
**[활동명 또는 프로젝트명 1]**  
- 기간: [예: 2025.03 ~ 2025.06]  
- 설명: [내용 입력]

**[활동명 또는 프로젝트명 2]**  
- 기간: [기간 입력]  
- 설명: [내용 입력]

**[활동명 또는 프로젝트명 3]**  
- 기간: [기간 입력]  
- 설명: [내용 입력]
""")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 강점 / 역량
# -----------------------------
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Strengths")
    st.write("""
    - [강점 1]
    - [강점 2]
    - [강점 3]
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Skills")
    st.write("""
    - [기술 또는 역량 1]
    - [기술 또는 역량 2]
    - [기술 또는 역량 3]
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 연락처
# -----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Contact")
st.write("""
- 이메일: [이메일 입력]
- GitHub: [링크 입력]
- 블로그 / 포트폴리오: [링크 입력]
- SNS: [링크 입력]
""")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# 하단 문구
# -----------------------------
st.markdown('<div class="footer">© 2026 [이름] Portfolio Page</div>', unsafe_allow_html=True)