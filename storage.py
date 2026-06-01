"""Persistence layer that mirrors the Apps Script server functions."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any


DB_DIR = Path(os.environ.get("STREAMLIT_DATA_DIR", "data"))
DB_PATH = DB_DIR / "submissions.db"

HEADERS = [
    "최종수정",
    "이름",
    "반/조",
    "현재단계",
    "선택조건",
    "경우의수",
    "풀이과정",
    "조별토의",
    "역설계목표",
    "전체데이터",
    "세션ID",
    "제출여부",
]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path: Path | None = None) -> None:
    with closing(connect(path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                session_id TEXT PRIMARY KEY,
                updated_at TEXT NOT NULL,
                student_name TEXT,
                class_code TEXT,
                current_step INTEGER,
                condition_label TEXT,
                condition_result TEXT,
                solution TEXT,
                discussion TEXT,
                target_count TEXT,
                payload_json TEXT NOT NULL,
                submitted TEXT NOT NULL
            )
            """
        )
        conn.commit()


def upsert_session(session_id: str, data: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    try:
        init_db(path)
        updated_at = now_iso()
        data = dict(data)
        data["sessionId"] = session_id
        data["updatedAt"] = updated_at
        submitted = "제출완료" if data.get("submitted") else "진행중"

        row = (
            session_id,
            updated_at,
            data.get("studentName", ""),
            data.get("classCode", ""),
            int(data.get("currentStep") or 1),
            (data.get("condition") or {}).get("label", "전체 조건 완료")
            if isinstance(data.get("condition"), dict)
            else "전체 조건 완료",
            (data.get("condition") or {}).get("result", "") if isinstance(data.get("condition"), dict) else "",
            data.get("solution", ""),
            data.get("discussion", ""),
            data.get("targetCount", ""),
            json.dumps(data, ensure_ascii=False),
            submitted,
        )
        with closing(connect(path)) as conn:
            conn.execute(
                """
                INSERT INTO submissions (
                    session_id, updated_at, student_name, class_code, current_step,
                    condition_label, condition_result, solution, discussion, target_count,
                    payload_json, submitted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    updated_at=excluded.updated_at,
                    student_name=excluded.student_name,
                    class_code=excluded.class_code,
                    current_step=excluded.current_step,
                    condition_label=excluded.condition_label,
                    condition_result=excluded.condition_result,
                    solution=excluded.solution,
                    discussion=excluded.discussion,
                    target_count=excluded.target_count,
                    payload_json=excluded.payload_json,
                    submitted=excluded.submitted
                """,
                row,
            )
            conn.commit()
        return {"success": True}
    except Exception as exc:  # pragma: no cover - surfaced in Streamlit UI
        return {"success": False, "error": str(exc)}


def get_submissions(path: Path | None = None) -> list[dict[str, Any]]:
    init_db(path)
    with closing(connect(path)) as conn:
        rows = conn.execute(
            "SELECT payload_json, updated_at, submitted FROM submissions ORDER BY updated_at DESC"
        ).fetchall()

    items: list[dict[str, Any]] = []
    for row in rows:
        try:
            item = json.loads(row["payload_json"])
            item.setdefault("updatedAt", row["updated_at"])
            item.setdefault("submitted", row["submitted"] == "제출완료")
            items.append(item)
        except json.JSONDecodeError:
            continue
    return items


def delete_session(session_id: str, path: Path | None = None) -> dict[str, Any]:
    try:
        init_db(path)
        with closing(connect(path)) as conn:
            cur = conn.execute("DELETE FROM submissions WHERE session_id = ?", (session_id,))
            conn.commit()
            if cur.rowcount:
                return {"success": True}
        return {"success": False, "error": "해당 세션을 찾을 수 없습니다."}
    except Exception as exc:  # pragma: no cover
        return {"success": False, "error": str(exc)}


def get_saved_session_by_identity(
    name: str,
    cls: str,
    group: str,
    members: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    del members
    init_db(path)
    with closing(connect(path)) as conn:
        rows = conn.execute(
            """
            SELECT payload_json
            FROM submissions
            WHERE TRIM(student_name) = ? AND TRIM(class_code) = ?
            ORDER BY updated_at DESC
            """,
            (name.strip(), cls.strip()),
        ).fetchall()

    for row in rows:
        try:
            data = json.loads(row["payload_json"])
        except json.JSONDecodeError:
            continue
        data_group = str(data.get("groupName") or "").strip()
        if group and data_group and data_group != group.strip():
            continue
        return {"success": True, "found": True, "data": data}
    return {"success": True, "found": False}


def normalize_class_code(value: str) -> str:
    return "".join(str(value or "").split())


def normalize_group_name(value: str) -> str:
    return "".join(str(value or "").split())


def group_order(value: str) -> int:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return int(digits) if digits else 9999


def get_problem_board(class_code: str, path: Path | None = None) -> list[dict[str, Any]]:
    class_key = normalize_class_code(class_code)
    problems = []
    for item in get_submissions(path):
        if normalize_class_code(item.get("classCode", "")) != class_key:
            continue
        if not str(item.get("probStatement", "")).strip():
            continue
        problems.append(item)
    return sorted(
        problems,
        key=lambda item: (
            group_order(item.get("groupName", "")),
            normalize_group_name(item.get("groupName", "")),
            item.get("updatedAt", ""),
        ),
    )
