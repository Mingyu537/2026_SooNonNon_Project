"""Streamlit 진입점 — 배포된 Apps Script 웹앱을 전체화면 iframe으로 표시.

Apps Script 웹앱이 학생/교사 페이지를 모두 서빙하고 Google Sheets에
실시간 저장한다. Apps Script는 XFrameOptionsMode.ALLOWALL이라 iframe 가능.
?page=teacher 쿼리도 그대로 전달한다.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

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


# ── 대상 URL (?page=teacher 등 쿼리 전달) ─────────────────────────────────────
target = _webapp_url()
try:
    page = st.query_params.get("page", "")
    if page:
        target = f"{target}?page={page}"
except Exception:
    pass

# ── Streamlit 크롬 전부 숨기기 ────────────────────────────────────────────────
st.markdown(
    """
    <style>
    #MainMenu, footer, header,
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="collapsedControl"], section[data-testid="stSidebar"],
    [data-testid="stStatusWidget"] { display: none !important; }
    .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    html, body { overflow: hidden !important; margin: 0 !important; padding: 0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Apps Script 웹앱을 전체화면 iframe으로 삽입 ──────────────────────────────
# 내부 JS가 자신의 iframe(window.frameElement)을 뷰포트 전체로 확장한다.
components.html(
    f"""
    <iframe id="app-frame" src="{target}"
            style="border:none;width:100%;height:100vh;display:block;"
            allow="clipboard-read; clipboard-write"></iframe>
    <script>
      (function() {{
        function fill() {{
          try {{
            var f = window.frameElement;   /* Streamlit이 만든 바깥 iframe */
            if (f) {{
              f.style.cssText = [
                'position:fixed','top:0','left:0',
                'width:100vw','height:100vh',
                'border:none','margin:0','padding:0',
                'z-index:2147483647','display:block'
              ].join('!important;') + '!important';
            }}
          }} catch(e) {{}}
          /* 내부 iframe도 뷰포트 전체 */
          var inner = document.getElementById('app-frame');
          if (inner) inner.style.height = '100vh';
        }}
        fill();
        window.addEventListener('resize', fill);
      }})();
    </script>
    """,
    height=900,
    scrolling=False,
)
