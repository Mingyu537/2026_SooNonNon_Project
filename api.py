"""FastAPI backend — replaces Google Apps Script server functions."""
from __future__ import annotations

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

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
    return upsert_session(session_id, body)


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


@app.post("/api/checkTeacherPassword")
async def api_check_pw(request: Request):
    body = await request.json()
    pw = body.get("pw", "")
    if pw == _teacher_password():
        return {"ok": True, "url": "?page=teacher"}
    return {"ok": False}
