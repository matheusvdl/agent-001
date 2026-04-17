import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from sse_starlette.sse import EventSourceResponse

load_dotenv()

from agent.analyzer import analyze_ticket
from agent.chat import stream_chat
from models import ChatInput, RunResponse, RunStatus, TicketInput
from storage.store import create_run, get_run, update_run

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server is up and running")
    yield
    logger.info("Server is shutting down")


app = FastAPI(title="Ticket Analyzer AI Agent", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------


async def _run_analysis(run_id: str, ticket: TicketInput) -> None:
    update_run(run_id, RunStatus.running)
    try:
        result = await analyze_ticket(
            run_id=run_id,
            title=ticket.title,
            description=ticket.description,
            customer_id=ticket.customer_id,
        )
        update_run(run_id, RunStatus.done, result=result)
        logger.info("Run %s completed: %s", run_id, result)
    except Exception as exc:
        logger.exception("Run %s failed", run_id)
        update_run(run_id, RunStatus.error, error=str(exc))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets/analyze", response_model=RunResponse, status_code=202)
async def tickets_analyze(ticket: TicketInput, background_tasks: BackgroundTasks):
    """Enqueue a ticket for async analysis. Returns a run_id to poll for results."""
    run_id = create_run(ticket.model_dump())
    background_tasks.add_task(_run_analysis, run_id, ticket)
    return RunResponse(run_id=run_id, status=RunStatus.pending)


@app.get("/runs/{run_id}", response_model=RunResponse)
def runs_get(run_id: str):
    """Return the status and result (if done) for a given run."""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(
        run_id=run["run_id"],
        status=run["status"],
        result=run.get("result"),
        error=run.get("error"),
    )


@app.post("/chat")
async def chat(chat_input: ChatInput):
    """Stream a chat response about a ticket via Server-Sent Events."""
    run = get_run(chat_input.run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator():
        async for token in stream_chat(chat_input.run_id, chat_input.message):
            yield {"data": token}
        yield {"data": "[DONE]"}

    return EventSourceResponse(event_generator())
