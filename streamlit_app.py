import streamlit as st

st.set_page_config(
    page_title="자기소개 페이지",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "SF Pro Display",
                 "SF Pro Text", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
}

.stApp {
    background-color: #f5f5f7;
    color: #1d1d1f;
}

/* 전체 폭 조정 */
.block-container {
    padding-top: 0rem;
    padding-bottom: 4rem;
    max-width: 1400px;
    padding-left: 0;
    padding-right: 0;
}

/* Streamlit 기본 요소 여백 정리 */
div[data-testid="stVerticalBlock"] > div {
    gap: 0;
}

/* 상단 네비 */
.top-nav {
    position: sticky;
    top: 0;
    z-index: 999;
    width: 100%;
    background: rgba(251, 251, 253, 0.72);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.nav-inner {
    max-width: 1100px;
    margin: 0 auto;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    font-size: 0.92rem;
    color: #1d1d1f;
}

.nav-left {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.nav-menu {
    display: flex;
    gap: 28px;
    color: #1d1d1f;
    opacity: 0.88;
}

.nav-menu span {
    cursor: default;
}

/* 공통 섹션 */
.section {
    padding: 72px 24px;
}

.section-dark {
    background: #000;
    color: #f5f5f7;
}

.section-light {
    background: #f5f5f7;
    color: #1d1d1f;
}

.section-white {
    background: #ffffff;
    color: #1d1d1f;
}

.container {
    max-width: 1100px;
    margin: 0 auto;
}

/* 히어로 */
.hero {
    text-align: center;
    padding: 100px 24px 72px 24px;
    background: linear-gradient(180deg, #fbfbfd 0%, #f5f5f7 100%);
}

.eyebrow {
    font-size: 1.05rem;
    font-weight: 600;
    color: #6e6e73;
    margin-bottom: 10px;
}

.hero-title {
    font-size: clamp(2.8rem, 6vw, 5rem);
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin-bottom: 14px;
}

.hero-subtitle {
    font-size: clamp(1.1rem, 2.2vw, 1.7rem);
    color: #424245;
    line-height: 1.4;
    margin-bottom: 28px;
}

.cta-wrap {
    display: flex;
    justify-content: center;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 42px;
}

.cta-primary {
    display: inline-block;
    background: #0071e3;
    color: white !important;
    padding: 12px 22px;
    border-radius: 999px;
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
}

.cta-secondary {
    display: inline-block;
    background: transparent;
    color: #0071e3 !important;
    padding: 12px 22px;
    border-radius: 999px;
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
    border: 1px solid rgba(0,113,227,0.18);
}

.hero-device {
    margin: 0 auto;
    margin-top: 22px;
    width: min(920px, 92%);
    height: 420px;
    border-radius: 36px;
    background:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,0.9), transparent 30%),
        radial-gradient(circle at 80% 30%, rgba(180,210,255,0.45), transparent 28%),
        linear-gradient(145deg, #dfe7f6 0%, #f9fbff 40%, #d9e6ff 100%);
    box-shadow:
        0 20px 60px rgba(0,0,0,0.10),
        inset 0 1px 0 rgba(255,255,255,0.9);
    position: relative;
    overflow: hidden;
}

.hero-device::before {
    content: "";
    position: absolute;
    inset: 18px;
    border-radius: 26px;
    background: linear-gradient(180deg, #ffffff 0%, #f7f7fa 100%);
    box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);
}

.hero-device::after {
    content: "MINGYU";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: clamp(2.5rem, 8vw, 6rem);
    font-weight: 800;
    letter-spacing: -0.05em;
    color: rgba(29,29,31,0.9);
}

/* 카드 그리드 */
.grid-title {
    text-align: center;
    font-size: clamp(2rem, 4vw, 3.4rem);
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin-bottom: 14px;
}

.grid-subtitle {
    text-align: center;
    font-size: 1.15rem;
    color: #6e6e73;
    margin-bottom: 40px;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
}

.apple-card {
    min-height: 340px;
    border-radius: 28px;
    padding: 34px 32px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}

.card-light {
    background: linear-gradient(180deg, #ffffff 0%, #f7f7fa 100%);
    color: #1d1d1f;
}

.card-dark {
    background: linear-gradient(180deg, #101114 0%, #000000 100%);
    color: #f5f5f7;
}

.card-blue {
    background: linear-gradient(135deg, #eaf2ff 0%, #d9e8ff 48%, #f7fbff 100%);
    color: #1d1d1f;
}

.card-silver {
    background: linear-gradient(135deg, #f3f4f7 0%, #ffffff 55%, #eceef3 100%);
    color: #1d1d1f;
}

.card-eyebrow {
    font-size: 0.95rem;
    font-weight: 700;
    margin-bottom: 8px;
    opacity: 0.8;
}

.card-title {
    font-size: clamp(1.8rem, 3vw, 2.7rem);
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.035em;
    margin-bottom: 10px;
}

.card-desc {
    font-size: 1.05rem;
    line-height: 1.5;
    opacity: 0.92;
    max-width: 420px;
}

.card-visual {
    position: absolute;
    right: -20px;
    bottom: -20px;
    width: 220px;
    height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0.08) 45%, transparent 70%);
    filter: blur(2px);
}

.card-dark .card-visual {
    background: radial-gradient(circle, rgba(130,170,255,0.35) 0%, rgba(255,255,255,0.04) 45%, transparent 70%);
}

/* 소개 섹션 */
.profile-wrap {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 24px;
    align-items: stretch;
}

.profile-main, .profile-side {
    border-radius: 28px;
    padding: 40px 36px;
    background: #fff;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.profile-name {
    font-size: clamp(2.4rem, 4vw, 3.8rem);
    line-height: 1.08;
    font-weight: 800;
    letter-spacing: -0.045em;
    margin-bottom: 10px;
}

.profile-oneline {
    font-size: 1.2rem;
    color: #6e6e73;
    margin-bottom: 26px;
}

.profile-text {
    font-size: 1.05rem;
    line-height: 1.8;
    color: #424245;
}

.spec-list {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.spec-item {
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}

.spec-label {
    font-size: 0.95rem;
    color: #6e6e73;
    margin-bottom: 4px;
}

.spec-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1d1d1f;
}

/* 푸터 */
.footer {
    text-align: center;
    padding: 36px 24px 56px 24px;
    font-size: 0.92rem;
    color: #86868b;
    background: #f5f5f7;
}

/* 반응형 */
@media (max-width: 900px) {
    .card-grid,
    .profile-wrap {
        grid-template-columns: 1fr;
    }

    .hero-device {
        height: 280px;
        border-radius: 28px;
    }

    .nav-menu {
        gap: 14px;
        font-size: 0.8rem;
    }

    .section {
        padding: 56px 18px;
    }
}
</style>
""", unsafe_allow_html=True)

# 상단 네비
st.markdown("""
<div class="top-nav">
    <div class="nav-inner">
        <div class="nav-left"></div>
        <div class="nav-menu">
            <span>소개</span>
            <span>역량</span>
            <span>프로젝트</span>
            <span>연락처</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 히어로 섹션
st.markdown("""
<section class="hero">
    <div class="container">
        <div class="eyebrow">자기소개 페이지</div>
        <div class="hero-title">심플하게.<br>강하게.</div>
        <div class="hero-subtitle">
            수학교육, 에듀테크, 그리고 더 나은 학습 경험을 설계하는 사람.
        </div>
        <div class="cta-wrap">
            <a class="cta-primary" href="#">더 알아보기</a>
            <a class="cta-secondary" href="#">연락하기</a>
        </div>
        <div class="hero-device"></div>
    </div>
</section>
""", unsafe_allow_html=True)

# 카드 섹션
st.markdown("""
<section class="section section-light">
    <div class="container">
        <div class="grid-title">핵심 역량.</div>
        <div class="grid-subtitle">깔끔한 구조. 명확한 메시지. 높은 완성도.</div>

        <div class="card-grid">
            <div class="apple-card card-dark">
                <div class="card-eyebrow">Education</div>
                <div class="card-title">수학교육 전공</div>
                <div class="card-desc">
                    수학적 개념을 학생 눈높이에 맞게 재구성하고,
                    학습자가 이해 가능한 형태로 설계합니다.
                </div>
                <div class="card-visual"></div>
            </div>

            <div class="apple-card card-light">
                <div class="card-eyebrow">EdTech</div>
                <div class="card-title">디지털 수업 설계</div>
                <div class="card-desc">
                    에듀테크와 디지털 코스웨어를 활용해
                    효율적이고 효과적인 수업 경험을 만듭니다.
                </div>
                <div class="card-visual"></div>
            </div>

            <div class="apple-card card-blue">
                <div class="card-eyebrow">Project</div>
                <div class="card-title">문제 해결 중심</div>
                <div class="card-desc">
                    단순한 정보 전달이 아니라,
                    실제 문제를 해결하는 구조로 프로젝트를 설계합니다.
                </div>
                <div class="card-visual"></div>
            </div>

            <div class="apple-card card-silver">
                <div class="card-eyebrow">Mindset</div>
                <div class="card-title">디테일과 완성도</div>
                <div class="card-desc">
                    결과물의 밀도, 구조, 표현까지 끝까지 다듬는 태도를 중요하게 봅니다.
                </div>
                <div class="card-visual"></div>
            </div>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# 프로필 섹션
st.markdown("""
<section class="section section-white">
    <div class="container">
        <div class="profile-wrap">
            <div class="profile-main">
                <div class="profile-name">민규</div>
                <div class="profile-oneline">수학교육과 학부생 · 예비교원 · 에듀테크 관심</div>
                <div class="profile-text">
                    저는 수학교육을 전공하며, 학생들이 수학을 더 잘 이해할 수 있도록
                    수업을 설계하는 데 관심이 많습니다.
                    특히 에듀테크와 디지털 도구를 활용해
                    학습 경험을 더 직관적이고 효과적으로 만드는 작업에 집중하고 있습니다.
                    <br><br>
                    단순히 예쁜 결과물보다, 목적에 맞고 실제로 작동하는 구조를 선호합니다.
                    그래서 기획, 내용 구성, 시각적 완성도를 함께 고려하는 편입니다.
                </div>
            </div>

            <div class="profile-side">
                <div class="spec-list">
                    <div class="spec-item">
                        <div class="spec-label">전공</div>
                        <div class="spec-value">수학교육</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">관심 분야</div>
                        <div class="spec-value">에듀테크 · 수업 설계 · 디지털 학습</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">강점</div>
                        <div class="spec-value">구조화 · 기획력 · 높은 완성도</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">지향점</div>
                        <div class="spec-value">학생 중심의 효과적인 수학교육</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# 푸터
st.markdown("""
<div class="footer">
    Copyright © 2026 MINGYU. All rights reserved.
</div>
""", unsafe_allow_html=True)