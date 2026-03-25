import streamlit as st

st.set_page_config(
    page_title="iPhone 스타일 랜딩",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #f5f5f7;
    --text: #1d1d1f;
    --sub: #6e6e73;
    --blue: #0071e3;
    --white: #ffffff;
    --line: rgba(0,0,0,0.08);
    --panel: #fbfbfd;
    --dark: #000000;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "SF Pro Display",
                 "SF Pro Text", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
    color: var(--text);
}

body {
    background: var(--bg);
}

.stApp {
    background: var(--bg);
}

header[data-testid="stHeader"] {
    background: transparent;
}

div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0;
    position: fixed;
}

#MainMenu, footer {
    visibility: hidden;
}

.block-container {
    max-width: 100%;
    padding: 0;
}

section[data-testid="stSidebar"] {
    display: none !important;
}

/* ---------- global nav ---------- */
.global-nav {
    position: sticky;
    top: 0;
    z-index: 9999;
    height: 44px;
    background: rgba(251, 251, 253, 0.78);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.global-nav-inner {
    max-width: 1024px;
    height: 44px;
    margin: 0 auto;
    padding: 0 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    font-size: 12px;
    color: var(--text);
}

.global-nav-left,
.global-nav-right {
    display: flex;
    align-items: center;
    gap: 24px;
}

.global-nav .apple {
    font-size: 16px;
    font-weight: 700;
    margin-right: 4px;
}

.global-nav a {
    color: var(--text);
    text-decoration: none;
    opacity: 0.85;
    white-space: nowrap;
}

/* ---------- local nav ---------- */
.local-nav {
    height: 52px;
    background: rgba(255,255,255,0.72);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.local-nav-inner {
    max-width: 1100px;
    height: 52px;
    margin: 0 auto;
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.local-title {
    font-size: 21px;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.local-links {
    display: flex;
    gap: 18px;
    flex-wrap: wrap;
    align-items: center;
    justify-content: flex-end;
}

.local-links a {
    font-size: 12px;
    color: #424245;
    text-decoration: none;
}

.buy-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 28px;
    padding: 0 12px;
    border-radius: 999px;
    background: var(--blue);
    color: white !important;
    font-size: 12px !important;
    font-weight: 600;
}

/* ---------- containers ---------- */
.wrap {
    max-width: 1400px;
    margin: 0 auto;
}

.section {
    padding: 20px 12px;
}

.section-tight {
    padding-top: 12px;
}

.hero {
    background: linear-gradient(180deg, #f7f7fa 0%, #ececf1 100%);
    border-radius: 0 0 32px 32px;
    overflow: hidden;
}

.hero-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 72px 24px 40px;
    text-align: center;
}

.hero-eyebrow {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin-bottom: 12px;
}

.hero-title {
    font-size: clamp(44px, 9vw, 112px);
    line-height: 0.95;
    font-weight: 900;
    letter-spacing: -0.06em;
    margin: 0;
}

.hero-sub {
    margin-top: 18px;
    font-size: clamp(19px, 2.2vw, 28px);
    line-height: 1.25;
    color: #424245;
    font-weight: 500;
}

.hero-links {
    margin-top: 20px;
    display: flex;
    gap: 26px;
    justify-content: center;
    flex-wrap: wrap;
}

.hero-links a {
    color: var(--blue);
    text-decoration: none;
    font-size: 21px;
    font-weight: 500;
}

.hero-links a::after {
    content: " ›";
}

.hero-visual {
    margin: 36px auto 0;
    width: min(1120px, 96%);
    height: 560px;
    border-radius: 40px;
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 50% 25%, rgba(255,255,255,0.92) 0%, rgba(255,255,255,0.20) 18%, transparent 34%),
        radial-gradient(circle at 22% 70%, rgba(152,178,255,0.32), transparent 26%),
        radial-gradient(circle at 78% 70%, rgba(204,168,255,0.26), transparent 24%),
        linear-gradient(180deg, #161618 0%, #272730 30%, #d7dce9 76%, #f6f7fb 100%);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.18);
}

.phone {
    position: absolute;
    bottom: -10px;
    width: 250px;
    height: 500px;
    border-radius: 42px;
    background: linear-gradient(180deg, #0d0d10 0%, #20242b 42%, #111216 100%);
    box-shadow:
        0 18px 60px rgba(0,0,0,0.22),
        inset 0 0 0 2px rgba(255,255,255,0.08);
}

.phone::before {
    content: "";
    position: absolute;
    inset: 10px;
    border-radius: 34px;
    background:
        radial-gradient(circle at 50% 20%, rgba(120,170,255,0.9), transparent 20%),
        linear-gradient(180deg, #15161b 0%, #232736 40%, #8fa8ff 100%);
}

.phone::after {
    content: "";
    position: absolute;
    top: 18px;
    left: 50%;
    transform: translateX(-50%);
    width: 110px;
    height: 26px;
    border-radius: 999px;
    background: rgba(0,0,0,0.86);
    z-index: 4;
}

.phone.left { left: 24%; transform: rotate(-10deg); }
.phone.center { left: 50%; transform: translateX(-50%); z-index: 3; }
.phone.right { right: 24%; transform: rotate(10deg); }

.hero-caption {
    margin-top: 26px;
    font-size: 14px;
    color: var(--sub);
}

/* ---------- feature cards ---------- */
.grid-wrap {
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 12px 18px;
}

.grid-2 {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.card {
    min-height: 700px;
    border-radius: 28px;
    overflow: hidden;
    position: relative;
    padding: 56px 48px;
    background: #fff;
}

.card.light {
    background: linear-gradient(180deg, #ffffff 0%, #f5f5f7 100%);
    color: var(--text);
}

.card.dark {
    background: linear-gradient(180deg, #000000 0%, #101115 100%);
    color: #f5f5f7;
}

.card.blue {
    background: linear-gradient(180deg, #dfe9ff 0%, #eef4ff 42%, #ffffff 100%);
}

.card.gray {
    background: linear-gradient(180deg, #f0f1f5 0%, #ffffff 100%);
}

.card-kicker {
    font-size: 21px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 10px;
}

.card-title {
    font-size: clamp(34px, 4vw, 64px);
    line-height: 1.03;
    font-weight: 800;
    letter-spacing: -0.05em;
    max-width: 720px;
}

.card-desc {
    margin-top: 18px;
    font-size: 21px;
    line-height: 1.35;
    max-width: 700px;
    color: inherit;
    opacity: 0.92;
}

.card-link {
    display: inline-block;
    margin-top: 18px;
    text-decoration: none;
    color: var(--blue);
    font-size: 19px;
    font-weight: 500;
}

.card-link::after {
    content: " ›";
}

.visual-ring {
    position: absolute;
    right: -80px;
    bottom: -80px;
    width: 460px;
    height: 460px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0.15) 35%, transparent 65%);
    filter: blur(2px);
}

.dark .visual-ring {
    background: radial-gradient(circle, rgba(98,139,255,0.45) 0%, rgba(255,255,255,0.08) 35%, transparent 68%);
}

.mock-screen {
    position: absolute;
    left: 50%;
    bottom: 32px;
    transform: translateX(-50%);
    width: min(78%, 520px);
    height: 320px;
    border-radius: 28px;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.9), rgba(255,255,255,0.55)),
        linear-gradient(135deg, #d9e6ff 0%, #ecf2ff 55%, #f8fbff 100%);
    box-shadow: 0 18px 50px rgba(0,0,0,0.10);
    border: 1px solid rgba(255,255,255,0.75);
}

.dark .mock-screen {
    background:
        linear-gradient(180deg, rgba(34,37,45,0.95), rgba(19,20,24,0.88)),
        linear-gradient(135deg, #31415f 0%, #15171d 100%);
    border-color: rgba(255,255,255,0.08);
}

.mock-bar {
    position: absolute;
    left: 24px;
    right: 24px;
    top: 22px;
    height: 18px;
    border-radius: 999px;
    background: rgba(0,0,0,0.08);
}

.dark .mock-bar {
    background: rgba(255,255,255,0.08);
}

.mock-chip {
    position: absolute;
    left: 24px;
    top: 62px;
    width: 120px;
    height: 88px;
    border-radius: 20px;
    background: rgba(0,113,227,0.12);
}

.mock-chip2 {
    position: absolute;
    right: 24px;
    top: 62px;
    width: 180px;
    height: 88px;
    border-radius: 20px;
    background: rgba(0,0,0,0.06);
}

.dark .mock-chip,
.dark .mock-chip2 {
    background: rgba(255,255,255,0.08);
}

.mock-footer {
    position: absolute;
    left: 24px;
    right: 24px;
    bottom: 24px;
    height: 110px;
    border-radius: 20px;
    background: rgba(0,0,0,0.06);
}

.dark .mock-footer {
    background: rgba(255,255,255,0.07);
}

.notice {
    max-width: 980px;
    margin: 0 auto;
    padding: 26px 22px 44px;
    color: var(--sub);
    font-size: 12px;
    line-height: 1.55;
}

@media (max-width: 1068px) {
    .grid-2 {
        grid-template-columns: 1fr;
    }

    .hero-visual {
        height: 440px;
    }

    .phone {
        width: 180px;
        height: 360px;
        border-radius: 30px;
    }

    .phone::before {
        border-radius: 22px;
    }

    .phone.left { left: 14%; }
    .phone.right { right: 14%; }

    .card {
        min-height: 620px;
        padding: 42px 28px;
    }

    .local-nav {
        height: auto;
        padding: 10px 0;
    }

    .local-nav-inner {
        height: auto;
        align-items: flex-start;
        gap: 10px;
        flex-direction: column;
    }

    .local-links {
        justify-content: flex-start;
    }
}

@media (max-width: 734px) {
    .global-nav-inner {
        justify-content: center;
        gap: 10px;
    }

    .global-nav-left a:not(:first-child),
    .global-nav-right a {
        display: none;
    }

    .hero-inner {
        padding-top: 56px;
    }

    .hero-title {
        font-size: clamp(40px, 14vw, 72px);
    }

    .hero-visual {
        height: 320px;
        border-radius: 28px;
    }

    .phone {
        width: 120px;
        height: 250px;
        border-radius: 22px;
    }

    .phone::before {
        inset: 6px;
        border-radius: 16px;
    }

    .phone::after {
        width: 58px;
        height: 14px;
        top: 10px;
    }

    .card {
        min-height: 540px;
    }

    .card-desc {
        font-size: 18px;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="global-nav">
    <div class="global-nav-inner">
        <div class="global-nav-left">
            <a href="#"><span class="apple"></span></a>
            <a href="#">스토어</a>
            <a href="#">Mac</a>
            <a href="#">iPad</a>
            <a href="#"><strong>iPhone</strong></a>
            <a href="#">Watch</a>
            <a href="#">AirPods</a>
            <a href="#">TV 및 홈</a>
            <a href="#">액세서리</a>
            <a href="#">고객지원</a>
        </div>
        <div class="global-nav-right">
            <a href="#">검색</a>
            <a href="#">장바구니</a>
        </div>
    </div>
</div>

<div class="local-nav">
    <div class="local-nav-inner">
        <div class="local-title">iPhone</div>
        <div class="local-links">
            <a href="#">iPhone 17 Pro</a>
            <a href="#">iPhone Air</a>
            <a href="#">iPhone 17</a>
            <a href="#">iPhone 17e</a>
            <a href="#">iPhone 16</a>
            <a href="#">비교하기</a>
            <a href="#">액세서리</a>
            <a href="#" class="buy-btn">쇼핑하기</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-inner">
        <div class="hero-eyebrow">iPhone</div>
        <h1 class="hero-title">그야말로 iPhone.</h1>
        <div class="hero-sub">강력함. 매끄러움. 그리고 놀랍도록 직관적인 경험.</div>
        <div class="hero-links">
            <a href="#">더 알아보기</a>
            <a href="#">쇼핑하기</a>
        </div>

        <div class="hero-visual">
            <div class="phone left"></div>
            <div class="phone center"></div>
            <div class="phone right"></div>
        </div>
        <div class="hero-caption">현재 Apple KR iPhone 랜딩 페이지의 대형 히어로 구조를 참고한 재구성 버전</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section section-tight">
    <div class="grid-wrap">
        <div class="grid-2">

            <div class="card light">
                <div class="card-kicker">시작하기</div>
                <div class="card-title">안드로이드에서 iPhone으로 갈아타기, 정말 간단합니다.</div>
                <div class="card-desc">
                    데이터 이전, 메시지 적응, 기본 사용 흐름까지.
                    복잡한 설명 대신 빠르고 부드러운 전환 경험에 초점을 둔 카드입니다.
                </div>
                <a class="card-link" href="#">자세히 보기</a>
                <div class="mock-screen">
                    <div class="mock-bar"></div>
                    <div class="mock-chip"></div>
                    <div class="mock-chip2"></div>
                    <div class="mock-footer"></div>
                </div>
                <div class="visual-ring"></div>
            </div>

            <div class="card dark">
                <div class="card-kicker">견고함을 위한 디자인</div>
                <div class="card-title">오랜 시간 그 가치를 유지하는 iPhone.</div>
                <div class="card-desc">
                    내구성, 긴 소프트웨어 지원, 빠른 칩 성능이라는 메시지를
                    Apple식 대형 타이포와 어두운 배경 카드 구성으로 재해석했습니다.
                </div>
                <a class="card-link" href="#">자세히 보기</a>
                <div class="mock-screen">
                    <div class="mock-bar"></div>
                    <div class="mock-chip"></div>
                    <div class="mock-chip2"></div>
                    <div class="mock-footer"></div>
                </div>
                <div class="visual-ring"></div>
            </div>

            <div class="card blue">
                <div class="card-kicker">iOS 및 Apple Intelligence</div>
                <div class="card-title">변화는 대대적. 경험은 더욱 환상적.</div>
                <div class="card-desc">
                    Liquid Glass, 개인화, 생산성 기능, 기기 내 AI 경험 같은
                    현재 페이지의 핵심 메시지를 반영한 레이아웃입니다.
                </div>
                <a class="card-link" href="#">기능 살펴보기</a>
                <div class="mock-screen">
                    <div class="mock-bar"></div>
                    <div class="mock-chip"></div>
                    <div class="mock-chip2"></div>
                    <div class="mock-footer"></div>
                </div>
                <div class="visual-ring"></div>
            </div>

            <div class="card gray">
                <div class="card-kicker">개인정보 보호</div>
                <div class="card-title">당신의 데이터는 당신이 원하는 곳에서만.</div>
                <div class="card-desc">
                    iPhone 페이지 후반부의 프라이버시 메시지 흐름을 반영해,
                    간결한 한 줄 메시지 중심 카드로 구성했습니다.
                </div>
                <a class="card-link" href="#">더 알아보기</a>
                <div class="mock-screen">
                    <div class="mock-bar"></div>
                    <div class="mock-chip"></div>
                    <div class="mock-chip2"></div>
                    <div class="mock-footer"></div>
                </div>
                <div class="visual-ring"></div>
            </div>

        </div>
    </div>
</div>

<div class="notice">
    이 페이지는 Apple KR iPhone 페이지의 현재 정보 구조와 섹션 흐름을 참고해 만든
    비공식 스타일 데모입니다. 실제 Apple 이미지, 원문 문구, 제품 사진, 인터랙션 자산은 포함하지 않았습니다.
</div>
""", unsafe_allow_html=True)