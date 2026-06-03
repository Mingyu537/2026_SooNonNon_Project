"""FastAPI backend — replaces Google Apps Script server functions."""
from __future__ import annotations

import os
import urllib.request
import json as _json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ── Google Apps Script 웹 앱 URL (Google Sheets 저장용) ──────────────────────
SHEETS_WEBAPP_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwlqctZCDXvqps6q5yJb2Nv_u3p_iATy3Vawv8Bn2V54j-zMeLkk8qgk5-cqzG5IScIXw"
    "/exec"
)


def _mirror_to_sheets(action: str, payload: dict) -> None:
    """Google Sheets(Apps Script 웹 앱)에 데이터를 미러링합니다.
    실패해도 예외를 밖으로 던지지 않습니다."""
    try:
        body = _json.dumps(dict(payload, action=action)).encode("utf-8")
        req = urllib.request.Request(
            SHEETS_WEBAPP_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        # 5초 타임아웃 — 학생 화면을 블로킹하지 않음
        with urllib.request.urlopen(req, timeout=5):
            pass
    except Exception as exc:
        print(f"[sheets mirror] {action} 실패: {exc}")

from storage import (
    delete_session,
    get_problem_board,
    get_saved_session_by_identity,
    get_submissions,
    upsert_session,
)
from constants import DEFAULT_TEACHER_PASSWORD

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _teacher_password() -> str:
    # 환경변수 > secrets > 기본값 순서로 확인
    env_pw = os.environ.get("TEACHER_PASSWORD", "")
    if env_pw:
        return env_pw
    try:
        import streamlit as st  # type: ignore
        secret_pw = st.secrets.get("TEACHER_PASSWORD", "")
        if secret_pw:
            return str(secret_pw)
    except Exception:
        pass
    return DEFAULT_TEACHER_PASSWORD  # "math2026"


@app.post("/api/upsertSession")
async def api_upsert(request: Request):
    body = await request.json()
    session_id = body.get("sessionId", "")
    # 1) SQLite 저장 (주 저장소)
    result = upsert_session(session_id, body)
    # 2) Google Sheets 미러링 (실패해도 학생 화면에 영향 없음)
    _mirror_to_sheets("upsertSession", body)
    return result


@app.get("/api/getSubmissions")
async def api_submissions():
    return get_submissions()


@app.post("/api/deleteSession")
async def api_delete(request: Request):
    body = await request.json()
    return delete_session(body.get("sessionId", ""))


@app.post("/api/getSavedSessionByIdentity")
async def api_restore(request: Request):
    body = await request.json()
    return get_saved_session_by_identity(
        body.get("name", ""),
        body.get("cls", ""),
        body.get("group", ""),
        body.get("members"),
    )


@app.get("/api/getProblemBoard")
async def api_problem_board(classCode: str = ""):
    return get_problem_board(classCode)


@app.get("/api/health")
async def health():
    return {"status": "ok", "password_hint": f"length={len(_teacher_password())}"}


@app.post("/api/checkTeacherPassword")
async def api_check_pw(request: Request):
    body = await request.json()
    pw = str(body.get("pw", "")).strip()
    expected = _teacher_password().strip()
    if pw == expected:
        return {"ok": True, "url": "?page=teacher"}
    return {"ok": False}
