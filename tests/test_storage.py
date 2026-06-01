from pathlib import Path

from storage import (
    delete_session,
    get_problem_board,
    get_saved_session_by_identity,
    get_submissions,
    upsert_session,
)


def test_upsert_restore_problem_board_delete(tmp_path: Path) -> None:
    db = tmp_path / "submissions.db"
    data = {
        "sessionId": "sid_test",
        "studentName": "홍길동",
        "classCode": "1반",
        "groupName": "2조",
        "members": "A, B",
        "currentStep": 4,
        "submitted": False,
        "probConds": ["특정 자리 고정", "이웃하는 조건"],
        "probStatement": "A를 첫 번째로 고정하고 B와 C가 이웃할 때의 수를 구하시오.",
    }

    assert upsert_session("sid_test", data, db)["success"]
    rows = get_submissions(db)
    assert len(rows) == 1
    assert rows[0]["studentName"] == "홍길동"

    restored = get_saved_session_by_identity("홍길동", "1반", "2조", "A, B", db)
    assert restored["found"] is True
    assert restored["data"]["sessionId"] == "sid_test"

    board = get_problem_board("1반", db)
    assert len(board) == 1
    assert board[0]["probStatement"].startswith("A를 첫 번째")

    assert delete_session("sid_test", db)["success"]
    assert get_submissions(db) == []
