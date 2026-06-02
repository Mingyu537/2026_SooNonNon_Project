from __future__ import annotations

import csv
import html
import io
import json
import os
import time
import uuid
from datetime import datetime
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from constants import (
    BLANK_FIELDS,
    CHECK_ITEMS,
    CLASSES,
    COND_GROUPS,
    COND_META,
    COND_NUMS,
    DEFAULT_TEACHER_PASSWORD,
    GENRES,
    GROUP_ORDER,
    GROUPS,
    LABELS,
    PROBLEM_CONDITIONS,
    STEP_LABELS,
    WORD_ITEMS,
)
from storage import (
    delete_session,
    get_problem_board,
    get_saved_session_by_identity,
    get_submissions,
    normalize_class_code,
    normalize_group_name,
    upsert_session,
)


st.set_page_config(
    page_title="플레이리스트로 순열 살펴보기",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS ──────────────────────────────────────────────────────────────────────

def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');

        :root {
          --isa:  #F3F3F3;
          --lb:   #5FA8C8;
          --lb2:  #3A8BAF;
          --fg:   #3D4A44;
          --fg2:  #1E2822;
          --cream:#F0EAE0;
          --sage: #6E9170;
          --sage2:#4A7050;
          --md-primary:       var(--lb2);
          --md-primary-cont:  rgba(58,139,175,.18);
          --md-success:       #2E6B42;
          --md-success-cont:  rgba(46,107,66,.16);
          --md-warning:       #7A5E1A;
          --md-warning-cont:  rgba(122,94,26,.14);
          --md-error:         #7A2A2A;
          --md-on-surface:    #1A211D;
          --md-on-surface-v:  #3D4A44;
          --glass-bg:         rgba(248,246,242,.78);
          --glass-bg-s:       rgba(244,240,232,.88);
          --glass-border:     rgba(255,255,255,.75);
          --shadow-sm: 0 2px 10px rgba(30,40,34,.14);
          --shadow-md: 0 6px 24px rgba(30,40,34,.18);
          --shadow-lg: 0 14px 44px rgba(30,40,34,.22);
          --r-sm:12px; --r-md:18px; --r-lg:22px; --r-xl:32px;
          --ease:cubic-bezier(.4,0,.2,1);
        }

        html, body, [class*="css"] {
          font-family: "Noto Sans KR", sans-serif !important;
        }

        /* Hide Streamlit chrome */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        section[data-testid="stSidebar"] { display: none; }
        [data-testid="stDecoration"] { display: none; }

        .stApp {
          background:
            radial-gradient(ellipse 75% 60% at 8%   0%,  rgba(169,207,224,.55) 0%, transparent 55%),
            radial-gradient(ellipse 65% 55% at 92%  8%,  rgba(181,196,177,.50) 0%, transparent 50%),
            radial-gradient(ellipse 60% 70% at 2%   65%, rgba(127,184,212,.38) 0%, transparent 55%),
            radial-gradient(ellipse 70% 55% at 92%  80%, rgba(181,196,177,.42) 0%, transparent 50%),
            radial-gradient(ellipse 85% 50% at 50% 110%, rgba(169,207,224,.30) 0%, transparent 55%),
            linear-gradient(160deg,#F0EAE0 0%,#EEE9E0 40%,#ECF3F5 75%,#F0EAE0 100%);
          color: var(--md-on-surface);
        }

        .block-container {
          max-width: 1120px !important;
          padding-top: 0 !important;
          padding-bottom: 4rem !important;
          padding-left: clamp(16px, 3vw, 48px) !important;
          padding-right: clamp(16px, 3vw, 48px) !important;
        }

        /* ── GLASS CARD ── */
        .card {
          background: var(--glass-bg);
          -webkit-backdrop-filter: saturate(180%) blur(20px);
          backdrop-filter: saturate(180%) blur(20px);
          border: 1px solid var(--glass-border);
          border-radius: var(--r-lg);
          padding: 24px;
          margin-bottom: 14px;
          box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,.72);
        }
        .card.compact { padding: 18px; border-radius: var(--r-md); }

        /* ── EYEBROW ── */
        .eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          font-size: .65rem;
          font-weight: 700;
          background: rgba(169,207,224,.2);
          -webkit-backdrop-filter: blur(6px);
          backdrop-filter: blur(6px);
          border: 1px solid rgba(169,207,224,.35);
          color: var(--lb2);
          letter-spacing: .8px;
          text-transform: uppercase;
          border-radius: 20px;
          padding: 3px 10px;
          margin-bottom: 10px;
        }
        .card-title { font-size: 1.15rem; font-weight: 800; line-height: 1.35; margin-bottom: 5px; color: var(--md-on-surface); }
        .card-desc  { font-size: .83rem; color: var(--md-on-surface-v); line-height: 1.75; }

        /* ── PROGRESS BAR ── */
        .progress-wrap {
          background: var(--glass-bg-s);
          -webkit-backdrop-filter: saturate(160%) blur(12px);
          backdrop-filter: saturate(160%) blur(12px);
          border-bottom: 1px solid var(--glass-border);
          padding: 14px 20px;
          position: sticky; top: 0; z-index: 100;
          box-shadow: 0 4px 16px rgba(96,111,105,.08);
          margin-bottom: 16px;
        }
        .progress-inner { max-width: 1080px; margin: 0 auto; }
        .steps-row { display: flex; align-items: center; }
        .dot {
          width: 30px; height: 30px; border-radius: 50%;
          background: rgba(243,243,243,.5);
          border: 2px solid rgba(255,255,255,.6);
          -webkit-backdrop-filter: blur(6px);
          backdrop-filter: blur(6px);
          display: flex; align-items: center; justify-content: center;
          font-size: .72rem; font-weight: 700; color: var(--fg);
          transition: all .3s var(--ease); flex-shrink: 0;
        }
        .dot.active {
          background: linear-gradient(135deg,var(--lb),var(--sage));
          border-color: rgba(255,255,255,.7); color: #fff;
          box-shadow: 0 0 0 4px rgba(169,207,224,.28), 0 4px 12px rgba(127,184,212,.35);
        }
        .dot.done {
          background: linear-gradient(135deg,var(--sage),var(--lb2));
          border-color: rgba(255,255,255,.6); color: #fff; font-size: 0;
        }
        .dot.done::after { content: "✓"; font-size: .72rem; }
        .prog-line {
          flex: 1; height: 2px;
          background: rgba(96,111,105,.15);
          margin: 0 4px; border-radius: 2px;
          transition: background .3s;
        }
        .prog-line.done { background: linear-gradient(90deg,var(--sage),var(--lb)); }
        .lbl-row { display: flex; justify-content: space-between; margin-top: 6px; }
        .lbl {
          font-size: .58rem; color: var(--fg);
          text-align: center; width: 30px; line-height: 1.35;
        }
        .lbl.active { color: var(--lb2); font-weight: 700; }
        .lbl.done   { color: var(--sage2); }

        /* ── APP HEADER ── */
        .app-header {
          background: var(--glass-bg-s);
          -webkit-backdrop-filter: saturate(160%) blur(12px);
          backdrop-filter: saturate(160%) blur(12px);
          border-bottom: 1px solid var(--glass-border);
          padding: 12px 20px;
          display: flex; align-items: center; justify-content: space-between;
          box-shadow: 0 4px 16px rgba(96,111,105,.07);
          margin-bottom: 0;
        }
        .hdr-icon {
          width: 34px; height: 34px;
          background: linear-gradient(135deg,var(--lb),var(--sage));
          border-radius: var(--r-sm);
          display: flex; align-items: center; justify-content: center;
          font-size: 1rem; flex-shrink: 0;
          box-shadow: 0 2px 8px rgba(127,184,212,.32);
        }
        .hdr-title { font-size: .88rem; font-weight: 700; color: var(--md-on-surface); }
        .hdr-sub   { font-size: .7rem; color: var(--md-on-surface-v); margin-top: 1px; }

        /* ── FORM ELEMENTS ── */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
          background: rgba(255,255,255,.55) !important;
          border: 1.5px solid rgba(255,255,255,.62) !important;
          border-radius: var(--r-sm) !important;
          font-family: "Noto Sans KR", sans-serif !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
          border-color: rgba(127,184,212,.55) !important;
          background: rgba(255,255,255,.78) !important;
          box-shadow: 0 0 0 3px rgba(169,207,224,.22) !important;
        }

        /* ── TIP / WARN BOX ── */
        .tip-box {
          background: rgba(169,207,224,.18);
          -webkit-backdrop-filter: blur(8px);
          backdrop-filter: blur(8px);
          border-left: 3px solid var(--lb2);
          border-radius: 0 var(--r-sm) var(--r-sm) 0;
          border-top: 1px solid rgba(169,207,224,.28);
          border-right: 1px solid rgba(169,207,224,.28);
          border-bottom: 1px solid rgba(169,207,224,.28);
          padding: 12px 14px; font-size: .82rem; color: var(--fg2);
          line-height: 1.75; margin-bottom: 16px;
        }
        .tip-box strong { color: var(--lb2); }
        .warn-box {
          background: rgba(160,132,80,.12);
          border-left: 3px solid var(--md-warning);
          border-radius: 0 var(--r-sm) var(--r-sm) 0;
          border-top: 1px solid rgba(160,132,80,.2);
          border-right: 1px solid rgba(160,132,80,.2);
          border-bottom: 1px solid rgba(160,132,80,.2);
          padding: 12px 14px; font-size: .82rem; color: #6B5420;
          line-height: 1.75; margin-bottom: 16px;
        }

        /* ── MINI CARD ── */
        .mini-card {
          background: rgba(255,255,255,.55);
          -webkit-backdrop-filter: blur(8px);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255,255,255,.65);
          border-radius: var(--r-sm);
          padding: 11px 14px; margin-bottom: 8px;
          font-size: .84rem; line-height: 1.65;
        }

        /* ── SONG CHIP ── */
        .song-chip {
          display: inline-block;
          background: linear-gradient(135deg,var(--lb),var(--sage));
          width: 32px; height: 32px; border-radius: 10px;
          display: inline-flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: .8rem; color: #fff;
          box-shadow: 0 3px 8px rgba(127,184,212,.3);
          flex-shrink: 0; margin-right: 8px;
        }
        .sm-chip {
          display: inline-block;
          background: rgba(169,207,224,.22);
          border: 1px solid rgba(127,184,212,.3);
          border-radius: 6px; padding: 3px 8px;
          font-size: .67rem; font-weight: 500; color: var(--lb2);
          margin: 0 3px 3px 0;
        }

        /* ── STATUS CHIPS ── */
        .status-done {
          display: inline-block;
          background: var(--md-success-cont); color: var(--md-success);
          border-radius: 20px; padding: 3px 9px;
          font-size: .65rem; font-weight: 700; white-space: nowrap;
        }
        .status-progress {
          display: inline-block;
          background: var(--md-warning-cont); color: var(--md-warning);
          border-radius: 20px; padding: 3px 9px;
          font-size: .65rem; font-weight: 700; white-space: nowrap;
        }

        /* ── COND ITEM ── */
        .cond-item {
          padding: 16px 18px;
          border-bottom: 1px solid rgba(255,255,255,.32);
        }
        .cond-item:last-child { border-bottom: none; }
        .cond-num {
          display: inline-flex; align-items: center; justify-content: center;
          width: 24px; height: 24px; border-radius: 50%;
          font-size: .68rem; font-weight: 800; color: #fff;
          margin-right: 6px; flex-shrink: 0; vertical-align: middle;
        }

        /* ── QUESTION TOGGLE BUTTON ── */
        .q-btn {
          display: inline-block;
          border-radius: 999px; padding: 5px 12px;
          font-size: .72rem; font-weight: 800;
          cursor: pointer; border: 1.5px solid;
          transition: all .18s; white-space: nowrap;
        }
        .q-btn.active { color: #fff; }

        /* ── BUTTONS ── */
        .stButton > button {
          font-family: "Noto Sans KR", sans-serif !important;
          font-weight: 700 !important;
          border-radius: 50px !important;
          transition: all .2s !important;
        }
        .stButton > button[kind="primary"] {
          background: linear-gradient(135deg,var(--lb),var(--sage)) !important;
          border: none !important;
          box-shadow: 0 4px 14px rgba(127,184,212,.38) !important;
          color: #fff !important;
        }
        .stButton > button[kind="primary"]:hover {
          transform: translateY(-2px) !important;
          box-shadow: 0 8px 22px rgba(127,184,212,.45) !important;
        }

        /* ── EXPANDER ── */
        .streamlit-expanderHeader {
          background: var(--glass-bg) !important;
          border: 1px solid var(--glass-border) !important;
          border-radius: var(--r-md) !important;
          font-weight: 700 !important;
        }

        /* ── TEACHER CARD ── */
        .sub-card {
          background: var(--glass-bg);
          -webkit-backdrop-filter: saturate(160%) blur(12px);
          backdrop-filter: saturate(160%) blur(12px);
          border: 1px solid var(--glass-border);
          border-radius: var(--r-lg); padding: 18px;
          box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,.6);
          margin-bottom: 12px;
        }
        .sub-card:hover {
          border-color: rgba(127,184,212,.45);
          box-shadow: var(--shadow-md), inset 0 1px 0 rgba(255,255,255,.7);
        }
        .student-name  { font-size: .98rem; font-weight: 800; margin-bottom: 2px; color: var(--md-on-surface); }
        .student-meta  { font-size: .72rem; color: var(--md-on-surface-v); }
        .cond-progress {
          background: rgba(255,255,255,.38);
          border: 1px solid rgba(255,255,255,.5);
          border-radius: 8px; padding: 6px 10px;
          font-size: .75rem; color: var(--md-on-surface-v);
          margin-bottom: 10px;
        }
        .cond-progress strong { color: var(--lb2); }
        .card-time { font-size: .65rem; color: var(--md-on-surface-v); margin-top: 8px; }

        /* ── TEACHER STAT CARD ── */
        .stat-card {
          background: var(--glass-bg);
          border: 1px solid var(--glass-border);
          border-radius: var(--r-md); padding: 16px 18px;
          box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,.65);
        }
        .stat-n { font-size: 2.1rem; font-weight: 900; color: var(--lb2); line-height: 1; margin-bottom: 4px; }
        .stat-l { font-size: .7rem; color: var(--md-on-surface-v); font-weight: 500; }

        /* ── SUCCESS ── */
        .success-wrap { text-align: center; padding: 32px 16px; }
        .success-icon { font-size: 3rem; margin-bottom: 12px; }
        .success-title {
          font-size: 1.3rem; font-weight: 900;
          background: linear-gradient(135deg,var(--lb2),var(--sage2));
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          margin-bottom: 8px;
        }

        /* ── HIDDEN INPUTS (blank sync) ── */
        div[data-testid="stTextInput"]:has(input[aria-label^="blank__"]) { display: none; }

        /* ── SPLASH HEADER ── */
        .splash-overlay {
          display: flex; flex-direction: column;
          align-items: center; justify-content: center;
          text-align: center; padding: 60px 32px 48px;
        }
        .splash-chip {
          background: rgba(255,255,255,.38);
          border: 1px solid rgba(255,255,255,.55);
          -webkit-backdrop-filter: blur(8px);
          backdrop-filter: blur(8px);
          border-radius: 20px; padding: 5px 14px;
          font-size: .72rem; font-weight: 700;
          color: var(--fg2); letter-spacing: .8px;
          text-transform: uppercase; margin-bottom: 28px;
        }
        .splash-title {
          font-size: clamp(2.6rem, 6vw, 3.6rem);
          font-weight: 900; color: var(--fg2);
          line-height: 1.2; letter-spacing: -1.2px;
          margin-bottom: 14px;
          text-shadow: 0 2px 12px rgba(255,255,255,.6);
        }
        .splash-desc {
          font-size: .88rem; color: var(--fg);
          line-height: 1.8; margin-bottom: 20px;
          max-width: 280px;
        }

        /* ── INFO MODAL ── */
        .info-modal {
          background: var(--glass-bg-s);
          -webkit-backdrop-filter: saturate(180%) blur(20px);
          backdrop-filter: saturate(180%) blur(20px);
          border: 1px solid var(--glass-border);
          border-radius: var(--r-xl);
          padding: 32px 28px;
          width: 100%; max-width: 500px;
          box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,.82);
        }

        /* ── SMALL MUTED ── */
        .small-muted { color: var(--fg); font-size: .82rem; line-height: 1.65; }

        /* ── DIVIDER ── */
        .divider { height: 1px; background: rgba(255,255,255,.45); margin: 18px 0; }

        /* ── SONG SIDEBAR ── */
        .song-sidebar-card {
          background: var(--glass-bg);
          -webkit-backdrop-filter: saturate(160%) blur(12px);
          backdrop-filter: saturate(160%) blur(12px);
          border: 1px solid var(--glass-border);
          border-radius: var(--r-md); padding: 16px;
          box-shadow: var(--shadow-sm), inset 0 1px 0 rgba(255,255,255,.6);
          position: sticky; top: 80px;
        }

        @media(max-width:640px) {
          .block-container { padding-left: 14px !important; padding-right: 14px !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Utilities ────────────────────────────────────────────────────────────────

def secret_value(name: str, default: str) -> str:
    try:
        value = st.secrets.get(name, None)
    except Exception:
        value = None
    return str(value or os.environ.get(name, default))


def get_query_page() -> str:
    try:
        return str(st.query_params.get("page", "student"))
    except Exception:
        params = st.experimental_get_query_params()  # type: ignore[attr-defined]
        raw = params.get("page", ["student"])
        return raw[0] if raw else "student"


def set_query_page(page: str) -> None:
    try:
        st.query_params["page"] = page
    except Exception:
        st.experimental_set_query_params(page=page)  # type: ignore[attr-defined]


def ensure_runtime() -> None:
    st.session_state.setdefault("session_id", f"sid_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}")
    st.session_state.setdefault("activity_ready", False)
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("step1_sub", "1a")
    st.session_state.setdefault("submitted_done", False)
    st.session_state.setdefault("teacher_authenticated", False)


def set_key(key: str, value: Any, force: bool = False) -> None:
    if force or key not in st.session_state:
        st.session_state[key] = "" if value is None else value


def text_key(key: str) -> str:
    return str(st.session_state.get(key, "") or "").strip()


def bool_key(key: str) -> bool:
    return bool(st.session_state.get(key, False))


def all_conditions() -> list[dict[str, Any]]:
    return [cond for group in COND_GROUPS for cond in group["conds"]]


def get_cond(cond_id: str) -> dict[str, Any]:
    for cond in all_conditions():
        if cond["id"] == cond_id:
            return cond
    raise KeyError(cond_id)


def default_conditions_data() -> dict[str, Any]:
    return {
        "totalFormula": "",
        "totalExplain": "",
        "groups": {
            group["id"]: [
                {"id": cond["id"], "formula": "", "explain": "", "question": False, "inputs": {}}
                for cond in group["conds"]
            ]
            for group in COND_GROUPS
        },
    }


def hydrate_from_data(data: dict[str, Any], force: bool = False) -> None:
    set_key("w_studentName", data.get("studentName", ""), force)
    set_key("w_classCode", data.get("classCode", ""), force)
    set_key("w_groupName", data.get("groupName", ""), force)
    set_key("w_members", data.get("members", ""), force)
    set_key("w_review2Choice", data.get("review2Choice") or data.get("review2choice") or "", force)

    blanks = data.get("blanks") or {}
    for key, _ in BLANK_FIELDS:
        set_key(f"w_blank_{key}", blanks.get(key, ""), force)

    songs = data.get("songs") or []
    for idx in range(7):
        song = songs[idx] if idx < len(songs) and isinstance(songs[idx], dict) else {}
        set_key(f"w_song_title_{idx}", song.get("title", ""), force)
        set_key(f"w_song_artist_{idx}", song.get("artist", ""), force)
        set_key(f"w_song_genre_{idx}", song.get("genre") or GENRES[0], force)
        set_key(f"w_song_time_{idx}", song.get("tag") or song.get("time") or "", force)

    cd = data.get("conditionsData") or default_conditions_data()
    set_key("w_total_formula", cd.get("totalFormula", ""), force)
    set_key("w_total_explain", cd.get("totalExplain", ""), force)
    for group in COND_GROUPS:
        group_data = (cd.get("groups") or {}).get(group["id"], [])
        by_id = {item.get("id"): item for item in group_data if isinstance(item, dict)}
        for cond in group["conds"]:
            item = by_id.get(cond["id"], {})
            set_key(f"w_cond_{cond['id']}_question", bool(item.get("question")), force)
            set_key(f"w_cond_{cond['id']}_formula", item.get("formula", ""), force)
            set_key(f"w_cond_{cond['id']}_explain", item.get("explain", ""), force)
            inputs = item.get("inputs") or {}
            counters = {"song": 0, "num": 0, "trait": 0}
            for input_type in cond["types"]:
                prefix = {"song": "s", "num": "n", "trait": "t"}[input_type]
                input_key = f"{prefix}{counters[input_type]}"
                set_key(f"w_cond_{cond['id']}_{input_key}", inputs.get(input_key, ""), force)
                counters[input_type] += 1

    selected_problem_conditions = set(data.get("probConds") or [])
    for cid, value, _, _ in PROBLEM_CONDITIONS:
        set_key(f"w_prob_{cid}", value in selected_problem_conditions, force)
    set_key("w_prob_statement", data.get("probStatement", ""), force)
    set_key("w_prob_formula", data.get("probFormula", ""), force)
    set_key("w_prob_explain", data.get("probExplain", ""), force)
    set_key("w_present_content", data.get("presentContent", ""), force)
    set_key("w_present_finding", data.get("presentFinding", ""), force)
    set_key("w_present_learned", data.get("presentLearned", ""), force)
    set_key("w_summary_when", data.get("summaryWhen", ""), force)
    set_key("w_summary_reflect", data.get("summaryReflect", ""), force)

    checked = set(data.get("checks") or [])
    for cid, _ in CHECK_ITEMS:
        set_key(f"w_check_{cid}", cid in checked, force)


def get_songs() -> list[dict[str, str]]:
    songs = []
    for idx, label in enumerate(LABELS):
        songs.append(
            {
                "label": label,
                "title": text_key(f"w_song_title_{idx}"),
                "artist": text_key(f"w_song_artist_{idx}"),
                "genre": str(st.session_state.get(f"w_song_genre_{idx}", GENRES[0])),
                "tag": text_key(f"w_song_time_{idx}"),
            }
        )
    return songs


def song_options() -> list[str]:
    return [""] + [song["label"] for song in get_songs() if song["title"]]


def song_label(label: str) -> str:
    if not label:
        return "곡 선택"
    for song in get_songs():
        if song["label"] == label:
            return f"{label}: {song['title'] or '미입력'}"
    return label


def collect_conditions_data() -> dict[str, Any]:
    result = {
        "totalFormula": text_key("w_total_formula"),
        "totalExplain": text_key("w_total_explain"),
        "groups": {},
    }
    for group in COND_GROUPS:
        result["groups"][group["id"]] = []
        for cond in group["conds"]:
            item: dict[str, Any] = {
                "id": cond["id"],
                "formula": text_key(f"w_cond_{cond['id']}_formula"),
                "explain": text_key(f"w_cond_{cond['id']}_explain"),
                "question": bool_key(f"w_cond_{cond['id']}_question"),
                "inputs": {},
            }
            counters = {"song": 0, "num": 0, "trait": 0}
            for input_type in cond["types"]:
                prefix = {"song": "s", "num": "n", "trait": "t"}[input_type]
                input_key = f"{prefix}{counters[input_type]}"
                item["inputs"][input_key] = text_key(f"w_cond_{cond['id']}_{input_key}")
                counters[input_type] += 1
            result["groups"][group["id"]].append(item)
    return result


def selected_problem_conditions() -> list[str]:
    values = []
    for cid, value, _, _ in PROBLEM_CONDITIONS:
        if bool_key(f"w_prob_{cid}"):
            values.append(value)
    return values


def collect_data(is_submitted: bool = False) -> dict[str, Any]:
    data = {
        "sessionId": st.session_state["session_id"],
        "currentStep": int(st.session_state.get("step", 1)),
        "submitted": is_submitted or bool(st.session_state.get("submitted_done", False)),
        "studentName": text_key("w_studentName"),
        "classCode": text_key("w_classCode"),
        "groupName": text_key("w_groupName"),
        "members": text_key("w_members"),
        "songs": get_songs(),
        "review1": "",
        "review2Choice": text_key("w_review2Choice"),
        "review2": "",
        "blanks": {key: text_key(f"w_blank_{key}") for key, _ in BLANK_FIELDS},
        "review2choice": text_key("w_review2Choice"),
        "conditionsData": collect_conditions_data(),
        "probConds": selected_problem_conditions(),
        "probStatement": text_key("w_prob_statement"),
        "probFormula": text_key("w_prob_formula"),
        "probExplain": text_key("w_prob_explain"),
        "presentContent": text_key("w_present_content"),
        "presentFinding": text_key("w_present_finding"),
        "presentLearned": text_key("w_present_learned"),
        "summaryWhen": text_key("w_summary_when"),
        "summaryReflect": text_key("w_summary_reflect"),
        "checks": [cid for cid, _ in CHECK_ITEMS if bool_key(f"w_check_{cid}")],
    }
    if is_submitted:
        data["submittedAt"] = datetime.now().isoformat(timespec="seconds")
    return data


def save_current_progress(silent: bool = True, completed_step: int | None = None) -> dict[str, Any] | None:
    if not st.session_state.get("activity_ready"):
        return None
    if not text_key("w_studentName"):
        return None
    data = collect_data(False)
    if completed_step is not None:
        data["completedStep"] = completed_step
        data["resumeStep"] = min(6, completed_step + 1)
    else:
        data["resumeStep"] = int(st.session_state.get("step", 1))
    result = upsert_session(st.session_state["session_id"], data)
    if not silent and result.get("success"):
        st.toast("저장됨")
    elif not silent:
        st.error(f"저장 실패: {result.get('error', '알 수 없는 오류')}")
    return result


def restore_step_from_data(data: dict[str, Any]) -> int:
    raw = data.get("resumeStep") or data.get("currentStep") or data.get("completedStep") or 1
    try:
        step = int(raw)
    except (TypeError, ValueError):
        step = 1
    if data.get("completedStep") and not data.get("resumeStep"):
        try:
            step = min(6, int(data["completedStep"]) + 1)
        except (TypeError, ValueError):
            step = 1
    return min(6, max(1, step))


def begin_activity(name: str, cls: str, group: str, members: str) -> None:
    st.session_state["activity_ready"] = True
    st.session_state["submitted_done"] = False
    result = get_saved_session_by_identity(name, cls, group, members)
    if result.get("success") and result.get("found") and result.get("data"):
        data = result["data"]
        st.session_state["session_id"] = data.get("sessionId") or st.session_state["session_id"]
        st.session_state["step"] = restore_step_from_data(data)
        st.session_state["step1_sub"] = "1a"
        hydrate_from_data(data, force=True)
        st.session_state["restore_notice"] = "이전에 작성하던 기록을 불러왔습니다."
    else:
        st.session_state["step"] = 1
        st.session_state["step1_sub"] = "1a"
        hydrate_from_data(
            {"studentName": name, "classCode": cls, "groupName": group, "members": members},
            force=True,
        )
        st.session_state["restore_notice"] = "새 활동을 시작합니다."
    save_current_progress(silent=True)
    st.rerun()


# ── Progress bar ─────────────────────────────────────────────────────────────

def progress_bar() -> None:
    current = int(st.session_state.get("step", 1))
    dots = []
    lines = []
    lbls = []
    for idx, label in enumerate(STEP_LABELS, start=1):
        if idx < current:
            dots.append(f'<div class="dot done" id="dot-{idx}"></div>')
            lbls.append(f'<div class="lbl done" style="flex:1;text-align:center;">{html.escape(label)}</div>')
        elif idx == current:
            dots.append(f'<div class="dot active">{idx}</div>')
            lbls.append(f'<div class="lbl active" style="flex:1;text-align:center;">{html.escape(label)}</div>')
        else:
            dots.append(f'<div class="dot">{idx}</div>')
            lbls.append(f'<div class="lbl" style="flex:1;text-align:center;">{html.escape(label)}</div>')
        if idx < len(STEP_LABELS):
            klass = "prog-line done" if idx < current else "prog-line"
            lines.append(f'<div class="{klass}"></div>')

    steps_html = ""
    for i, dot in enumerate(dots):
        steps_html += dot
        if i < len(lines):
            steps_html += lines[i]

    # lbl-row: need spacer before first and after last to align
    lbl_html = '<div class="lbl-row" style="display:flex;gap:0;">'
    for idx, (label, lbl) in enumerate(zip(STEP_LABELS, lbls)):
        lbl_html += lbl
    lbl_html += "</div>"

    st.markdown(
        f"""
        <div class="progress-wrap">
          <div class="progress-inner">
            <div class="steps-row">{steps_html}</div>
            {lbl_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── App header ───────────────────────────────────────────────────────────────

def render_header() -> None:
    name = text_key("w_studentName")
    cls = text_key("w_classCode")
    group = text_key("w_groupName")
    st.markdown(
        f"""
        <div class="app-header">
          <div style="display:flex;align-items:center;gap:10px;">
            <div class="hdr-icon">🎵</div>
            <div>
              <div class="hdr-title">플레이리스트로 순열 살펴보기</div>
              <div class="hdr-sub">{html.escape(name)} · {html.escape(cls)} {html.escape(group)}</div>
            </div>
          </div>
          <div class="status-progress" style="font-size:.7rem;">자동 저장</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Splash + Info modal ──────────────────────────────────────────────────────

def render_start() -> None:
    # 스플래시 상단 타이틀
    st.markdown(
        """
        <div class="splash-overlay">
          <div class="splash-chip">공통수학Ⅰ · 경우의 수</div>
          <div style="font-size:3rem;margin-bottom:20px;filter:drop-shadow(0 4px 16px rgba(96,111,105,.25));">🎵</div>
          <div class="splash-title">플레이리스트로<br>순열 살펴보기</div>
          <div class="splash-desc">같은 곡, 다른 순서<br>플레이리스트로 순열을 알아봅시다</div>
          <div style="font-size:.72rem;color:rgba(61,74,68,.55);letter-spacing:.6px;margin-bottom:0;">made by mingyu kim</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 정보 입력 카드
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            """
            <div style="background:var(--glass-bg-s);-webkit-backdrop-filter:saturate(180%) blur(20px);
            backdrop-filter:saturate(180%) blur(20px);border:1px solid var(--glass-border);
            border-radius:var(--r-xl);padding:28px 24px 8px;
            box-shadow:var(--shadow-lg),inset 0 1px 0 rgba(255,255,255,.82);margin-bottom:4px;">
              <div style="font-size:.7rem;font-weight:700;color:var(--lb2);letter-spacing:.9px;text-transform:uppercase;margin-bottom:6px;">기본 정보 입력</div>
              <div style="font-size:1.25rem;font-weight:900;margin-bottom:4px;color:var(--md-on-surface);">활동을 시작하기 전에</div>
              <div style="font-size:.82rem;color:var(--md-on-surface-v);margin-bottom:16px;line-height:1.65;">아래 정보를 모두 입력해야 활동을 시작할 수 있어요.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        name = st.text_input("이름", placeholder="홍길동", key="start_name")
        c1, c2 = st.columns(2)
        with c1:
            cls = st.selectbox("반", [""] + CLASSES, format_func=lambda x: x or "반 선택", key="start_class")
        with c2:
            group = st.selectbox("조", [""] + GROUPS, format_func=lambda x: x or "조 선택", key="start_group")
        members = st.text_input("조원 이름", placeholder="카리나, 윈터, 닝닝, 지젤", key="start_members")
        st.markdown("<br>", unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            if st.button("활동 시작하기 🎵", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("이름을 입력하세요.")
                elif not cls:
                    st.error("반을 입력하세요.")
                elif not group:
                    st.error("조를 입력하세요.")
                elif not members.strip():
                    st.error("조원 이름을 입력하세요.")
                else:
                    begin_activity(name.strip(), cls, group, members.strip())
        with cb:
            if st.button("🔐 교사용 대시보드", use_container_width=True):
                set_query_page("teacher")
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)


# ── Nav buttons ──────────────────────────────────────────────────────────────

def validate_step(step: int) -> bool:
    if step == 1:
        missing = [label for key, label in BLANK_FIELDS if not text_key(f"w_blank_{key}")]
        if missing:
            st.error("<보기>의 빈칸을 모두 채우세요.")
            return False
        if not text_key("w_review2Choice"):
            st.error("오늘의 질문에서 예/아니오를 선택하세요.")
            return False
    elif step == 2:
        filled = len([song for song in get_songs() if song["title"]])
        if filled < 7:
            st.error(f"7곡을 모두 입력하세요. 현재 {filled}곡이 입력되었습니다.")
            return False
    elif step == 3:
        if not text_key("w_total_formula"):
            st.error("전체 경우의 수 식을 먼저 작성하세요.")
            return False
        for cond in all_conditions():
            if bool_key(f"w_cond_{cond['id']}_question"):
                continue
            if not text_key(f"w_cond_{cond['id']}_formula") or not text_key(f"w_cond_{cond['id']}_explain"):
                st.error(f"제한조건 {COND_NUMS[cond['id']]}번의 식과 이유를 작성하거나 질문으로 표시하세요.")
                return False
    elif step == 4:
        checked = selected_problem_conditions()
        if len(checked) < 2:
            st.error("제한조건을 2가지 이상 선택하세요.")
            return False
        if not text_key("w_prob_statement"):
            st.error("만든 문제를 작성하세요.")
            return False
    elif step == 6:
        if not all(bool_key(f"w_check_{cid}") for cid, _ in CHECK_ITEMS):
            st.error("자기 점검 항목을 모두 확인하세요.")
            return False
    return True


def navigate(target_step: int) -> None:
    current = int(st.session_state.get("step", 1))
    if target_step > current and not validate_step(current):
        return
    if target_step > current:
        save_current_progress(silent=False, completed_step=current)
    else:
        save_current_progress(silent=True)
    st.session_state["step"] = target_step
    st.session_state["step1_sub"] = "1a"
    st.rerun()


def nav_buttons(prev_step: int | None, next_step: int | None, next_label: str = "다음 단계") -> None:
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1])
    with left:
        if prev_step is not None and st.button("← 이전", use_container_width=True, key=f"nav_prev_{prev_step}_{next_step}"):
            navigate(prev_step)
    with right:
        if next_step is not None and st.button(
            f"{next_label} →", type="primary", use_container_width=True,
            key=f"nav_next_{prev_step}_{next_step}",
        ):
            navigate(next_step)


# ── Drag-and-drop blank fill widget ──────────────────────────────────────────

def render_blank_sync_inputs() -> None:
    for key, _ in BLANK_FIELDS:
        st.text_input(f"blank__{key}", key=f"w_blank_{key}", label_visibility="collapsed")


def render_permutation_drag_widget() -> None:
    words_json = json.dumps(WORD_ITEMS, ensure_ascii=False)
    fields_json = json.dumps([{"key": key, "label": label} for key, label in BLANK_FIELDS], ensure_ascii=False)
    blanks_json = json.dumps(
        {key: text_key(f"w_blank_{key}") for key, _ in BLANK_FIELDS},
        ensure_ascii=False,
    )
    component_html = r"""
    <style>
      :root {
        --lb: #5FA8C8; --lb2: #3A8BAF; --fg: #3D4A44; --fg2: #1E2822;
        --sage: #6E9170; --outline: rgba(61,74,68,.24);
      }
      * { box-sizing: border-box; }
      body { margin: 0; color: var(--fg2); font-family: "Noto Sans KR", -apple-system, sans-serif; }
      .drag-section {
        background: rgba(248,246,242,.82);
        border: 1.5px solid rgba(61,74,68,.18);
        border-radius: 18px; padding: 20px;
      }
      .section-title {
        font-size: .78rem; font-weight: 800; color: var(--lb2);
        text-transform: uppercase; letter-spacing: .8px; margin-bottom: 14px;
      }
      .word-bank {
        min-height: 72px; display: flex; flex-wrap: wrap;
        align-items: center; gap: 8px; padding: 13px;
        margin-bottom: 15px;
        border: 1.5px dashed rgba(58,139,175,.48); border-radius: 14px;
        background: rgba(169,207,224,.14);
      }
      .word-bank.over { background: rgba(169,207,224,.28); border-color: var(--lb2); }
      .bank-title {
        font-size: .72rem; font-weight: 800; color: var(--md-on-surface, var(--fg2));
        margin-bottom: 8px; text-align: center;
      }
      .concept-lines { display: grid; gap: 10px; }
      .concept-line {
        margin: 0; padding: 14px 16px;
        border: 1px solid rgba(61,74,68,.16); border-radius: 14px;
        background: rgba(255,255,255,.72);
        line-height: 2.2; word-break: keep-all; font-size: .92rem;
      }
      .word-chip {
        appearance: none;
        border: 1.5px solid rgba(169,207,224,.45);
        border-radius: 20px;
        background: rgba(169,207,224,.22);
        color: var(--fg2);
        cursor: grab;
        display: inline-flex; align-items: center; justify-content: center;
        min-height: 34px; max-width: 100%;
        padding: 5px 13px;
        font: inherit; font-size: .82rem; font-weight: 700;
        box-shadow: 0 2px 8px rgba(30,40,34,.06);
        touch-action: none; user-select: none; white-space: nowrap;
        transition: all .18s;
      }
      .word-chip:hover {
        background: linear-gradient(135deg,var(--lb),var(--sage));
        color: #fff; border-color: transparent;
        transform: scale(1.05);
        box-shadow: 0 6px 18px rgba(127,184,212,.38);
      }
      .word-chip:active { cursor: grabbing; }
      .word-chip.dragging { opacity: .45; }
      .drop-zone {
        display: inline-flex; align-items: center; justify-content: center;
        vertical-align: middle; min-width: 130px; min-height: 36px; max-width: 100%;
        margin: 0 5px; padding: 3px 8px;
        border: 2px dashed rgba(127,184,212,.38); border-radius: 10px;
        background: rgba(255,255,255,.32);
        color: rgba(61,74,68,.5); font-size: .82rem; font-weight: 700;
        transition: all .18s; cursor: pointer;
      }
      .drop-zone.over { border-color: var(--lb2); background: rgba(169,207,224,.15); }
      .drop-zone.filled {
        border-style: solid; border-color: var(--lb2);
        background: rgba(169,207,224,.18); color: var(--lb2);
      }
      .sync-status { min-height: 18px; margin-top: 10px; color: #7A2A2A; font-size: .76rem; font-weight: 700; }
      .touch-clone {
        position: fixed; left: 0; top: 0; z-index: 9999;
        pointer-events: none; opacity: .9; transform: translate(-50%, -50%);
      }
      @media (max-width: 640px) {
        .drop-zone { min-width: 100px; margin: 3px 2px; }
        .word-chip { font-size: .76rem; padding: 5px 10px; }
        .concept-line { font-size: .84rem; }
      }
    </style>

    <div class="drag-section">
      <div class="section-title">📝 순열 개념 확인 — &lt;보기&gt;에서 끌어다 빈칸에 채워보세요</div>
      <div class="bank-title">&lt;보기&gt;</div>
      <div id="perm-word-bank" class="word-bank" aria-label="보기"></div>
      <div style="font-size:.68rem;color:rgba(61,74,68,.6);margin-bottom:16px;text-align:center;">
        💡 &lt;보기&gt;의 키워드를 아래 빈칸으로 끌어다 놓으세요. 잘못 놓은 경우 키워드를 한 번 터치하면 &lt;보기&gt;로 되돌아갑니다.
      </div>
      <div class="concept-lines">
        <p class="concept-line">
          서로 다른 <b>n</b>개에서 <b>r</b>&thinsp;(0&lt;r≤n)개를 택하여 일렬로 나열하는 것을
          <span class="drop-zone" data-key="def1"></span>이라 하고, 이 순열의 가짓수를 기호로
          <span class="drop-zone" data-key="def2"></span>와 같이 나타낸다.
        </p>
        <p class="concept-line">
          서로 다른 <b>n</b>개에서 <b>r</b>개를 택하는 순열의 수 &ensp;
          <b>nPr</b> = <span class="drop-zone" data-key="npr"></span> &ensp;(단, 0&lt;r≤n)
        </p>
        <p class="concept-line">
          (1)&ensp; <b>nPn</b> = <span class="drop-zone" data-key="pnn"></span>
          = <span class="drop-zone" data-key="pnnExpand"></span>
        </p>
        <p class="concept-line">
          (2)&ensp; <b>nP0</b> = <span class="drop-zone" data-key="p0"></span>
          &ensp;,&ensp; <b>0!</b> = <span class="drop-zone" data-key="fac0"></span>
        </p>
        <p class="concept-line">
          (3)&ensp; <b>nPr</b> = <span class="drop-zone" data-key="fact"></span>
          &ensp;(단, <span class="drop-zone" data-key="cond"></span>)
        </p>
        <p style="font-size:.76rem;color:rgba(61,74,68,.6);padding-top:8px;border-top:1px solid rgba(61,74,68,.12);">
          💬 [참고] 기호 nPr에서 P는 Permutation(순열)의 머리글자이다.
        </p>
      </div>
      <div id="sync-status" class="sync-status"></div>
    </div>

    <script>
      (() => {
        const WORDS = __WORDS__;
        const FIELDS = __FIELDS__;
        const INITIAL_BLANKS = __BLANKS__;
        const byId = new Map(WORDS.map(w => [w.id, w]));
        const order = WORDS.map(w => w.id);
        const state = {};
        let draggingId = null, touchId = null, touchClone = null, pointerId = null;

        function zoneForWord(id) { return Object.keys(state).find(k => state[k] && state[k].id === id); }
        function clearWord(id) { const k = zoneForWord(id); if (k) delete state[k]; }
        function assignWord(id, key) {
          if (!id || !byId.has(id)) return;
          clearWord(id);
          if (state[key]) delete state[key];
          const w = byId.get(id);
          state[key] = { id: w.id, text: w.text };
          render();
        }

        function setParentInput(key, value) {
          try {
            const doc = window.parent.document;
            const input = doc.querySelector(`input[aria-label="blank__${key}"]`);
            if (!input) return false;
            if (input.value === value) return true;
            const setter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
            setter.call(input, value);
            input.dispatchEvent(new window.parent.Event("input", { bubbles: true }));
            input.dispatchEvent(new window.parent.Event("change", { bubbles: true }));
            return true;
          } catch(e) { return false; }
        }
        function syncAll() {
          const failed = FIELDS.some(f => !setParentInput(f.key, state[f.key] ? state[f.key].text : ""));
          document.getElementById("sync-status").textContent = failed
            ? "빈칸 저장 동기화가 지연되고 있습니다. 페이지를 새로고침한 뒤 다시 시도하세요." : "";
        }

        function makeChip(word, inZone) {
          const chip = document.createElement("button");
          chip.type = "button"; chip.className = "word-chip";
          chip.draggable = true; chip.dataset.id = word.id; chip.textContent = word.text;
          chip.addEventListener("dragstart", e => {
            draggingId = word.id; chip.classList.add("dragging");
            e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", word.id);
          });
          chip.addEventListener("dragend", () => { draggingId = null; chip.classList.remove("dragging"); });
          chip.addEventListener("pointerdown", pointerStart);
          chip.addEventListener("touchstart", touchStart, { passive: false });
          if (inZone) chip.addEventListener("click", () => { clearWord(word.id); render(); });
          return chip;
        }

        function renderBank() {
          const bank = document.getElementById("perm-word-bank");
          const used = new Set(Object.values(state).map(i => i.id));
          bank.innerHTML = "";
          order.filter(id => !used.has(id)).forEach(id => bank.appendChild(makeChip(byId.get(id), false)));
        }
        function renderZones() {
          document.querySelectorAll(".drop-zone").forEach(zone => {
            const key = zone.dataset.key; zone.innerHTML = ""; zone.classList.remove("filled");
            const item = state[key];
            if (item && byId.has(item.id)) {
              zone.classList.add("filled"); zone.appendChild(makeChip(byId.get(item.id), true));
            } else { zone.textContent = ""; }
          });
        }
        function render() { renderBank(); renderZones(); syncAll(); }

        function restoreInitial() {
          const used = new Set();
          FIELDS.forEach(f => {
            const text = INITIAL_BLANKS[f.key] || "";
            if (!text) return;
            let w = WORDS.find(i => i.text === text && !used.has(i.id));
            if (!w) { w = { id: `custom-${f.key}`, text }; byId.set(w.id, w); }
            used.add(w.id);
            state[f.key] = { id: w.id, text: w.text };
          });
        }

        function bindDrops() {
          const bank = document.getElementById("perm-word-bank");
          bank.addEventListener("dragover", e => { e.preventDefault(); bank.classList.add("over"); });
          bank.addEventListener("dragleave", () => bank.classList.remove("over"));
          bank.addEventListener("drop", e => { e.preventDefault(); bank.classList.remove("over"); clearWord(e.dataTransfer.getData("text/plain") || draggingId); render(); });
          document.querySelectorAll(".drop-zone").forEach(zone => {
            zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("over"); });
            zone.addEventListener("dragleave", () => zone.classList.remove("over"));
            zone.addEventListener("drop", e => { e.preventDefault(); zone.classList.remove("over"); assignWord(e.dataTransfer.getData("text/plain") || draggingId, zone.dataset.key); });
            zone.addEventListener("click", e => { if (e.target.closest(".word-chip")) return; if (state[zone.dataset.key]) { delete state[zone.dataset.key]; render(); } });
          });
        }

        function moveCloneTo(x, y) { if (touchClone) { touchClone.style.left=`${x}px`; touchClone.style.top=`${y}px`; } }
        function cleanupTouch() { window.removeEventListener("touchmove", touchMove); if (touchClone) touchClone.remove(); touchClone=null; touchId=null; }
        function cleanupPointer() { window.removeEventListener("pointermove", pointerMove); if (touchClone) touchClone.remove(); touchClone=null; touchId=null; pointerId=null; }

        function pointerStart(e) {
          if (e.button !== 0 || touchId) return; e.preventDefault();
          pointerId=e.pointerId; touchId=e.currentTarget.dataset.id; draggingId=touchId;
          touchClone=e.currentTarget.cloneNode(true); touchClone.classList.add("touch-clone");
          document.body.appendChild(touchClone); moveCloneTo(e.clientX, e.clientY);
          window.addEventListener("pointermove", pointerMove);
          window.addEventListener("pointerup", pointerEnd, { once:true });
          window.addEventListener("pointercancel", cleanupPointer, { once:true });
        }
        function pointerMove(e) { if (pointerId!==null && e.pointerId!==pointerId) return; e.preventDefault(); moveCloneTo(e.clientX, e.clientY); }
        function pointerEnd(e) {
          if (pointerId!==null && e.pointerId!==pointerId) return; e.preventDefault();
          const el=document.elementFromPoint(e.clientX,e.clientY);
          const zone=el&&el.closest(".drop-zone"); const bank=el&&el.closest("#perm-word-bank");
          const id=touchId; cleanupPointer();
          if (zone) assignWord(id, zone.dataset.key); else if (bank) { clearWord(id); render(); }
          draggingId=null;
        }
        function touchStart(e) {
          if (e.touches.length!==1||touchId) return; e.preventDefault();
          touchId=e.currentTarget.dataset.id; draggingId=touchId;
          touchClone=e.currentTarget.cloneNode(true); touchClone.classList.add("touch-clone");
          document.body.appendChild(touchClone); moveCloneTo(e.touches[0].clientX, e.touches[0].clientY);
          window.addEventListener("touchmove", touchMove, { passive:false });
          window.addEventListener("touchend", touchEnd, { passive:false, once:true });
          window.addEventListener("touchcancel", cleanupTouch, { passive:false, once:true });
        }
        function touchMove(e) { e.preventDefault(); moveCloneTo(e.touches[0].clientX, e.touches[0].clientY); }
        function touchEnd(e) {
          e.preventDefault(); const t=e.changedTouches[0];
          const el=document.elementFromPoint(t.clientX,t.clientY);
          const zone=el&&el.closest(".drop-zone"); const bank=el&&el.closest("#perm-word-bank");
          const id=touchId; cleanupTouch();
          if (zone) assignWord(id, zone.dataset.key); else if (bank) { clearWord(id); render(); }
          draggingId=null;
        }

        restoreInitial(); bindDrops(); render();
      })();
    </script>
    """
    component_html = (
        component_html.replace("__WORDS__", words_json)
        .replace("__FIELDS__", fields_json)
        .replace("__BLANKS__", blanks_json)
    )
    components.html(component_html, height=620, scrolling=False)


# ── Step 1 ────────────────────────────────────────────────────────────────────

def render_step1() -> None:
    sub = st.session_state.get("step1_sub", "1a")

    if sub == "1a":
        # ─ 1a: 오늘의 질문 + 학습목표 ─
        st.markdown(
            '<div class="card">'
            '<div class="eyebrow">STEP 01-1 · 오늘의 질문</div>'
            '<div class="card-title">플레이리스트에서 곡의 순서를 바꾸면 다른 플레이리스트일까요?</div>',
            unsafe_allow_html=True,
        )
        choice = st.session_state.get("w_review2Choice", "")
        ca, cb = st.columns(2)
        yes_type = "primary" if choice == "yes" else "secondary"
        no_type = "primary" if choice == "no" else "secondary"
        with ca:
            if st.button("✅ 예", type=yes_type, use_container_width=True, key="btn_yes"):
                st.session_state["w_review2Choice"] = "yes"
                st.rerun()
        with cb:
            if st.button("❌ 아니오", type=no_type, use_container_width=True, key="btn_no"):
                st.session_state["w_review2Choice"] = "no"
                st.rerun()
        if choice == "yes":
            st.success("선택: ✅ 예")
        elif choice == "no":
            st.info("선택: ❌ 아니오")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="card">'
            '<div class="eyebrow">STEP 01-1 · 학습목표</div>'
            '<div class="card-title">오늘 활동에서 배울 것들</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="mini-card" style="background:rgba(127,184,212,.1);border:1px solid rgba(127,184,212,.2);">
              <span style="font-size:1.1rem;">①</span>&ensp;
              순열의 개념을 이해하고, 곡의 순서가 중요한 플레이리스트 배열 상황을 순열로 해석할 수 있다.
            </div>
            <div class="mini-card" style="background:rgba(127,184,212,.1);border:1px solid rgba(127,184,212,.2);">
              <span style="font-size:1.1rem;">②</span>&ensp;
              조별로 선택한 곡으로 제한조건을 만족하는 플레이리스트 배열의 경우의 수를 구하고, 그 풀이 과정을 논리적으로 설명할 수 있다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        _, right = st.columns([1, 1])
        with right:
            if st.button("다음 →", type="primary", use_container_width=True, key="go_1b"):
                if not st.session_state.get("w_review2Choice"):
                    st.error("오늘의 질문에서 예/아니오를 선택하세요.")
                else:
                    st.session_state["step1_sub"] = "1b"
                    st.rerun()

    else:
        # ─ 1b: 순열 개념 빈칸 채우기 ─
        st.markdown(
            '<div class="card">'
            '<div class="eyebrow">STEP 01-2 · 순열 개념 확인</div>'
            '<div class="card-title">순열이란 무엇인가?</div>'
            '<div class="card-desc">오늘 활동을 시작하기 전, 순열의 핵심 개념을 다시 확인해봅시다.</div>',
            unsafe_allow_html=True,
        )
        render_blank_sync_inputs()
        render_permutation_drag_widget()
        st.markdown("</div>", unsafe_allow_html=True)

        left, right = st.columns([1, 1])
        with left:
            if st.button("← 이전", use_container_width=True, key="go_1a"):
                st.session_state["step1_sub"] = "1a"
                st.rerun()
        with right:
            if st.button("다음 단계 →", type="primary", use_container_width=True, key="go_step2"):
                missing = [label for key, label in BLANK_FIELDS if not text_key(f"w_blank_{key}")]
                if missing:
                    st.error("<보기>의 빈칸을 모두 채우세요.")
                else:
                    save_current_progress(silent=False, completed_step=1)
                    st.session_state["step"] = 2
                    st.session_state["step1_sub"] = "1a"
                    st.rerun()


# ── Step 2 ────────────────────────────────────────────────────────────────────

def render_step2() -> None:
    st.markdown(
        '<div class="card">'
        '<div class="eyebrow">STEP 02 · 플레이리스트 구성</div>'
        '<div class="card-title">어떤 플레이리스트를 만들어볼까?</div>'
        '<div class="card-desc">지금 당장 듣고 싶은 7개의 곡을 직접 선택해봅시다. 멜론, 유튜브 뮤직 등에서 검색하여 곡의 정보를 입력해봅시다.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="warn-box">⚠️ <strong>중요:</strong> 오늘의 활동은 7곡 중의 일부를 가지고 배열하는 활동이 아닙니다. '
        '조별로 선택한 <strong>7개의 곡 전체를 조건에 맞춰 순서 있게 배열</strong>하는 활동입니다.</div>',
        unsafe_allow_html=True,
    )
    hdr = st.columns([0.5, 2.2, 2.2, 1.6, 1.5])
    for i, h in enumerate(["", "곡명", "아티스트", "장르", "재생 시간"]):
        hdr[i].markdown(f"<div style='font-size:.62rem;font-weight:700;color:var(--fg);text-transform:uppercase;letter-spacing:.5px;padding:0 4px;'>{h}</div>", unsafe_allow_html=True)
    for idx, label in enumerate(LABELS):
        cols = st.columns([0.5, 2.2, 2.2, 1.6, 1.5])
        cols[0].markdown(
            f"<div style='width:32px;height:32px;background:linear-gradient(135deg,var(--lb),var(--sage));border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.8rem;color:#fff;box-shadow:0 3px 8px rgba(127,184,212,.3);'>{label}</div>",
            unsafe_allow_html=True,
        )
        cols[1].text_input("곡명", key=f"w_song_title_{idx}", label_visibility="collapsed", placeholder="곡명")
        cols[2].text_input("아티스트", key=f"w_song_artist_{idx}", label_visibility="collapsed", placeholder="아티스트")
        cols[3].selectbox("장르", GENRES, key=f"w_song_genre_{idx}", label_visibility="collapsed")
        cols[4].text_input("재생 시간", key=f"w_song_time_{idx}", label_visibility="collapsed", placeholder="3:00")
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(1, 3)


# ── Step 3 ────────────────────────────────────────────────────────────────────

def render_song_summary_sidebar() -> None:
    st.markdown('<div class="song-sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.72rem;font-weight:800;color:var(--lb2);margin-bottom:10px;letter-spacing:.3px;">🎧 선택한 7곡</div>', unsafe_allow_html=True)
    for song in get_songs():
        title = song["title"] or "미입력"
        artist = song["artist"] or "미입력"
        st.markdown(
            f"<div style='background:#fff;border:1px solid rgba(127,184,212,.25);border-radius:var(--r-sm);padding:9px 11px;display:flex;align-items:flex-start;gap:9px;margin-bottom:7px;'>"
            f"<div style='width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--lb),var(--sage));display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.72rem;color:#fff;flex-shrink:0;'>{html.escape(song['label'])}</div>"
            f"<div><div style='font-size:.82rem;font-weight:700;line-height:1.35;margin-bottom:2px;word-break:break-word;'>{html.escape(title)}</div>"
            f"<div style='font-size:.7rem;color:var(--md-on-surface-v);'>{html.escape(artist)}"
            + (f" · {html.escape(song['genre'])}" if song.get('genre') else "")
            + "</div></div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def plain_cond_sentence(cond: dict[str, Any]) -> str:
    result = ""
    type_idx = 0
    for part in cond["parts"]:
        result += part
        if type_idx < len(cond["types"]):
            t = cond["types"][type_idx]
            result += "[곡 선택]" if t == "song" else "[자리/개수]" if t == "num" else "[곡의 특징]"
            type_idx += 1
    return " ".join(result.split())


def filled_cond_sentence(cond: dict[str, Any]) -> str:
    result = ""
    counters = {"song": 0, "num": 0, "trait": 0}
    type_idx = 0
    for part in cond["parts"]:
        result += part
        if type_idx < len(cond["types"]):
            input_type = cond["types"][type_idx]
            prefix = {"song": "s", "num": "n", "trait": "t"}[input_type]
            input_key = f"{prefix}{counters[input_type]}"
            value = text_key(f"w_cond_{cond['id']}_{input_key}")
            if input_type == "song":
                value = song_label(value) if value else "[곡 선택]"
            elif input_type == "num":
                value = value or "[자리/개수]"
            else:
                value = value or "[곡의 특징]"
            result += value
            counters[input_type] += 1
            type_idx += 1
    return " ".join(result.split())


def render_condition_inputs(cond: dict[str, Any]) -> None:
    counters = {"song": 0, "num": 0, "trait": 0}
    input_types = cond["types"]
    if not input_types:
        return
    cols = st.columns(min(3, len(input_types)))
    for idx, input_type in enumerate(input_types):
        prefix = {"song": "s", "num": "n", "trait": "t"}[input_type]
        input_key = f"{prefix}{counters[input_type]}"
        widget_key = f"w_cond_{cond['id']}_{input_key}"
        with cols[idx % len(cols)]:
            if input_type == "song":
                opts = song_options()
                current = st.session_state.get(widget_key, "")
                if current and current not in opts:
                    opts.append(current)
                st.selectbox("곡 선택", opts, format_func=song_label, key=widget_key)
            elif input_type == "num":
                st.text_input("자리/개수", key=widget_key, placeholder="n")
            else:
                st.text_input("곡의 특징", key=widget_key, placeholder="장르가 댄스, 재생 시간이 가장 짧은 곡 등")
        counters[input_type] += 1


def render_step3() -> None:
    st.markdown(
        '<div class="card">'
        '<div class="eyebrow">STEP 03 · 경우의 수 계산하기</div>'
        '<div class="card-title">제한조건을 만족하는 플레이리스트의 수</div>'
        '<div class="card-desc">먼저 전체 경우의 수를 구한 다음, 각 제한조건을 만족하는 경우의 수를 구해봅시다. '
        '각 조건에서 사용할 곡 또는 곡의 특징을 선택하고 경우의 수를 구하는 식과 그렇게 식을 세운 이유를 작성해봅시다.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:var(--md-primary-cont);border-radius:var(--r-md);padding:18px;margin-bottom:4px;">'
        '<div style="font-size:.78rem;font-weight:800;color:var(--md-primary);margin-bottom:10px;">🔢 전체 경우의 수</div>'
        '<div style="font-size:.88rem;line-height:2;margin-bottom:12px;">내가 선택한 7곡으로 플레이리스트를 몇 가지 만들 수 있나요?</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    col1.text_area("경우의 수를 구하는 식", key="w_total_formula", placeholder="식을 직접 작성해보세요.", height=90)
    col2.text_area("왜 이 식이 나왔는지 설명해보기", key="w_total_explain", placeholder="이유를 간략하게 설명해보세요", height=90)
    st.markdown("</div></div>", unsafe_allow_html=True)

    left, right = st.columns([0.9, 2.4])
    with left:
        render_song_summary_sidebar()
    with right:
        for group in COND_GROUPS:
            color = group["color"]
            with st.expander(
                f"{group['icon']} {group['title']} · {len(group['conds'])}문제",
                expanded=True,
            ):
                if group.get("note"):
                    st.caption(group["note"])
                for cond in group["conds"]:
                    num = COND_NUMS[cond["id"]]
                    is_q = bool_key(f"w_cond_{cond['id']}_question")
                    sentence = filled_cond_sentence(cond)
                    st.markdown(
                        f"<div class='cond-item'>"
                        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:12px;'>"
                        f"<span class='cond-num' style='background:{color};'>{num}</span>"
                        f"<span style='font-size:.88rem;font-weight:700;flex:1;color:var(--md-on-surface);'>{html.escape(sentence)}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    render_condition_inputs(cond)
                    q_col, _ = st.columns([1, 2])
                    with q_col:
                        q_label = "✅ 질문 표시됨" if is_q else "❓ 질문으로 표시"
                        if st.button(q_label, key=f"qbtn_{cond['id']}", use_container_width=True):
                            st.session_state[f"w_cond_{cond['id']}_question"] = not is_q
                            st.rerun()
                    if is_q:
                        st.info("질문으로 표시한 문제입니다. 이 문제는 답을 작성하지 않아도 다음 단계로 넘어갈 수 있습니다.")
                    else:
                        cols = st.columns(2)
                        cols[0].text_area("경우의 수 식", key=f"w_cond_{cond['id']}_formula", placeholder="식을 작성하세요", height=86)
                        cols[1].text_area("왜 이 식이 나왔는지 설명해보기", key=f"w_cond_{cond['id']}_explain", placeholder="이유를 간략하게 설명해보세요", height=86)
                    st.markdown("</div>", unsafe_allow_html=True)
        nav_buttons(2, 4)


# ── Step 4 ────────────────────────────────────────────────────────────────────

def render_selected_condition_summary() -> None:
    checked = [(cid, label, group_id) for cid, _, label, group_id in PROBLEM_CONDITIONS if bool_key(f"w_prob_{cid}")]
    if not checked:
        return
    st.markdown(
        '<div style="background:var(--md-surface-var, rgba(240,234,224,.72));border:1.5px solid rgba(61,74,68,.18);border-radius:var(--r-md);padding:16px 18px;margin-bottom:16px;">'
        '<div style="font-size:.82rem;font-weight:800;color:var(--md-primary);margin-bottom:10px;">📌 선택한 조건 유형 정리</div>',
        unsafe_allow_html=True,
    )
    for _, label, group_id in checked:
        if group_id == "custom":
            st.markdown(
                f"<div class='mini-card'><strong>{html.escape(label)}</strong><br>"
                "<span class='small-muted'>앞의 유형을 바탕으로 조가 직접 새로운 조건을 추가합니다.</span></div>",
                unsafe_allow_html=True,
            )
            continue
        group = next((g for g in COND_GROUPS if g["id"] == group_id), None)
        if group:
            items_html = "".join(
                f"<li style='margin-bottom:4px;font-size:.78rem;'>{COND_NUMS[c['id']]}번. {html.escape(plain_cond_sentence(c))}</li>"
                for c in group["conds"]
            )
            st.markdown(
                f"<div class='mini-card'><strong>{html.escape(label)}</strong>"
                f"<ul style='margin:8px 0 0 18px;color:var(--md-on-surface-v);line-height:1.7;'>{items_html}</ul></div>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def render_step4() -> None:
    st.markdown(
        '<div class="card">'
        '<div class="eyebrow">STEP 04 · 문제 만들기</div>'
        '<div class="card-title">나만의 순열 문제 설계하기</div>'
        '<div class="card-desc">앞에서 풀었던 제한조건을 <strong>2가지 이상 선택</strong>하거나 또 다른 새로운 조건을 추가하여 새로운 문제를 직접 만들어봅시다.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="tip-box">💡 예시: "조건 1(위치 고정) + 조건 이웃"을 결합하면?<br>'
        '"A를 첫 번째로 고정하고, B와 C가 이웃할 때 플레이리스트의 수는?"</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**사용할 조건 선택 (2가지 이상)**")
    cols = st.columns(2)
    for idx, (cid, _, label, _) in enumerate(PROBLEM_CONDITIONS):
        with cols[idx % 2]:
            st.checkbox(label, key=f"w_prob_{cid}")
    render_selected_condition_summary()
    st.text_area(
        "📝 내가 만든 문제",
        key="w_prob_statement",
        placeholder="어떤 7곡의 플레이리스트에서, ~할 때 만들 수 있는 플레이리스트의 개수를 구하시오.",
        height=130,
    )
    st.text_area("경우의 수를 구하는 식", key="w_prob_formula", placeholder="선택한 조건을 결합한 식을 작성하세요.", height=100)
    st.text_area("풀이 과정 및 이유", key="w_prob_explain", placeholder="왜 이 식을 사용했는지, 어떤 순서로 계산했는지 설명하세요.", height=130)
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(3, 5)


# ── Step 5 ────────────────────────────────────────────────────────────────────

def group_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    group = item.get("groupName", "")
    digits = "".join(ch for ch in str(group) if ch.isdigit())
    order = int(digits) if digits else 9999
    return order, normalize_group_name(group)


def render_problem_card(item: dict[str, Any], is_mine: bool = False) -> None:
    class_group = " ".join(p for p in [item.get("classCode"), item.get("groupName")] if p) or "조 정보 없음"
    members = item.get("members", "")
    conds = " + ".join(item.get("probConds") or []) or "—"
    border = "#3A8BAF" if is_mine else "rgba(255,255,255,.75)"
    badge = '<span class="status-done">우리 조</span>' if is_mine else '<span class="status-progress">다른 조</span>'
    st.markdown(
        f"<div class='mini-card' style='border-color:{border};'>"
        f"<div style='display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:8px;'>"
        f"<strong>{html.escape(class_group)}{(' · ' + html.escape(members)) if members else ''}</strong>"
        f"{badge}</div>"
        f"<div style='font-size:.9rem;line-height:1.75;font-weight:700;margin-bottom:8px;white-space:pre-wrap;'>{html.escape(item.get('probStatement', ''))}</div>"
        f"<div class='small-muted'>선택 조건: {html.escape(conds)}</div></div>",
        unsafe_allow_html=True,
    )


def render_step5() -> None:
    st.markdown(
        '<div class="card">'
        '<div class="eyebrow">STEP 05 · 활동 결과 발표하기</div>'
        '<div class="card-title">우리 조의 활동 결과 공유</div>'
        '<div class="card-desc">조별로 만든 문제에 대해서 학급 전체와 공유해봅시다.</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        top_l, top_r = st.columns([3, 1])
        top_l.markdown("#### 🧩 다른 조가 만든 문제")
        if top_r.button("새로고침", use_container_width=True):
            st.rerun()
        own = collect_data(False)
        if own.get("probStatement"):
            render_problem_card(own, is_mine=True)
        my_class = normalize_class_code(text_key("w_classCode"))
        my_group = normalize_group_name(text_key("w_groupName"))
        peers = []
        for item in get_problem_board(text_key("w_classCode")):
            if item.get("sessionId") == st.session_state["session_id"]:
                continue
            if normalize_group_name(item.get("groupName", "")) == my_group:
                continue
            if normalize_class_code(item.get("classCode", "")) == my_class:
                peers.append(item)
        peers.sort(key=group_sort_key)
        if not own.get("probStatement") and not peers:
            st.caption("아직 표시할 문제가 없습니다. Step 4에서 문제를 작성한 뒤 다음 단계로 넘어오면 이곳에 표시됩니다.")
        elif not peers:
            st.caption(f"{text_key('w_classCode')}에서 아직 다른 조 문제가 없습니다.")
        else:
            st.caption(f"{text_key('w_classCode')}에서 다른 조 문제 {len(peers)}개를 불러왔습니다.")
            for item in peers:
                render_problem_card(item)
    st.text_area("🎤 발표할 내용 정리", key="w_present_content", placeholder="우리 조의 플레이리스트, 흥미로웠던 조건, 계산 결과, 만든 문제를 간단히 정리하세요.", height=120)
    st.text_area("💡 가장 흥미로웠던 점 / 발견한 것", key="w_present_finding", placeholder="여러 조건 중 어떤 것이 가장 인상적이었나요? 예상과 달랐던 결과가 있었나요?", height=100)
    st.text_area("🔍 다른 조의 발표를 듣고 — 새롭게 알게 된 것", key="w_present_learned", placeholder="다른 조의 발표에서 배운 점, 우리 조와 다른 풀이 전략 등을 기록하세요.", height=100)
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(4, 6)


# ── Step 6 ────────────────────────────────────────────────────────────────────

def render_summary_area() -> None:
    songs = [song for song in get_songs() if song["title"]]
    song_text = " / ".join(f"{s['label']}: {s['title']}" for s in songs)
    st.markdown(
        f"<div class='mini-card'><span class='small-muted'>이름</span><br><strong>{html.escape(text_key('w_studentName'))}</strong></div>"
        f"<div class='mini-card'><span class='small-muted'>반/조</span><br><strong>{html.escape(text_key('w_classCode'))} {html.escape(text_key('w_groupName'))}</strong></div>"
        f"<div class='mini-card'><span class='small-muted'>조원</span><br><strong>{html.escape(text_key('w_members'))}</strong></div>"
        f"<div class='mini-card'><span class='small-muted'>선택 곡</span><br>{html.escape(song_text)}</div>",
        unsafe_allow_html=True,
    )


def submit_all() -> None:
    if not validate_step(6):
        return
    data = collect_data(True)
    data["currentStep"] = 6
    data["resumeStep"] = 6
    result = upsert_session(st.session_state["session_id"], data)
    if result.get("success"):
        st.session_state["submitted_done"] = True
        st.rerun()
    else:
        st.error(f"제출 오류: {result.get('error', '알 수 없는 오류')}")


def render_step6() -> None:
    if st.session_state.get("submitted_done"):
        st.markdown(
            '<div class="card"><div class="success-wrap">'
            '<div class="success-icon">🎉</div>'
            '<div class="success-title">제출 완료!</div>'
            '<div class="small-muted">오늘 수업은 여기까지!<br>모두 수고했습니다😊</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="card">'
        '<div class="eyebrow">STEP 06 · 순열 조건 정리 및 제출</div>'
        '<div class="card-title">오늘의 학습 마무리하기</div>'
        '<div class="card-desc">오늘 활동을 통해 배운 내용을 정리해봅시다.</div>',
        unsafe_allow_html=True,
    )
    st.text_area("📌 순열을 사용하는 상황의 핵심 특징은 무엇인가요?", key="w_summary_when", placeholder="오늘 활동을 통해 깨달은 것을 바탕으로, 순열로 모델링할 수 있는 상황의 특징을 정리해보세요.", height=130)
    st.text_area("💬 오늘 활동에서 배운 것 / 어려웠던 점", key="w_summary_reflect", placeholder="새롭게 알게 된 것과 어려웠던 부분을 솔직하게 적어주세요.", height=100)
    render_summary_area()
    st.markdown('<div class="divider"></div><div style="font-size:.8rem;font-weight:700;color:var(--md-on-surface-v);margin-bottom:10px;">✅ 자기 점검</div>', unsafe_allow_html=True)
    for cid, label in CHECK_ITEMS:
        st.checkbox(label, key=f"w_check_{cid}")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    submit_col, _ = st.columns([1, 1])
    with submit_col:
        if st.button("📤 활동지 제출하기", type="primary", use_container_width=True):
            submit_all()
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(5, None)


# ── Student app ───────────────────────────────────────────────────────────────

def render_student_app() -> None:
    if not st.session_state.get("activity_ready"):
        render_start()
        return
    if st.session_state.get("restore_notice"):
        st.toast(st.session_state.pop("restore_notice"))
    render_header()
    progress_bar()
    step = int(st.session_state.get("step", 1))
    if step == 1:
        render_step1()
    elif step == 2:
        render_step2()
    elif step == 3:
        render_step3()
    elif step == 4:
        render_step4()
    elif step == 5:
        render_step5()
    elif step == 6:
        render_step6()
    save_current_progress(silent=True)


# ── Teacher dashboard ─────────────────────────────────────────────────────────

def format_time(value: Any) -> str:
    if not value:
        return "—"
    return str(value).replace("T", " ")[:16]


def condition_progress(item: dict[str, Any]) -> tuple[int, int]:
    cond_filled = 0
    cond_total = 14
    cd = item.get("conditionsData") or {}
    if cd.get("totalFormula"):
        cond_filled += 1
    for gid in GROUP_ORDER:
        for cond in (cd.get("groups") or {}).get(gid, []) or []:
            if cond.get("formula") or cond.get("question"):
                cond_filled += 1
    return cond_filled, cond_total


def csv_export(items: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["최종수정", "이름", "반/조", "현재단계", "선택조건", "경우의수", "풀이과정", "전체데이터", "세션ID", "제출여부"])
    for item in items:
        writer.writerow([
            item.get("updatedAt", ""),
            item.get("studentName", ""),
            f"{item.get('classCode', '')} {item.get('groupName', '')}".strip(),
            item.get("currentStep", 1),
            " + ".join(item.get("probConds") or []),
            item.get("probFormula", ""),
            item.get("probExplain", ""),
            json.dumps(item, ensure_ascii=False),
            item.get("sessionId", ""),
            "제출완료" if item.get("submitted") else "진행중",
        ])
    return output.getvalue()


def render_student_detail(item: dict[str, Any]) -> None:
    songs = [s for s in item.get("songs", []) if s.get("title")]
    cd = item.get("conditionsData") or {}
    st.markdown("##### 📖 순열 복습")
    blanks = item.get("blanks") or {}
    if blanks:
        cols = st.columns(3)
        for idx, (key, label) in enumerate(BLANK_FIELDS):
            cols[idx % 3].markdown(f"**{label}**: {blanks.get(key) or '(미작성)'}")
    choice = item.get("review2Choice") or item.get("review2choice") or ""
    st.write("오늘의 질문:", "예" if choice == "yes" else "아니오" if choice == "no" else "(미작성)")

    st.markdown("##### 🎵 선택한 7곡")
    chips = " ".join(
        f"<span style='display:inline-flex;align-items:center;gap:6px;background:rgba(169,207,224,.22);border:1px solid rgba(127,184,212,.3);border-radius:8px;padding:4px 10px;margin:2px;font-size:.78rem;'>"
        f"<strong style='color:var(--lb2);'>{html.escape(s.get('label',''))}</strong> {html.escape(s.get('title',''))}"
        f"<span style='color:var(--md-on-surface-v);font-size:.7rem;'> · {html.escape(s.get('artist','') or '—')}</span></span>"
        for s in songs
    )
    st.markdown(chips or "(없음)", unsafe_allow_html=True)

    st.markdown("##### 🔢 전체 경우의 수")
    c1, c2 = st.columns(2)
    c1.write(f"식: {cd.get('totalFormula') or '(미작성)'}")
    c2.write(f"이유: {cd.get('totalExplain') or '(미작성)'}")

    st.markdown("##### 📐 제한조건별 경우의 수")
    for gid in GROUP_ORDER:
        meta = COND_META.get(gid)
        if not meta:
            continue
        with st.expander(meta["title"], expanded=False):
            for row in (cd.get("groups") or {}).get(gid, []) or []:
                cid = row.get("id")
                label = meta["items"].get(cid, cid)
                num = COND_NUMS.get(cid, "")
                inputs = row.get("inputs") or {}
                selected = " / ".join(str(v) for v in inputs.values() if v)
                st.markdown(f"**{num}번. {label}**")
                if selected:
                    st.caption(f"선택: {selected}")
                if row.get("question"):
                    st.warning("질문으로 표시됨")
                else:
                    c1, c2 = st.columns(2)
                    c1.write(f"식: {row.get('formula') or '(미작성)'}")
                    c2.write(f"이유: {row.get('explain') or '(미작성)'}")

    st.markdown("##### 🛠 나만의 문제 만들기")
    st.write("선택한 조건:", " + ".join(item.get("probConds") or []) or "—")
    st.write("만든 문제:", item.get("probStatement") or "(미작성)")
    st.write("경우의 수 식:", item.get("probFormula") or "(미작성)")
    st.write("풀이 및 이유:", item.get("probExplain") or "(미작성)")

    st.markdown("##### 🎤 발표 내용")
    st.write("발표 내용 정리:", item.get("presentContent") or "(미작성)")
    st.write("가장 흥미로웠던 점:", item.get("presentFinding") or "(미작성)")
    st.write("다른 조에서 배운 것:", item.get("presentLearned") or "(미작성)")

    st.markdown("##### 📌 순열 조건 정리")
    st.write("순열을 사용하는 상황의 특징:", item.get("summaryWhen") or "(미작성)")
    st.write("배운 것 / 어려웠던 점:", item.get("summaryReflect") or "(미작성)")


def render_teacher_dashboard() -> None:
    teacher_password = secret_value("TEACHER_PASSWORD", DEFAULT_TEACHER_PASSWORD)

    if not st.session_state.get("teacher_authenticated"):
        # PW 입력 모달 스타일
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            st.markdown(
                """
                <div style="background:var(--glass-bg-s);-webkit-backdrop-filter:saturate(180%) blur(20px);backdrop-filter:saturate(180%) blur(20px);border:1px solid var(--glass-border);border-radius:var(--r-xl);padding:30px 26px;text-align:center;box-shadow:var(--shadow-lg),inset 0 1px 0 rgba(255,255,255,.82);margin-top:80px;">
                  <div style="font-size:2rem;margin-bottom:12px;">🔐</div>
                  <div style="font-size:1.1rem;font-weight:800;margin-bottom:5px;">교사용 대시보드</div>
                  <div style="font-size:.8rem;color:var(--md-on-surface-v);margin-bottom:22px;line-height:1.65;">교사용 비밀번호를 입력하세요.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            pw = st.text_input("비밀번호", type="password", label_visibility="collapsed", placeholder="비밀번호")
            if st.button("입장하기 →", type="primary", use_container_width=True):
                if pw == teacher_password:
                    st.session_state["teacher_authenticated"] = True
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
            if st.button("← 학생용 화면으로", use_container_width=True):
                set_query_page("student")
                st.rerun()
        return

    # ── 헤더 ──
    st.markdown(
        """
        <div class="app-header" style="margin-bottom:16px;">
          <div style="display:flex;align-items:center;gap:10px;">
            <div class="hdr-icon" style="background:linear-gradient(135deg,var(--lb2),var(--sage2));">📊</div>
            <div>
              <div class="hdr-title">교사용 대시보드 — 플레이리스트로 순열 살펴보기</div>
              <div class="hdr-sub">공통수학Ⅰ - 순열을 활용한 플레이리스트 만들기 - 학생 제출 현황</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_items = get_submissions()
    total = len(all_items)
    submitted_count = len([x for x in all_items if x.get("submitted")])
    in_progress = total - submitted_count
    avg_step = sum(int(x.get("currentStep") or 1) for x in all_items) / total if total else 0

    # ── 통계 카드 ──
    c1, c2, c3, c4 = st.columns(4)
    for col, num, label in [
        (c1, str(total), "총 접속 수"),
        (c2, str(submitted_count), "제출 완료"),
        (c3, str(in_progress), "진행 중"),
        (c4, f"{avg_step:.1f}단계" if total else "—", "평균 진행 단계"),
    ]:
        col.markdown(
            f"<div class='stat-card'><div class='stat-n'>{num}</div><div class='stat-l'>{label}</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 필터 ──
    with st.container(border=True):
        f1, f2, f3, f4, f5 = st.columns([2, 1, 1, 1, 1])
        name_filter = f1.text_input("이름 검색", placeholder="이름 검색...", label_visibility="collapsed")
        class_filter = f2.selectbox("반", [""] + CLASSES, format_func=lambda x: x or "전체 반", label_visibility="collapsed")
        group_filter = f3.selectbox("조", [""] + GROUPS, format_func=lambda x: x or "전체 조", label_visibility="collapsed")
        status_filter = f4.selectbox("상태", ["", "done", "progress"], format_func=lambda x: {"": "전체 상태", "done": "제출완료", "progress": "진행중"}[x], label_visibility="collapsed")
        if f5.button("↻ 지금 갱신", use_container_width=True):
            st.rerun()
        auto_refresh = st.toggle("🔄 8초 자동 갱신", value=False)
        if auto_refresh:
            components.html("<script>setTimeout(() => window.parent.location.reload(), 8000);</script>", height=0)

    # ── 필터 적용 ──
    filtered = []
    for item in all_items:
        status = "done" if item.get("submitted") else "progress"
        if name_filter and name_filter.lower() not in str(item.get("studentName", "")).lower():
            continue
        if class_filter and item.get("classCode") != class_filter:
            continue
        if group_filter and item.get("groupName") != group_filter:
            continue
        if status_filter and status != status_filter:
            continue
        filtered.append(item)

    # ── CSV 다운로드 ──
    if filtered:
        st.download_button(
            "📥 CSV 다운로드",
            data=csv_export(filtered),
            file_name=f"playlist_permutation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=False,
        )

    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;color:var(--md-on-surface-v);">'
            '<div style="font-size:2.8rem;margin-bottom:12px;">📭</div>'
            '<div style="font-size:.875rem;line-height:1.8;">아직 접속한 학생이 없습니다.<br>데이터가 들어오면 자동으로 표시됩니다.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # ── 카드 그리드 (3열) ──
    num_cols = 3
    rows_of_items = [filtered[i:i + num_cols] for i in range(0, len(filtered), num_cols)]
    for row_items in rows_of_items:
        cols = st.columns(num_cols)
        for col, item in zip(cols, row_items):
            with col:
                uid = item.get("sessionId") or f"{item.get('studentName', '')}_{item.get('updatedAt', '')}"
                songs = [s for s in item.get("songs", []) if s.get("title")]
                cond_filled, cond_total = condition_progress(item)
                meta = " ".join(p for p in [item.get("classCode"), item.get("groupName")] if p)
                is_submit = bool(item.get("submitted"))
                step_n = item.get("currentStep", 1)
                status_html = (
                    '<span class="status-done">✅ 제출완료</span>'
                    if is_submit
                    else f'<span class="status-progress">STEP {step_n} 진행중</span>'
                )
                chips_html = "".join(
                    f"<span class='sm-chip'>{html.escape(s['label'])}: {html.escape(s['title'])}</span>"
                    for s in songs[:5]
                )
                prob_preview = (item.get("probStatement") or "—")[:30]
                if len(item.get("probStatement") or "") > 30:
                    prob_preview += "…"

                st.markdown(
                    f"<div class='sub-card'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;'>"
                    f"<div><div class='student-name'>{html.escape(item.get('studentName') or '(이름 없음)')}</div>"
                    f"<div class='student-meta'>{html.escape(meta)}"
                    + (f" · {html.escape(item.get('members', ''))}" if item.get('members') else "")
                    + f"</div></div>{status_html}</div>"
                    f"<div style='display:flex;flex-wrap:wrap;gap:5px;margin-bottom:11px;'>{chips_html}</div>"
                    f"<div class='cond-progress'>📐 경우의 수 계산: <strong>{cond_filled} / {cond_total}문제</strong> 완료</div>"
                    f"<div style='font-size:.75rem;margin-bottom:8px;'><span style='color:var(--md-on-surface-v);'>만든 문제</span> "
                    f"<strong style='font-size:.78rem;'>{html.escape(prob_preview)}</strong></div>"
                    f"<div class='card-time'>{html.escape(format_time(item.get('updatedAt')))}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                with st.expander("📋 상세 보기 / 삭제"):
                    render_student_detail(item)
                    st.divider()
                    confirm_key = f"confirm_del_{uid}"
                    st.checkbox("삭제 확인 (되돌릴 수 없습니다)", key=confirm_key)
                    if st.button("🗑️ 삭제", key=f"del_{uid}", disabled=not bool_key(confirm_key)):
                        result = delete_session(uid)
                        if result.get("success"):
                            st.success("삭제했습니다.")
                            st.rerun()
                        else:
                            st.error(f"삭제 실패: {result.get('error', '알 수 없는 오류')}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    inject_css()
    ensure_runtime()
    page = get_query_page()
    if page == "teacher":
        render_teacher_dashboard()
    else:
        render_student_app()


if __name__ == "__main__":
    main()
