"""Streamlit launcher — serves original HTML pages via FastAPI backend."""
from __future__ import annotations

import os
import socket
import threading
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="플레이리스트로 순열 살펴보기",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── FastAPI background server ─────────────────────────────────────────────────

API_PORT = 8502


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def _get_local_ip() -> str:
    """LAN에서 접속할 수 있는 실제 IP 주소를 반환합니다."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _start_api(port: int) -> None:
    import uvicorn
    from api import app as api_app
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="error")


if "api_server_started" not in st.session_state:
    if not _port_in_use(API_PORT):
        t = threading.Thread(target=_start_api, args=(API_PORT,), daemon=True)
        t.start()
        for _ in range(30):          # 최대 3초 대기
            if _port_in_use(API_PORT):
                break
            time.sleep(0.1)
    st.session_state["api_server_started"] = True

# ── API base URL: Python이 직접 주입 (srcdoc iframe은 parent.location 접근 불가) ──
# 환경변수 API_HOST가 있으면 우선 사용 (Streamlit Cloud 등 외부 배포용)
_api_host = os.environ.get("API_HOST", _get_local_ip())
API_BASE = f"http://{_api_host}:{API_PORT}"

# ── Bridge script: replaces google.script.run with fetch() ───────────────────

BRIDGE_SCRIPT = f"""
<script>
/* ════ Google Apps Script → FastAPI Bridge ════ */
(function () {{
  /* API_BASE는 Python이 서버 IP를 직접 주입 — srcdoc iframe 제약 우회 */
  var API_BASE = '{API_BASE}';

  function _post(path, body) {{
    return fetch(API_BASE + path, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(body)
    }}).then(function(r) {{ return r.json(); }});
  }}
  function _get(path) {{
    return fetch(API_BASE + path).then(function(r) {{ return r.json(); }});
  }}

  var ENDPOINTS = {{
    upsertSession: function(sid, data) {{
      return _post('/api/upsertSession', Object.assign({{}}, data, {{ sessionId: sid }}));
    }},
    getSubmissions: function() {{ return _get('/api/getSubmissions'); }},
    deleteSession: function(sid) {{ return _post('/api/deleteSession', {{ sessionId: sid }}); }},
    getSavedSessionByIdentity: function(name, cls, group, members) {{
      return _post('/api/getSavedSessionByIdentity', {{ name:name, cls:cls, group:group, members:members }});
    }},
    getProblemBoard: function(classCode) {{
      return _get('/api/getProblemBoard?classCode=' + encodeURIComponent(classCode || ''));
    }},
    checkTeacherPassword: function(pw) {{
      return _post('/api/checkTeacherPassword', {{ pw: pw }});
    }}
  }};

  function Builder() {{
    this._s = null;
    this._f = function(e) {{ console.error('[Bridge]', e); }};
  }}
  Builder.prototype.withSuccessHandler = function(fn) {{ this._s = fn; return this; }};
  Builder.prototype.withFailureHandler = function(fn) {{ this._f = fn; return this; }};
  Object.keys(ENDPOINTS).forEach(function(m) {{
    Builder.prototype[m] = function() {{
      var args = Array.prototype.slice.call(arguments);
      var s = this._s, f = this._f;
      ENDPOINTS[m].apply(null, args)
        .then(function(d) {{ if (s) s(d); }})
        .catch(function(e) {{ if (f) f(e); }});
    }};
  }});

  window.google = {{
    script: {{
      run: {{
        withSuccessHandler: function(fn) {{ return (new Builder()).withSuccessHandler(fn); }},
        withFailureHandler: function(fn) {{ return (new Builder()).withFailureHandler(fn); }}
      }}
    }}
  }};

  /* ── Teacher page navigation helper ── */
  /* srcdoc iframe에서 parent.location 접근이 막히므로 API_BASE의 호스트를 활용 */
  window.__navigateParent = function(url) {{
    /* url 예: "?page=teacher" */
    var query = url.replace(/^[^?]*/, '');   /* "?page=teacher" */
    /* API_BASE에서 호스트+포트 추출 → Streamlit 포트(8501)로 변환 */
    var apiUrl  = new URL(API_BASE);
    var stBase  = apiUrl.protocol + '//' + apiUrl.hostname + ':8501';
    var target  = stBase + '/' + query;
    try {{
      (window.parent || window).location.href = target;
    }} catch(e) {{
      window.location.href = target;
    }}
  }};

  /* ── Full-screen iframe ── */
  /* iframe을 뷰포트 전체로 확장하고 Streamlit 크롬을 숨깁니다 */
  function _makeFullscreen() {{
    try {{
      var f = window.frameElement;
      if (!f) return;
      /* scrolling 속성 제거 → 브라우저 기본(auto) 스크롤 허용 */
      f.removeAttribute('scrolling');
      f.style.cssText = [
        'position:fixed', 'top:0', 'left:0',
        'width:100vw', 'height:100vh',
        'z-index:2147483647', 'border:none',
        'margin:0', 'padding:0', 'display:block',
        'overflow:auto'
      ].join('!important;') + '!important';
      /* 부모 페이지의 Streamlit 요소 숨기기 */
      try {{
        var pdoc = window.parent.document;
        if (!pdoc.getElementById('_st_hide')) {{
          var s = pdoc.createElement('style');
          s.id = '_st_hide';
          s.textContent = [
            '#MainMenu', 'footer', 'header',
            '[data-testid="stToolbar"]',
            '[data-testid="stDecoration"]',
            '[data-testid="collapsedControl"]',
            'section[data-testid="stSidebar"]',
            '[data-testid="stStatusWidget"]'
          ].join(',') + '{{display:none!important}}' +
          'html,body{{overflow:hidden!important;margin:0!important;padding:0!important}}';
          pdoc.head.appendChild(s);
        }}
      }} catch(e2) {{}}
    }} catch(e) {{}}
  }}
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', _makeFullscreen);
  }} else {{
    _makeFullscreen();
  }}
}})();
/* ════ End Bridge ════ */
</script>
"""

# ── Hide all Streamlit chrome so only the iframe is visible ──────────────────

HIDE_CSS = """
<style>
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }
iframe { display: block; }
</style>
"""

# iframe 내부 스크롤 보장 CSS — _patch_student에서 <head>에 주입
SCROLL_FIX_CSS = """
<style>
/* iframe 안에서 세로 스크롤이 되도록 보장 */
html { height: 100%; overflow-y: auto !important; }
body { min-height: 100%; overflow-y: visible !important; }
</style>
"""

# ── Animated background blobs ────────────────────────────────────────────────

ANIMATED_BG = """
<style>
/* ── 일렁이는 액체 그라디언트 배경 ── */
.bg-blobs {
  position: fixed; inset: 0;
  z-index: 0; pointer-events: none; overflow: hidden;
}
.blob {
  position: absolute; border-radius: 50%;
  filter: blur(72px);
  animation: blobDrift ease-in-out infinite;
  will-change: transform;
}
.blob-1 {
  width: 62vw; height: 62vw; opacity: .60;
  background: radial-gradient(circle, rgba(169,207,224,.90), rgba(169,207,224,0) 70%);
  top: -18%; left: -8%;
  animation-duration: 14s; animation-delay: 0s;
}
.blob-2 {
  width: 55vw; height: 55vw; opacity: .55;
  background: radial-gradient(circle, rgba(181,196,177,.85), rgba(181,196,177,0) 70%);
  top: 2%; right: -12%;
  animation-duration: 18s; animation-delay: -5s;
}
.blob-3 {
  width: 50vw; height: 58vw; opacity: .50;
  background: radial-gradient(circle, rgba(127,184,212,.80), rgba(127,184,212,0) 70%);
  bottom: -12%; left: -6%;
  animation-duration: 22s; animation-delay: -9s;
}
.blob-4 {
  width: 58vw; height: 48vw; opacity: .48;
  background: radial-gradient(circle, rgba(181,196,177,.75), rgba(181,196,177,0) 70%);
  bottom: -8%; right: -12%;
  animation-duration: 17s; animation-delay: -13s;
}
.blob-5 {
  width: 38vw; height: 38vw; opacity: .38;
  background: radial-gradient(circle, rgba(169,207,224,.70), rgba(169,207,224,0) 70%);
  top: 38%; left: 28%;
  animation-duration: 25s; animation-delay: -7s;
}

