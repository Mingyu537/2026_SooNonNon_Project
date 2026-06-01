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


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');
        :root {
          --lb: #5FA8C8;
          --lb2: #3A8BAF;
          --fg: #3D4A44;
          --fg2: #1E2822;
          --cream: #F0EAE0;
          --sage: #6E9170;
          --surface: rgba(248,246,242,.84);
          --surface-strong: rgba(244,240,232,.92);
          --outline: rgba(61,74,68,.24);
          --success: #2E6B42;
          --warning: #7A5E1A;
          --error: #7A2A2A;
          --shadow: 0 8px 26px rgba(30,40,34,.14);
        }
        html, body, [class*="css"] {
          font-family: "Noto Sans KR", sans-serif;
        }
        .stApp {
          background:
            radial-gradient(ellipse 75% 60% at 8% 0%, rgba(169,207,224,.55) 0%, transparent 55%),
            radial-gradient(ellipse 65% 55% at 92% 8%, rgba(181,196,177,.50) 0%, transparent 50%),
            radial-gradient(ellipse 70% 55% at 92% 80%, rgba(181,196,177,.42) 0%, transparent 50%),
            linear-gradient(160deg, var(--cream) 0%, #EEE9E0 40%, #ECF3F5 75%, var(--cream) 100%);
          color: var(--fg2);
        }
        .block-container {
          max-width: 1120px;
          padding-top: 1.6rem;
          padding-bottom: 4rem;
        }
        .glass-card {
          background: var(--surface);
          border: 1px solid rgba(255,255,255,.72);
          border-radius: 22px;
          padding: 24px;
          box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.75);
          margin: 0 0 14px 0;
        }
        .glass-card.compact {
          padding: 18px;
          border-radius: 18px;
        }
        .eyebrow {
          display: inline-flex;
          color: var(--lb2);
          background: rgba(169,207,224,.22);
          border: 1px solid rgba(169,207,224,.35);
          border-radius: 999px;
          padding: 4px 11px;
          font-size: .72rem;
          font-weight: 800;
          letter-spacing: .04em;
          margin-bottom: 10px;
        }
        .title {
          font-size: 1.25rem;
          font-weight: 900;
          line-height: 1.35;
          margin-bottom: 6px;
        }
        .desc {
          color: var(--fg);
          font-size: .92rem;
          line-height: 1.75;
          margin-bottom: 12px;
        }
        .splash {
          min-height: 72vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          gap: 12px;
        }
        .splash h1 {
          font-size: clamp(2.4rem, 6vw, 4.2rem);
          line-height: 1.15;
          letter-spacing: 0;
          margin: 0;
          color: var(--fg2);
        }
        .splash .chip {
          background: rgba(255,255,255,.42);
          border: 1px solid rgba(255,255,255,.55);
          border-radius: 999px;
          padding: 6px 16px;
          font-size: .78rem;
          font-weight: 800;
          color: var(--fg2);
        }
        .progress-wrap {
          background: var(--surface-strong);
          border: 1px solid rgba(255,255,255,.72);
          border-radius: 20px;
          padding: 14px 16px;
          box-shadow: 0 4px 16px rgba(96,111,105,.08);
          margin-bottom: 16px;
        }
        .progress-row {
          display: grid;
          grid-template-columns: repeat(6, minmax(0, 1fr));
          gap: 8px;
        }
        .step-pill {
          border-radius: 14px;
          padding: 10px 8px;
          text-align: center;
          font-size: .78rem;
          font-weight: 800;
          border: 1px solid var(--outline);
          background: rgba(255,255,255,.45);
          color: var(--fg);
        }
        .step-pill.active {
          background: linear-gradient(135deg, var(--lb), var(--sage));
          color: #fff;
          border-color: rgba(255,255,255,.7);
        }
        .step-pill.done {
          color: var(--success);
          background: rgba(46,107,66,.12);
        }
        .warn-box, .tip-box {
          background: rgba(122,94,26,.12);
          border: 1px solid rgba(122,94,26,.22);
          border-radius: 16px;
          padding: 14px 16px;
          line-height: 1.7;
          margin-bottom: 14px;
          color: var(--fg2);
        }
        .tip-box {
          background: rgba(58,139,175,.13);
          border-color: rgba(58,139,175,.24);
        }
        .mini-card {
          background: rgba(255,255,255,.62);
          border: 1px solid rgba(255,255,255,.75);
          border-radius: 14px;
          padding: 13px 14px;
          margin-bottom: 8px;
        }
        .song-chip {
          display: inline-block;
          background: rgba(169,207,224,.28);
          border: 1px solid rgba(127,184,212,.34);
          color: var(--lb2);
          border-radius: 8px;
          padding: 4px 9px;
          margin: 0 5px 5px 0;
          font-size: .78rem;
          font-weight: 700;
        }
        .status-done, .status-progress {
          display: inline-block;
          border-radius: 999px;
          padding: 4px 10px;
          font-size: .74rem;
          font-weight: 800;
        }
        .status-done {
          color: var(--success);
          background: rgba(46,107,66,.14);
        }
        .status-progress {
          color: var(--warning);
          background: rgba(122,94,26,.14);
        }
        .condition-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 28px;
          height: 28px;
          border-radius: 50%;
          color: #fff;
          font-weight: 900;
          margin-right: 8px;
        }
        div[data-testid="stMetric"] {
          background: var(--surface);
          border: 1px solid rgba(255,255,255,.72);
          border-radius: 18px;
          padding: 12px 14px;
          box-shadow: 0 2px 10px rgba(30,40,34,.10);
        }
        .small-muted {
          color: var(--fg);
          font-size: .82rem;
          line-height: 1.65;
        }
        div[data-testid="stTextInput"]:has(input[aria-label^="blank__"]) {
          display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
        params = st.experimental_get_query_params()
        raw = params.get("page", ["student"])
        return raw[0] if raw else "student"


def set_query_page(page: str) -> None:
    try:
        st.query_params["page"] = page
    except Exception:
        st.experimental_set_query_params(page=page)


def ensure_runtime() -> None:
    st.session_state.setdefault("session_id", f"sid_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}")
    st.session_state.setdefault("activity_ready", False)
    st.session_state.setdefault("step", 1)
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
    labels = [song["label"] for song in get_songs() if song["title"]]
    return [""] + labels


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
            item = {
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
    component_html = """
    <style>
      :root {
        --lb: #5FA8C8;
        --lb2: #3A8BAF;
        --fg: #3D4A44;
        --fg2: #1E2822;
        --cream: #F0EAE0;
        --sage: #6E9170;
        --outline: rgba(61,74,68,.24);
        --shadow: 0 8px 22px rgba(30,40,34,.10);
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        color: var(--fg2);
        font-family: "Noto Sans KR", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .perm-drag-app {
        padding: 2px 2px 16px;
      }
      .word-bank {
        min-height: 86px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        padding: 13px;
        margin-bottom: 15px;
        border: 1px dashed rgba(58,139,175,.48);
        border-radius: 14px;
        background: rgba(169,207,224,.16);
      }
      .word-bank.over {
        background: rgba(169,207,224,.28);
        border-color: var(--lb2);
      }
      .concept-lines {
        display: grid;
        gap: 10px;
        padding: 2px 0;
      }
      .concept-line {
        margin: 0;
        padding: 12px 13px;
        border: 1px solid rgba(255,255,255,.70);
        border-radius: 14px;
        background: rgba(255,255,255,.56);
        box-shadow: 0 2px 10px rgba(30,40,34,.06);
        line-height: 1.75;
        word-break: keep-all;
      }
      .word-chip {
        appearance: none;
        border: 1px solid rgba(58,139,175,.34);
        border-radius: 999px;
        background: rgba(255,255,255,.86);
        color: var(--fg2);
        cursor: grab;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 34px;
        max-width: 100%;
        padding: 6px 12px;
        font: inherit;
        font-size: 14px;
        font-weight: 800;
        line-height: 1.25;
        box-shadow: 0 2px 8px rgba(30,40,34,.08);
        touch-action: none;
        user-select: none;
        white-space: normal;
      }
      .word-chip:active {
        cursor: grabbing;
      }
      .word-chip.dragging {
        opacity: .48;
      }
      .drop-zone {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
        min-width: 136px;
        min-height: 38px;
        max-width: 100%;
        margin: 0 4px;
        padding: 3px 8px;
        border: 2px dashed rgba(61,74,68,.26);
        border-radius: 12px;
        background: rgba(255,255,255,.46);
        color: rgba(61,74,68,.64);
        font-size: 13px;
        font-weight: 800;
        line-height: 1.3;
      }
      .drop-zone.over {
        border-color: var(--lb2);
        background: rgba(169,207,224,.26);
      }
      .drop-zone.filled {
        border-style: solid;
        border-color: rgba(58,139,175,.38);
        background: rgba(255,255,255,.70);
        color: var(--fg2);
      }
      .drop-zone.filled .word-chip {
        width: 100%;
        min-height: 30px;
        border-color: transparent;
        background: transparent;
        box-shadow: none;
        padding: 3px 2px;
      }
      .sync-status {
        min-height: 18px;
        margin-top: 8px;
        color: #7A2A2A;
        font-size: 12px;
        font-weight: 700;
      }
      .touch-clone {
        position: fixed;
        left: 0;
        top: 0;
        z-index: 9999;
        pointer-events: none;
        opacity: .92;
        transform: translate(-50%, -50%);
      }
      @media (max-width: 640px) {
        .word-bank { padding: 10px; }
        .concept-line { padding: 10px; }
        .drop-zone {
          min-width: 104px;
          margin: 3px 2px;
        }
        .word-chip {
          font-size: 13px;
          padding: 6px 10px;
        }
      }
    </style>

    <div class="perm-drag-app">
      <div id="perm-word-bank" class="word-bank" aria-label="보기"></div>
      <div class="concept-lines">
        <p class="concept-line">
          서로 다른 <b>n</b>개에서 <b>r</b>(0&lt;r≤n)개를 택하여 일렬로 나열하는 것을
          <span class="drop-zone" data-key="def1"></span>이라 하고, 이 순열의 가짓수를
          <span class="drop-zone" data-key="def2"></span>로 나타냅니다.
        </p>
        <p class="concept-line">
          <b>nPr</b> =
          <span class="drop-zone" data-key="npr"></span>
        </p>
        <p class="concept-line">
          <b>nPn</b> =
          <span class="drop-zone" data-key="pnn"></span>
          =
          <span class="drop-zone" data-key="pnnExpand"></span>
        </p>
        <p class="concept-line">
          <b>nP0</b> =
          <span class="drop-zone" data-key="p0"></span>,
          <b>0!</b> =
          <span class="drop-zone" data-key="fac0"></span>
        </p>
        <p class="concept-line">
          <b>nPr</b> =
          <span class="drop-zone" data-key="fact"></span>,
          조건:
          <span class="drop-zone" data-key="cond"></span>
        </p>
      </div>
      <div id="sync-status" class="sync-status"></div>
    </div>

    <script>
      (() => {
        const WORDS = __WORDS__;
        const FIELDS = __FIELDS__;
        const INITIAL_BLANKS = __BLANKS__;
        const byId = new Map(WORDS.map((word) => [word.id, word]));
        const order = WORDS.map((word) => word.id);
        const state = {};
        let draggingId = null;
        let touchId = null;
        let touchClone = null;
        let pointerId = null;

        function fieldLabel(key) {
          return "빈칸";
        }

        function zoneForWord(id) {
          return Object.keys(state).find((key) => state[key] && state[key].id === id);
        }

        function clearWord(id) {
          const key = zoneForWord(id);
          if (key) {
            delete state[key];
          }
        }

        function assignWord(id, key) {
          if (!id || !byId.has(id)) {
            return;
          }
          clearWord(id);
          if (state[key]) {
            delete state[key];
          }
          const word = byId.get(id);
          state[key] = { id: word.id, text: word.text };
          render();
        }

        function setParentInput(key, value) {
          try {
            const doc = window.parent.document;
            const input = doc.querySelector(`input[aria-label="blank__${key}"]`);
            if (!input) {
              return false;
            }
            if (input.value === value) {
              return true;
            }
            const setter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
            setter.call(input, value);
            input.dispatchEvent(new window.parent.Event("input", { bubbles: true }));
            input.dispatchEvent(new window.parent.Event("change", { bubbles: true }));
            return true;
          } catch (error) {
            return false;
          }
        }

        function syncAll() {
          const failed = FIELDS.some((field) => {
            const value = state[field.key] ? state[field.key].text : "";
            return !setParentInput(field.key, value);
          });
          document.getElementById("sync-status").textContent = failed
            ? "빈칸 저장 동기화가 지연되고 있습니다. 페이지를 새로고침한 뒤 다시 시도하세요."
            : "";
        }

        function makeChip(word, inZone) {
          const chip = document.createElement("button");
          chip.type = "button";
          chip.className = "word-chip";
          chip.draggable = true;
          chip.dataset.id = word.id;
          chip.textContent = word.text;
          chip.addEventListener("dragstart", (event) => {
            draggingId = word.id;
            chip.classList.add("dragging");
            event.dataTransfer.effectAllowed = "move";
            event.dataTransfer.setData("text/plain", word.id);
          });
          chip.addEventListener("dragend", () => {
            draggingId = null;
            chip.classList.remove("dragging");
          });
          chip.addEventListener("pointerdown", pointerStart);
          chip.addEventListener("touchstart", touchStart, { passive: false });
          if (inZone) {
            chip.addEventListener("click", () => {
              clearWord(word.id);
              render();
            });
          }
          return chip;
        }

        function renderBank() {
          const bank = document.getElementById("perm-word-bank");
          const usedIds = new Set(Object.values(state).map((item) => item.id));
          bank.innerHTML = "";
          order
            .filter((id) => !usedIds.has(id))
            .forEach((id) => bank.appendChild(makeChip(byId.get(id), false)));
        }

        function renderZones() {
          document.querySelectorAll(".drop-zone").forEach((zone) => {
            const key = zone.dataset.key;
            zone.innerHTML = "";
            zone.classList.remove("filled");
            const item = state[key];
            if (item && byId.has(item.id)) {
              zone.classList.add("filled");
              zone.appendChild(makeChip(byId.get(item.id), true));
            } else {
              zone.textContent = fieldLabel(key);
            }
          });
        }

        function render() {
          renderBank();
          renderZones();
          syncAll();
        }

        function restoreInitial() {
          const usedIds = new Set();
          FIELDS.forEach((field) => {
            const text = INITIAL_BLANKS[field.key] || "";
            if (!text) {
              return;
            }
            let word = WORDS.find((item) => item.text === text && !usedIds.has(item.id));
            if (!word) {
              word = { id: `custom-${field.key}`, text };
              byId.set(word.id, word);
            }
            usedIds.add(word.id);
            state[field.key] = { id: word.id, text: word.text };
          });
        }

        function eventWordId(event) {
          return event.dataTransfer.getData("text/plain") || draggingId;
        }

        function bindDrops() {
          const bank = document.getElementById("perm-word-bank");
          bank.addEventListener("dragover", (event) => {
            event.preventDefault();
            bank.classList.add("over");
          });
          bank.addEventListener("dragleave", () => bank.classList.remove("over"));
          bank.addEventListener("drop", (event) => {
            event.preventDefault();
            bank.classList.remove("over");
            clearWord(eventWordId(event));
            render();
          });

          document.querySelectorAll(".drop-zone").forEach((zone) => {
            zone.addEventListener("dragover", (event) => {
              event.preventDefault();
              zone.classList.add("over");
            });
            zone.addEventListener("dragleave", () => zone.classList.remove("over"));
            zone.addEventListener("drop", (event) => {
              event.preventDefault();
              zone.classList.remove("over");
              assignWord(eventWordId(event), zone.dataset.key);
            });
            zone.addEventListener("click", (event) => {
              if (event.target.closest(".word-chip")) {
                return;
              }
              if (state[zone.dataset.key]) {
                delete state[zone.dataset.key];
                render();
              }
            });
          });
        }

        function moveCloneTo(x, y) {
          if (!touchClone) {
            return;
          }
          touchClone.style.left = `${x}px`;
          touchClone.style.top = `${y}px`;
        }

        function moveTouchClone(touch) {
          moveCloneTo(touch.clientX, touch.clientY);
        }

        function cleanupTouch() {
          window.removeEventListener("touchmove", touchMove);
          if (touchClone) {
            touchClone.remove();
          }
          touchClone = null;
          touchId = null;
        }

        function cleanupPointer() {
          window.removeEventListener("pointermove", pointerMove);
          if (touchClone) {
            touchClone.remove();
          }
          touchClone = null;
          touchId = null;
          pointerId = null;
        }

        function pointerStart(event) {
          if (event.button !== 0 || touchId) {
            return;
          }
          event.preventDefault();
          pointerId = event.pointerId;
          touchId = event.currentTarget.dataset.id;
          draggingId = touchId;
          touchClone = event.currentTarget.cloneNode(true);
          touchClone.classList.add("touch-clone");
          document.body.appendChild(touchClone);
          moveCloneTo(event.clientX, event.clientY);
          window.addEventListener("pointermove", pointerMove);
          window.addEventListener("pointerup", pointerEnd, { once: true });
          window.addEventListener("pointercancel", cleanupPointer, { once: true });
        }

        function pointerMove(event) {
          if (pointerId !== null && event.pointerId !== pointerId) {
            return;
          }
          event.preventDefault();
          moveCloneTo(event.clientX, event.clientY);
        }

        function pointerEnd(event) {
          if (pointerId !== null && event.pointerId !== pointerId) {
            return;
          }
          event.preventDefault();
          const element = document.elementFromPoint(event.clientX, event.clientY);
          const zone = element && element.closest(".drop-zone");
          const bank = element && element.closest("#perm-word-bank");
          const id = touchId;
          cleanupPointer();
          if (zone) {
            assignWord(id, zone.dataset.key);
          } else if (bank) {
            clearWord(id);
            render();
          }
          draggingId = null;
        }

        function touchStart(event) {
          if (event.touches.length !== 1 || touchId) {
            return;
          }
          event.preventDefault();
          touchId = event.currentTarget.dataset.id;
          draggingId = touchId;
          touchClone = event.currentTarget.cloneNode(true);
          touchClone.classList.add("touch-clone");
          document.body.appendChild(touchClone);
          moveTouchClone(event.touches[0]);
          window.addEventListener("touchmove", touchMove, { passive: false });
          window.addEventListener("touchend", touchEnd, { passive: false, once: true });
          window.addEventListener("touchcancel", cleanupTouch, { passive: false, once: true });
        }

        function touchMove(event) {
          event.preventDefault();
          moveTouchClone(event.touches[0]);
        }

        function touchEnd(event) {
          event.preventDefault();
          const touch = event.changedTouches[0];
          const element = document.elementFromPoint(touch.clientX, touch.clientY);
          const zone = element && element.closest(".drop-zone");
          const bank = element && element.closest("#perm-word-bank");
          const id = touchId;
          cleanupTouch();
          if (zone) {
            assignWord(id, zone.dataset.key);
          } else if (bank) {
            clearWord(id);
            render();
          }
          draggingId = null;
        }

        restoreInitial();
        bindDrops();
        render();
      })();
    </script>
    """
    component_html = (
        component_html.replace("__WORDS__", words_json)
        .replace("__FIELDS__", fields_json)
        .replace("__BLANKS__", blanks_json)
    )
    components.html(component_html, height=520, scrolling=False)


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
        hydrate_from_data(data, force=True)
        st.session_state["restore_notice"] = "이전에 작성하던 기록을 불러왔습니다."
    else:
        st.session_state["step"] = 1
        hydrate_from_data(
            {
                "studentName": name,
                "classCode": cls,
                "groupName": group,
                "members": members,
            },
            force=True,
        )
        st.session_state["restore_notice"] = "새 활동을 시작합니다."
    save_current_progress(silent=True)
    st.rerun()


def progress_bar() -> None:
    current = int(st.session_state.get("step", 1))
    pills = []
    for idx, label in enumerate(STEP_LABELS, start=1):
        klass = "active" if idx == current else "done" if idx < current else ""
        prefix = "✓" if idx < current else str(idx)
        pills.append(f'<div class="step-pill {klass}">{prefix}<br>{html.escape(label)}</div>')
    st.markdown(
        f'<div class="progress-wrap"><div class="progress-row">{"".join(pills)}</div></div>',
        unsafe_allow_html=True,
    )


def card_start(eyebrow: str, title: str, desc: str | None = None, compact: bool = False) -> None:
    klass = "glass-card compact" if compact else "glass-card"
    desc_html = f'<div class="desc">{desc}</div>' if desc else ""
    st.markdown(
        f"""
        <div class="{klass}">
          <div class="eyebrow">{html.escape(eyebrow)}</div>
          <div class="title">{html.escape(title)}</div>
          {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def plain_cond_sentence(cond: dict[str, Any]) -> str:
    result = ""
    type_idx = 0
    for part in cond["parts"]:
        result += part
        if type_idx < len(cond["types"]):
            t = cond["types"][type_idx]
            if t == "song":
                result += "[곡 선택]"
            elif t == "num":
                result += "[자리/개수]"
            elif t == "trait":
                result += "[곡의 특징]"
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
            if not text_key(f"w_cond_{cond['id']}_formula") or not text_key(
                f"w_cond_{cond['id']}_explain"
            ):
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
    st.rerun()


def nav_buttons(prev_step: int | None, next_step: int | None, next_label: str = "다음 단계") -> None:
    left, right = st.columns([1, 1])
    with left:
        if prev_step is not None and st.button("← 이전", use_container_width=True):
            navigate(prev_step)
    with right:
        if next_step is not None and st.button(f"{next_label} →", type="primary", use_container_width=True):
            navigate(next_step)


def render_start() -> None:
    st.markdown(
        """
        <div class="splash">
          <div class="chip">공통수학Ⅰ · 경우의 수</div>
          <div style="font-size:3.4rem;">🎵</div>
          <h1>플레이리스트로<br>순열 살펴보기</h1>
          <div class="desc">같은 곡, 다른 순서<br>플레이리스트로 순열을 알아봅시다</div>
          <div class="small-muted">made by mingyu kim</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.subheader("활동을 시작하기 전에")
        st.caption("아래 정보를 모두 입력해야 활동을 시작할 수 있어요.")
        name = st.text_input("이름", placeholder="홍길동", key="start_name")
        col1, col2 = st.columns(2)
        with col1:
            cls = st.selectbox("반", [""] + CLASSES, format_func=lambda x: x or "반 선택", key="start_class")
        with col2:
            group = st.selectbox("조", [""] + GROUPS, format_func=lambda x: x or "조 선택", key="start_group")
        members = st.text_input("조원 이름", placeholder="카리나, 윈터, 닝닝, 지젤", key="start_members")

        col_a, col_b = st.columns(2)
        with col_a:
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
        with col_b:
            if st.button("🔐 교사용 대시보드", use_container_width=True):
                set_query_page("teacher")
                st.rerun()


def render_header() -> None:
    name = text_key("w_studentName")
    cls = text_key("w_classCode")
    group = text_key("w_groupName")
    st.markdown(
        f"""
        <div class="glass-card compact">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
            <div style="display:flex;align-items:center;gap:12px;">
              <div style="width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,#5FA8C8,#6E9170);display:flex;align-items:center;justify-content:center;">🎵</div>
              <div>
                <div style="font-weight:900;">플레이리스트로 순열 살펴보기</div>
                <div class="small-muted">{html.escape(name)} · {html.escape(cls)} {html.escape(group)}</div>
              </div>
            </div>
            <div class="status-progress">자동 저장</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step1() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 01-1 · 오늘의 질문</div>', unsafe_allow_html=True)
    st.subheader("플레이리스트에서 곡의 순서를 바꾸면 다른 플레이리스트일까요?")
    st.radio(
        "답을 선택하세요.",
        ["", "yes", "no"],
        format_func=lambda v: "선택 안 함" if not v else "✅ 예" if v == "yes" else "❌ 아니오",
        horizontal=True,
        key="w_review2Choice",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 01-1 · 학습목표</div>', unsafe_allow_html=True)
    st.subheader("오늘 활동에서 배울 것들")
    st.markdown(
        """
        <div class="mini-card">① 순열의 개념을 이해하고, 곡의 순서가 중요한 플레이리스트 배열 상황을 순열로 해석할 수 있다.</div>
        <div class="mini-card">② 조별로 선택한 곡으로 제한조건을 만족하는 플레이리스트 배열의 경우의 수를 구하고, 그 풀이 과정을 논리적으로 설명할 수 있다.</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 01-2 · 순열 개념 확인</div>', unsafe_allow_html=True)
    st.subheader("순열이란 무엇인가?")
    st.caption("오늘 활동을 시작하기 전, 순열의 핵심 개념을 다시 확인해봅시다.")
    st.markdown(
        """
        <div class="tip-box">
        📝 순열 개념 확인 — &lt;보기&gt;에서 알맞은 표현을 골라 빈칸에 채워보세요.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        서로 다른 $n$개에서 $r\\,(0 < r \\leq n)$개를 택하여 일렬로 나열하는 것을
        $n$개에서 $r$개를 택하는 순열이라 하고, 이 순열의 가짓수를 순열의 수라 하고
        기호로 나타냅니다. 아래 빈칸을 완성하세요.
        """
    )
    render_blank_sync_inputs()
    render_permutation_drag_widget()
    st.info("참고: 기호 $_nP_r$에서 P는 Permutation(순열)의 머리글자입니다.")
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(None, 2)


def render_step2() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 02 · 플레이리스트 구성</div>', unsafe_allow_html=True)
    st.subheader("어떤 플레이리스트를 만들어볼까?")
    st.caption("지금 당장 듣고 싶은 7개의 곡을 직접 선택해봅시다. 멜론, 유튜브 뮤직 등에서 검색하여 곡의 정보를 입력해봅시다.")
    st.markdown(
        '<div class="warn-box">⚠️ <strong>중요:</strong> 오늘의 활동은 7곡 중의 일부를 가지고 배열하는 활동이 아닙니다. '
        '조별로 선택한 <strong>7개의 곡 전체를 조건에 맞춰 순서 있게 배열</strong>하는 활동입니다.</div>',
        unsafe_allow_html=True,
    )
    for idx, label in enumerate(LABELS):
        cols = st.columns([0.5, 2.2, 2.2, 1.6, 1.5])
        cols[0].markdown(f"<div class='song-chip'>{label}</div>", unsafe_allow_html=True)
        cols[1].text_input("곡명", key=f"w_song_title_{idx}", label_visibility="collapsed", placeholder="곡명")
        cols[2].text_input("아티스트", key=f"w_song_artist_{idx}", label_visibility="collapsed", placeholder="아티스트")
        cols[3].selectbox("장르", GENRES, key=f"w_song_genre_{idx}", label_visibility="collapsed")
        cols[4].text_input("곡의 재생 시간", key=f"w_song_time_{idx}", label_visibility="collapsed", placeholder="3:00")
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(1, 3)


def render_song_summary() -> None:
    st.markdown("#### 🎧 선택한 7곡")
    for song in get_songs():
        title = song["title"] or "미입력"
        artist = song["artist"] or "미입력"
        meta = " · ".join(part for part in [artist, song.get("genre"), song.get("tag")] if part)
        st.markdown(
            f"<div class='mini-card'><span class='song-chip'>{html.escape(song['label'])}</span>"
            f"<strong>{html.escape(title)}</strong><br><span class='small-muted'>{html.escape(meta)}</span></div>",
            unsafe_allow_html=True,
        )


def render_condition_inputs(cond: dict[str, Any]) -> None:
    counters = {"song": 0, "num": 0, "trait": 0}
    input_types = cond["types"]
    if input_types:
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
                    st.selectbox(
                        "곡 선택",
                        opts,
                        format_func=song_label,
                        key=widget_key,
                    )
                elif input_type == "num":
                    st.text_input("자리/개수", key=widget_key, placeholder="n")
                else:
                    st.text_input(
                        "곡의 특징",
                        key=widget_key,
                        placeholder="장르가 댄스, 재생 시간이 가장 짧은 곡 등",
                    )
            counters[input_type] += 1


def render_step3() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 03 · 경우의 수 계산하기</div>', unsafe_allow_html=True)
    st.subheader("제한조건을 만족하는 플레이리스트의 수")
    st.caption("먼저 전체 경우의 수를 구한 다음, 각 제한조건을 만족하는 경우의 수를 구해봅시다.")
    st.markdown('<div class="tip-box"><strong>🔢 전체 경우의 수</strong><br>내가 선택한 7곡으로 플레이리스트를 몇 가지 만들 수 있나요?</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.text_area("경우의 수를 구하는 식", key="w_total_formula", placeholder="식을 직접 작성해보세요.", height=90)
    col2.text_area("왜 이 식이 나왔는지 설명해보기", key="w_total_explain", placeholder="이유를 간략하게 설명해보세요", height=90)
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([0.9, 2.4])
    with left:
        render_song_summary()
    with right:
        for group in COND_GROUPS:
            with st.expander(
                f"{group['icon']} {group['title']} · {len(group['conds'])}문제",
                expanded=True,
            ):
                if group.get("note"):
                    st.caption(group["note"])
                for cond in group["conds"]:
                    st.markdown(
                        f"<div class='mini-card'><span class='condition-number' style='background:{group['color']};'>"
                        f"{COND_NUMS[cond['id']]}</span><strong>{html.escape(filled_cond_sentence(cond))}</strong></div>",
                        unsafe_allow_html=True,
                    )
                    render_condition_inputs(cond)
                    st.checkbox("질문으로 표시", key=f"w_cond_{cond['id']}_question")
                    if bool_key(f"w_cond_{cond['id']}_question"):
                        st.info("질문으로 표시한 문제입니다. 이 문제는 답을 작성하지 않아도 다음 단계로 넘어갈 수 있습니다.")
                    cols = st.columns(2)
                    cols[0].text_area(
                        "경우의 수 식",
                        key=f"w_cond_{cond['id']}_formula",
                        placeholder="식을 작성하세요",
                        height=86,
                    )
                    cols[1].text_area(
                        "왜 이 식이 나왔는지 설명해보기",
                        key=f"w_cond_{cond['id']}_explain",
                        placeholder="이유를 간략하게 설명해보세요",
                        height=86,
                    )
                    st.divider()
    nav_buttons(2, 4)


def render_selected_condition_summary() -> None:
    checked = [(cid, label, group_id) for cid, _, label, group_id in PROBLEM_CONDITIONS if bool_key(f"w_prob_{cid}")]
    if not checked:
        return
    st.markdown("#### 📌 선택한 조건 유형 정리")
    for _, label, group_id in checked:
        with st.container(border=True):
            st.markdown(f"**{label}**")
            if group_id == "custom":
                st.write("앞의 유형을 바탕으로 조가 직접 새로운 조건을 추가합니다.")
                continue
            group = next((item for item in COND_GROUPS if item["id"] == group_id), None)
            if group:
                for cond in group["conds"]:
                    st.write(f"{COND_NUMS[cond['id']]}번. {plain_cond_sentence(cond)}")


def render_step4() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 04 · 문제 만들기</div>', unsafe_allow_html=True)
    st.subheader("나만의 순열 문제 설계하기")
    st.caption("앞에서 풀었던 제한조건을 2가지 이상 선택하거나 또 다른 새로운 조건을 추가하여 새로운 문제를 직접 만들어봅시다.")
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
    st.text_area(
        "풀이 과정 및 이유",
        key="w_prob_explain",
        placeholder="왜 이 식을 사용했는지, 어떤 순서로 계산했는지 설명하세요.",
        height=130,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(3, 5)


def group_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    group = item.get("groupName", "")
    digits = "".join(ch for ch in str(group) if ch.isdigit())
    order = int(digits) if digits else 9999
    return order, normalize_group_name(group)


def render_problem_card(item: dict[str, Any], is_mine: bool = False) -> None:
    class_group = " ".join(part for part in [item.get("classCode"), item.get("groupName")] if part) or "조 정보 없음"
    members = item.get("members", "")
    conds = " + ".join(item.get("probConds") or []) or "—"
    badge = "우리 조" if is_mine else "다른 조"
    st.markdown(
        f"""
        <div class="mini-card" style="border-color:{'#3A8BAF' if is_mine else 'rgba(255,255,255,.75)'};">
          <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
            <strong>{html.escape(class_group)}{(' · ' + html.escape(members)) if members else ''}</strong>
            <span class="{'status-done' if is_mine else 'status-progress'}">{badge}</span>
          </div>
          <div style="font-size:.95rem;line-height:1.75;font-weight:700;margin-top:8px;white-space:pre-wrap;">{html.escape(item.get('probStatement', ''))}</div>
          <div class="small-muted">선택 조건: {html.escape(conds)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step5() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 05 · 활동 결과 발표하기</div>', unsafe_allow_html=True)
    st.subheader("우리 조의 활동 결과 공유")
    st.caption("조별로 만든 문제에 대해서 학급 전체와 공유해봅시다.")
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
            st.caption(f"{text_key('w_classCode')}에서 아직 새로 추가된 다른 조 문제가 없습니다.")
        else:
            st.caption(f"{text_key('w_classCode')}에서 다른 조 문제 {len(peers)}개를 불러왔습니다.")
            for item in peers:
                render_problem_card(item)
    st.text_area(
        "🎤 발표할 내용 정리",
        key="w_present_content",
        placeholder="우리 조의 플레이리스트, 흥미로웠던 조건, 계산 결과, 만든 문제를 간단히 정리하세요.",
        height=120,
    )
    st.text_area(
        "💡 가장 흥미로웠던 점 / 발견한 것",
        key="w_present_finding",
        placeholder="여러 조건 중 어떤 것이 가장 인상적이었나요? 예상과 달랐던 결과가 있었나요?",
        height=100,
    )
    st.text_area(
        "🔍 다른 조의 발표를 듣고 — 새롭게 알게 된 것",
        key="w_present_learned",
        placeholder="다른 조의 발표에서 배운 점, 우리 조와 다른 풀이 전략 등을 기록하세요.",
        height=100,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(4, 6)


def render_summary_area() -> None:
    songs = [song for song in get_songs() if song["title"]]
    song_text = " / ".join(f"{song['label']}: {song['title']}" for song in songs)
    st.markdown(
        f"""
        <div class="mini-card"><strong>이름</strong><br>{html.escape(text_key('w_studentName'))}</div>
        <div class="mini-card"><strong>반/조</strong><br>{html.escape(text_key('w_classCode'))} {html.escape(text_key('w_groupName'))}</div>
        <div class="mini-card"><strong>조원</strong><br>{html.escape(text_key('w_members'))}</div>
        <div class="mini-card"><strong>선택 곡</strong><br>{html.escape(song_text)}</div>
        """,
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
        st.success("🎵 제출 완료! 오늘 수업은 여기까지. 모두 수고했습니다.")
    else:
        st.error(f"제출 오류: {result.get('error', '알 수 없는 오류')}")


def render_step6() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">STEP 06 · 순열 조건 정리 및 제출</div>', unsafe_allow_html=True)
    st.subheader("오늘의 학습 마무리하기")
    st.caption("오늘 활동을 통해 배운 내용을 정리해봅시다.")
    st.text_area(
        "📌 순열을 사용하는 상황의 핵심 특징은 무엇인가요?",
        key="w_summary_when",
        placeholder="오늘 활동을 통해 깨달은 것을 바탕으로, 순열로 모델링할 수 있는 상황의 특징을 정리해보세요.",
        height=130,
    )
    st.text_area(
        "💬 오늘 활동에서 배운 것 / 어려웠던 점",
        key="w_summary_reflect",
        placeholder="새롭게 알게 된 것과 어려웠던 부분을 솔직하게 적어주세요.",
        height=100,
    )
    render_summary_area()
    st.markdown("#### ✅ 자기 점검")
    for cid, label in CHECK_ITEMS:
        st.checkbox(label, key=f"w_check_{cid}")
    submit_col, _ = st.columns([1, 1])
    with submit_col:
        if st.button("📤 활동지 제출하기", type="primary", use_container_width=True):
            submit_all()
    st.markdown("</div>", unsafe_allow_html=True)
    nav_buttons(5, None)


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


def format_time(value: Any) -> str:
    if not value:
        return "—"
    text = str(value).replace("T", " ")
    return text[:16]


def condition_progress(item: dict[str, Any]) -> tuple[int, int]:
    cond_filled = 0
    cond_total = 14
    cd = item.get("conditionsData") or {}
    if cd.get("totalFormula"):
        cond_filled += 1
    groups = cd.get("groups") or {}
    for gid in GROUP_ORDER:
        for cond in groups.get(gid, []) or []:
            if cond.get("formula") or cond.get("question"):
                cond_filled += 1
    return cond_filled, cond_total


def csv_export(items: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["최종수정", "이름", "반/조", "현재단계", "선택조건", "경우의수", "풀이과정", "전체데이터", "세션ID", "제출여부"])
    for item in items:
        writer.writerow(
            [
                item.get("updatedAt", ""),
                item.get("studentName", ""),
                f"{item.get('classCode', '')} {item.get('groupName', '')}".strip(),
                item.get("currentStep", 1),
                " + ".join(item.get("probConds") or []),
                item.get("probFormula", ""),
                item.get("probExplain", ""),
                html.unescape(str(item)),
                item.get("sessionId", ""),
                "제출완료" if item.get("submitted") else "진행중",
            ]
        )
    return output.getvalue()


def render_student_detail(item: dict[str, Any]) -> None:
    songs = [song for song in item.get("songs", []) if song.get("title")]
    cd = item.get("conditionsData") or {}
    st.markdown("##### 📖 순열 복습")
    blanks = item.get("blanks") or {}
    if blanks:
        cols = st.columns(3)
        for idx, (key, label) in enumerate(BLANK_FIELDS):
            cols[idx % 3].markdown(f"**{label}**: {blanks.get(key, '(미작성)') or '(미작성)'}")
    choice = item.get("review2Choice") or item.get("review2choice") or ""
    st.write("오늘의 질문 선택:", "예" if choice == "yes" else "아니오" if choice == "no" else choice or "(작성 내용 없음)")

    st.markdown("##### 🎵 선택한 7곡")
    for song in songs:
        st.markdown(
            f"<span class='song-chip'>{html.escape(song.get('label', ''))}: {html.escape(song.get('title', ''))}</span> "
            f"<span class='small-muted'>{html.escape(song.get('artist', '') or '—')} · {html.escape(song.get('genre', '') or '—')} · {html.escape(song.get('tag', '') or '—')}</span>",
            unsafe_allow_html=True,
        )

    st.markdown("##### 🔢 전체 경우의 수")
    st.write("경우의 수 식:", cd.get("totalFormula") or "(미작성)")
    st.write("이유 설명:", cd.get("totalExplain") or "(미작성)")

    st.markdown("##### 📐 제한조건별 경우의 수")
    groups = cd.get("groups") or {}
    for gid in GROUP_ORDER:
        meta = COND_META.get(gid)
        if not meta:
            continue
        with st.expander(meta["title"], expanded=False):
            group_rows = groups.get(gid, []) or []
            for row in group_rows:
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
                    st.write("식:", row.get("formula") or "(미작성)")
                    st.write("이유:", row.get("explain") or "(미작성)")

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
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="eyebrow">교사용 대시보드</div>', unsafe_allow_html=True)
        st.subheader("교사용 비밀번호를 입력하세요.")
        pw = st.text_input("비밀번호", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("입장하기 →", type="primary", use_container_width=True):
                if pw == teacher_password:
                    st.session_state["teacher_authenticated"] = True
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        with col2:
            if st.button("학생용 화면으로", use_container_width=True):
                set_query_page("student")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown(
        """
        <div class="glass-card compact">
          <div style="display:flex;justify-content:space-between;gap:16px;align-items:center;">
            <div>
              <div style="font-weight:900;font-size:1.1rem;">교사용 대시보드</div>
              <div class="small-muted">플레이리스트로 순열 살펴보기 · 실시간 제출 현황</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    all_items = get_submissions()
    total = len(all_items)
    submitted = len([item for item in all_items if item.get("submitted")])
    progress = total - submitted
    avg_step = sum(int(item.get("currentStep") or 1) for item in all_items) / total if total else 0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 접속 수", total)
    m2.metric("제출 완료", submitted)
    m3.metric("진행 중", progress)
    m4.metric("평균 진행 단계", f"{avg_step:.1f}단계" if total else "—")

    with st.container(border=True):
        f1, f2, f3, f4, f5 = st.columns([2, 1, 1, 1, 1])
        name_filter = f1.text_input("이름 검색", placeholder="이름 검색...")
        class_filter = f2.selectbox("반", [""] + CLASSES, format_func=lambda x: x or "전체")
        group_filter = f3.selectbox("조", [""] + GROUPS, format_func=lambda x: x or "전체")
        status_filter = f4.selectbox("상태", ["", "done", "progress"], format_func=lambda x: {"": "전체", "done": "제출완료", "progress": "진행중"}[x])
        if f5.button("↻ 지금 갱신", use_container_width=True):
            st.rerun()
        auto_refresh = st.toggle("8초 자동 갱신", value=False)
        if auto_refresh:
            components.html("<script>setTimeout(() => window.parent.location.reload(), 8000);</script>", height=0)

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

    st.download_button(
        "CSV 다운로드",
        data=csv_export(filtered),
        file_name=f"playlist_permutation_submissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if not filtered:
        st.info("아직 접속한 학생이 없습니다.")
        return

    for item in filtered:
        uid = item.get("sessionId") or f"{item.get('studentName', '')}_{item.get('updatedAt', '')}"
        songs = [song for song in item.get("songs", []) if song.get("title")]
        cond_filled, cond_total = condition_progress(item)
        meta = " ".join(part for part in [item.get("classCode"), item.get("groupName")] if part)
        status_html = (
            '<span class="status-done">✅ 제출완료</span>'
            if item.get("submitted")
            else f'<span class="status-progress">STEP {item.get("currentStep", 1)} 진행중</span>'
        )
        with st.expander(f"{item.get('studentName') or '(이름 없음)'} · {meta} · {format_time(item.get('updatedAt'))}", expanded=False):
            st.markdown(status_html, unsafe_allow_html=True)
            st.caption((item.get("members") and f"조원: {item.get('members')}") or "조원 정보 없음")
            st.markdown(" ".join(f"<span class='song-chip'>{html.escape(song['label'])}: {html.escape(song['title'])}</span>" for song in songs), unsafe_allow_html=True)
            st.write(f"📐 경우의 수 계산: {cond_filled} / {cond_total}문제 완료")
            if item.get("probStatement"):
                st.write("만든 문제:", item["probStatement"])
            render_student_detail(item)
            st.divider()
            confirm_key = f"confirm_delete_{uid}"
            st.checkbox("삭제 확인", key=confirm_key)
            if st.button("🗑️ 삭제", key=f"delete_{uid}", disabled=not bool_key(confirm_key)):
                result = delete_session(uid)
                if result.get("success"):
                    st.success("삭제했습니다.")
                    st.rerun()
                else:
                    st.error(f"삭제 실패: {result.get('error', '알 수 없는 오류')}")


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
