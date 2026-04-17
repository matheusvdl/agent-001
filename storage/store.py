import uuid
from datetime import datetime, timezone
from typing import Optional

from models import AnalysisResult, RunStatus

# In-memory stores — swap for a DB (SQLite/Postgres) when needed
_runs: dict[str, dict] = {}
_conversations: dict[str, list] = {}


def create_run(ticket_input: dict) -> str:
    run_id = str(uuid.uuid4())
    _runs[run_id] = {
        "run_id": run_id,
        "status": RunStatus.pending,
        "input": ticket_input,
        "result": None,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return run_id


def update_run(
    run_id: str,
    status: RunStatus,
    result: Optional[AnalysisResult] = None,
    error: Optional[str] = None,
) -> None:
    run = _runs.get(run_id)
    if not run:
        return
    run["status"] = status
    if result is not None:
        run["result"] = result
    if error is not None:
        run["error"] = error


def get_run(run_id: str) -> Optional[dict]:
    return _runs.get(run_id)


def get_conversation(run_id: str) -> list:
    return _conversations.setdefault(run_id, [])


def append_message(run_id: str, role: str, content: str) -> None:
    get_conversation(run_id).append({"role": role, "content": content})