@keyframes blobDrift {
  0%   { transform: translate(0,    0)    scale(1);    }
  15%  { transform: translate(7vw,  5vh)  scale(1.06); }
  30%  { transform: translate(3vw,  11vh) scale(0.95); }
  45%  { transform: translate(11vw, 3vh)  scale(1.08); }
  60%  { transform: translate(5vw,  14vh) scale(0.93); }
  75%  { transform: translate(9vw,  6vh)  scale(1.04); }
  90%  { transform: translate(2vw,  9vh)  scale(0.98); }
  100% { transform: translate(0,    0)    scale(1);    }
}
</style>
<div class="bg-blobs" aria-hidden="true">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>
  <div class="blob blob-4"></div>
  <div class="blob blob-5"></div>
</div>
"""

# ── HTML patchers ─────────────────────────────────────────────────────────────

import re as _re


def _remove_teacher_elements(html: str) -> str:
    """교사용 대시보드 관련 HTML/JS를 모두 제거합니다. student.html 파일은 건드리지 않습니다."""

    # 1) 스플래시 화면 교사 버튼
    html = _re.sub(
        r'<button[^>]*class="splash-teacher"[^>]*>.*?</button>',
        "", html, flags=_re.DOTALL
    )

    # 2) 비밀번호 모달 전체 (pw-overlay div + 자식 요소)
    html = _re.sub(
        r'<div[^>]*id="pw-overlay"[^>]*>.*?</div>\s*</div>',
        "", html, flags=_re.DOTALL
    )

    # 3) 교사 관련 JS 함수 블록 (openPwModal / closePwModal / checkPw)
    html = _re.sub(
        r'/\* ════ 교사 비번 ════ \*/.*?\.checkTeacherPassword\(input\);[\s\n]*\}',
        "", html, flags=_re.DOTALL
    )

    # 4) window 전역 노출에서 교사 함수 참조 제거
    for ref in ["window.openPwModal=openPwModal", "window.closePwModal=closePwModal", "window.checkPw=checkPw"]:
        html = html.replace(" " + ref + ";", "")
        html = html.replace(ref + ";", "")

    return html


# ── Step 5: 다른 조 문제 칸 → 우리 조 문제 표시로 교체 ────────────────────────

# 교체할 대상 블록 (peer problems container)
_PEER_BLOCK = (
    '    <div style="background:var(--md-surface-var);border:1.5px solid var(--md-outline);'
    'border-radius:var(--r-md);padding:18px;margin-bottom:18px;">\n'
    '      <div style="display:flex;align-items:center;justify-content:space-between;'
    'gap:10px;margin-bottom:12px;">\n'
    '        <div style="font-size:.88rem;font-weight:800;color:var(--md-primary);">🧩 다른 조가 만든 문제</div>\n'
    '        <button type="button" class="btn btn-s" style="padding:8px 14px;font-size:.78rem;'
    'min-height:36px;" onclick="loadPeerProblems()">새로고침</button>\n'
    '      </div>\n'
    '      <div id="peer-problems-status" style="font-size:.78rem;color:var(--md-on-surface-v);'
    'line-height:1.6;margin-bottom:10px;">문제 목록을 불러오는 중입니다.</div>\n'
    '      <div id="peer-problems-list" style="display:grid;gap:10px;"></div>\n'
    '    </div>'
)

# 교체될 내용: 우리 조 문제 표시 카드만 (스크립트는 </body> 직전에 주입)
_MY_PROB_HTML = '''    <div style="background:var(--md-primary-cont);border:1.5px solid rgba(58,139,175,.3);border-radius:var(--r-md);padding:18px;margin-bottom:18px;">
      <div style="font-size:.88rem;font-weight:800;color:var(--md-primary);margin-bottom:14px;">📋 우리 조가 만든 문제 (STEP 4)</div>
      <div id="my-problem-display">
        <div style="font-size:.82rem;color:var(--md-on-surface-v);font-style:italic;">Step 4에서 문제를 작성하면 여기에 표시됩니다.</div>
      </div>
    </div>'''

# 오버라이드 스크립트는 </body> 직전에 주입 → 원본 스크립트보다 나중에 실행되어 덮어씌워지지 않음
_MY_PROB_SCRIPT = '''<script>
/* ════ Step 5: 우리 조 문제 표시 (원본 스크립트 이후 실행) ════ */
function _showMyProblem() {
  var display = document.getElementById('my-problem-display');
  if (!display) return;
  var stmt    = (document.getElementById('s-prob-statement') || {}).value || '';
  var formula = (document.getElementById('s-prob-formula')   || {}).value || '';
  var explain = (document.getElementById('s-prob-explain')   || {}).value || '';
  var probConds = ['pc1','pc2','pc3','pc4','pc5','pc6']
    .filter(function(id){ var el=document.getElementById(id); return el && el.checked; })
    .map(function(id){ var el=document.getElementById(id); return el ? el.value : ''; })
    .join(' + ');
  if (!stmt.trim()) {
    display.innerHTML = '<div style="font-size:.82rem;color:var(--md-on-surface-v);font-style:italic;">Step 4에서 문제를 작성하면 여기에 표시됩니다.</div>';
    return;
  }
  function _e(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  display.innerHTML =
    (probConds ? '<div style="font-size:.72rem;font-weight:700;color:var(--md-on-surface-v);margin-bottom:8px;">선택 조건: ' + _e(probConds) + '</div>' : '') +
    '<div style="font-size:.95rem;font-weight:700;line-height:1.75;white-space:pre-wrap;color:var(--md-on-surface);margin-bottom:12px;padding:12px 14px;background:rgba(255,255,255,.55);border-radius:12px;border:1px solid rgba(255,255,255,.65);">' + _e(stmt) + '</div>' +
    (formula ? '<div style="font-size:.72rem;font-weight:700;color:var(--md-on-surface-v);margin-bottom:4px;">경우의 수를 구하는 식</div><div style="font-size:.88rem;margin-bottom:12px;padding:8px 12px;background:rgba(255,255,255,.45);border-radius:10px;">' + _e(formula) + '</div>' : '') +
    (explain  ? '<div style="font-size:.72rem;font-weight:700;color:var(--md-on-surface-v);margin-bottom:4px;">풀이 과정 및 이유</div><div style="font-size:.85rem;white-space:pre-wrap;padding:8px 12px;background:rgba(255,255,255,.45);border-radius:10px;">' + _e(explain) + '</div>' : '');
}
/* 원본 함수 재정의 — 이 스크립트가 마지막에 실행되므로 확실히 override됨 */
startPeerProblemPolling = function(){ _showMyProblem(); };
stopPeerProblemPolling  = function(){};
loadPeerProblems        = function(){ _showMyProblem(); };

/* ── 제출 버튼 텍스트 변경 ── */
(function() {
  var btn = document.getElementById('sub-btn');
  if (btn) btn.textContent = '🎓 오늘의 학습 끝내기';
})();

/* ── submitAll 재정의: API 없이 즉시 완료 화면 표시 ── */
submitAll = function() {
  var allChk = ['chk1','chk2','chk3','chk4','chk5'].every(function(id) {
    var el = document.getElementById(id);
    return el && el.checked;
  });
  if (!allChk) { showToast('자기 점검 항목을 모두 확인하세요.'); return; }

  /* 버튼 숨기고 완료 카드 표시 */
  var btn = document.getElementById('sub-btn');
  if (btn) btn.style.display = 'none';
  var okCard = document.getElementById('ok-card');
  if (okCard) okCard.style.display = 'block';
  showToast('🎵 오늘 수업도 수고했어요!');
};
</script>
'''


def _patch_student(html: str) -> str:
    # 1) API 브리지 + 스크롤 보장 CSS 주입
    html = html.replace("<head>", "<head>\n" + BRIDGE_SCRIPT + SCROLL_FIX_CSS, 1)
    # 2) 일렁이는 배경 애니메이션 주입
    html = html.replace("<body>", "<body>\n" + ANIMATED_BG, 1)
    # 3) 교사용 대시보드 요소 완전 제거
    html = _remove_teacher_elements(html)
    # 4) Step 5: 다른 조 문제 칸 → 우리 조 문제 표시 카드로 교체
    html = html.replace(_PEER_BLOCK, _MY_PROB_HTML, 1)
    # 5) override 스크립트를 </body> 직전에 주입 (원본 스크립트보다 나중에 실행)
    html = html.replace("</body>", _MY_PROB_SCRIPT + "</body>", 1)
    return html


# ── Load HTML ─────────────────────────────────────────────────────────────────

LEGACY = Path(__file__).parent / "legacy_apps_script"


def _load(filename: str, patcher) -> str:
    path = LEGACY / filename
    if not path.exists():
        st.error(f"파일을 찾을 수 없습니다: {path}")
        st.stop()
    return patcher(path.read_text(encoding="utf-8"))


# ── Render (교사용 대시보드 제거 — 학생 페이지만 서빙) ──────────────────────────

st.markdown(HIDE_CSS, unsafe_allow_html=True)

html = _load("student.html", _patch_student)

# height=1 → DOM 흐름에서는 1px만 차지
# iframe 내부 JS가 position:fixed로 확장해 뷰포트 전체를 덮음
components.html(html, height=800, scrolling=True)
