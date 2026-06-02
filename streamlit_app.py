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

# ── HTML patchers ─────────────────────────────────────────────────────────────

def _patch_student(html: str) -> str:
    html = html.replace("<head>", "<head>\n" + BRIDGE_SCRIPT, 1)
    # Fix teacher redirect: navigate parent instead of iframe
    html = html.replace(
        "window.location.replace(result.url);",
        "window.__navigateParent(result.url);",
    )
    return html


def _patch_teacher(html: str) -> str:
    html = html.replace("<head>", "<head>\n" + BRIDGE_SCRIPT, 1)
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

# height=900 + scrolling=True → iframe fills viewport and scrolls internally
# (the original HTML already has position:sticky header + scrollable content)
components.html(html, height=900, scrolling=True)
