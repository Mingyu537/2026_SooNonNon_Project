"""Streamlit 진입점 — 배포된 Apps Script 웹앱으로 리다이렉트.

Apps Script 웹앱이 이미 학생/교사 페이지를 모두 서빙하고
Google Sheets에 실시간 저장하므로, Streamlit은 그 URL로 넘겨주기만 한다.
?page=teacher 쿼리도 그대로 전달한다.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="플레이리스트로 순열 살펴보기",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _webapp_url() -> str:
    """secrets에 SHEETS_WEBAPP_URL이 있으면 사용, 없으면 기본값."""
    try:
        u = st.secrets.get("SHEETS_WEBAPP_URL", "")
        if u:
            return str(u)
    except Exception:
        pass
    return (
        "https://script.google.com/macros/s/"
        "AKfycbwlqctZCDXvqps6q5yJb2Nv_u3p_iATy3Vawv8Bn2V54j-zMeLkk8qgk5-cqzG5IScIXw"
        "/exec"
    )


# ── 쿼리 파라미터 전달 (?page=teacher 등) ─────────────────────────────────────
target = _webapp_url()
try:
    page = st.query_params.get("page", "")
    if page:
        target = f"{target}?page={page}"
except Exception:
    pass

# ── Streamlit 크롬 숨기기 ─────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    #MainMenu, footer, header,
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="collapsedControl"], section[data-testid="stSidebar"]
    { display: none !important; }
    .block-container { padding: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 최상위 창을 Apps Script 웹앱으로 이동 ────────────────────────────────────
st.markdown(
    f"""
    <div style="font-family:'Noto Sans KR',sans-serif;text-align:center;padding:60px 20px;color:#3D4A44;">
      <div style="font-size:2.4rem;margin-bottom:16px;">🎵</div>
      <div style="font-size:1.05rem;font-weight:700;margin-bottom:8px;">플레이리스트로 순열 살펴보기</div>
      <div style="font-size:.85rem;color:#6E9170;">활동 페이지로 이동 중입니다…</div>
      <div style="margin-top:18px;font-size:.8rem;">
        자동으로 넘어가지 않으면
        <a href="{target}" target="_top" style="color:#3A8BAF;font-weight:700;">여기를 눌러주세요</a>.
      </div>
    </div>
    <script>
      /* 부모(최상위) 창 전체를 Apps Script 웹앱으로 이동 */
      window.top.location.href = "{target}";
    </script>
    """,
    unsafe_allow_html=True,
)
