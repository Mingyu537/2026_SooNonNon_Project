"""Streamlit launcher — serves original HTML pages via FastAPI backend."""
from __future__ import annotations

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


def _start_api(port: int) -> None:
    import uvicorn
    from api import app as api_app
    uvicorn.run(api_app, host="0.0.0.0", port=port, log_level="error")


if "api_server_started" not in st.session_state:
    if not _port_in_use(API_PORT):
        t = threading.Thread(target=_start_api, args=(API_PORT,), daemon=True)
        t.start()
        for _ in range(20):
            if _port_in_use(API_PORT):
                break
            time.sleep(0.1)
    st.session_state["api_server_started"] = True

# ── Bridge script: replaces google.script.run with fetch() ───────────────────

BRIDGE_SCRIPT = f"""
<script>
/* ════ Google Apps Script → FastAPI Bridge ════ */
(function () {{
  var _port = '{API_PORT}';
  var _host = 'localhost';
  try {{ _host = (window.parent || window).location.hostname || 'localhost'; }} catch(e) {{}}
  var API_BASE = (window.parent || window).location.protocol + '//' + _host + ':' + _port;

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
  window.__navigateParent = function(url) {{
    try {{
      var base = (window.parent || window).location.href.split('?')[0];
      (window.parent || window).location.href = base + '?' + url.replace(/^.*\?/, '');
    }} catch(e) {{ window.location.href = url; }}
  }};

  /* ── Full-screen iframe ── */
  /* iframe을 뷰포트 전체로 확장하고 Streamlit 크롬을 숨깁니다 */
  function _makeFullscreen() {{
    try {{
      var f = window.frameElement;
      if (!f) return;
      f.style.cssText = [
        'position:fixed', 'top:0', 'left:0',
        'width:100vw', 'height:100vh',
        'z-index:2147483647', 'border:none',
        'margin:0', 'padding:0', 'display:block'
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

def _patch_student(html: str) -> str:
    html = html.replace("<head>", "<head>\n" + BRIDGE_SCRIPT, 1)
    # Inject animated background blobs right after <body>
    html = html.replace("<body>", "<body>\n" + ANIMATED_BG, 1)
    # Fix teacher redirect: navigate parent instead of iframe
    html = html.replace(
        "window.location.replace(result.url);",
        "window.__navigateParent(result.url);",
    )
    return html


def _patch_teacher(html: str) -> str:
    html = html.replace("<head>", "<head>\n" + BRIDGE_SCRIPT, 1)
    html = html.replace("<body>", "<body>\n" + ANIMATED_BG, 1)
    return html


# ── Load HTML ─────────────────────────────────────────────────────────────────

LEGACY = Path(__file__).parent / "legacy_apps_script"


def _load(filename: str, patcher) -> str:
    path = LEGACY / filename
    if not path.exists():
        st.error(f"파일을 찾을 수 없습니다: {path}")
        st.stop()
    return patcher(path.read_text(encoding="utf-8"))


# ── Page routing ──────────────────────────────────────────────────────────────

def _get_page() -> str:
    try:
        return str(st.query_params.get("page", "student"))
    except Exception:
        params = st.experimental_get_query_params()  # type: ignore[attr-defined]
        return (params.get("page", ["student"]) or ["student"])[0]


# ── Render ────────────────────────────────────────────────────────────────────

st.markdown(HIDE_CSS, unsafe_allow_html=True)

page = _get_page()

if page == "teacher":
    html = _load("teacher.html", _patch_teacher)
else:
    html = _load("student.html", _patch_student)

# height=1 → DOM 흐름에서는 1px만 차지
# iframe 내부 JS가 position:fixed로 확장해 뷰포트 전체를 덮음
components.html(html, height=1, scrolling=False)
