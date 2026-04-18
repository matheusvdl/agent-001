# agent-001

FastAPI service that analyzes customer support tickets with an LLM agent.

## What it does

Given a ticket (title, description, customer_id) the agent:

1. Looks up the customer and searches an internal knowledge base (tools).
2. Decides whether the issue needs human escalation.
3. Returns a structured analysis: `category`, `priority`, `needs_human`, `suggested_reply`, `next_action`.

A follow-up `/chat` endpoint streams a conversation about the analyzed ticket.

## Stack

- **FastAPI** — routes, background tasks, SSE streaming
- **LangChain** — tool-calling agent + structured output
- **Langfuse** — versioned prompts (label `production`) + tracing via callback
- **OpenAI** — LLM backend (swappable for Claude/Bedrock via LiteLLM)

## Endpoints

| Method | Path                   | Description                                           |
| ------ | ---------------------- | ----------------------------------------------------- |
| POST   | `/tickets/analyze`     | Enqueue a ticket for analysis. Returns `run_id`.      |
| GET    | `/runs/{run_id}`       | Poll status and retrieve the structured result.       |
| POST   | `/chat`                | Stream a conversation about a run via SSE.            |
| GET    | `/health`              | Liveness probe.                                       |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY and Langfuse keys
```

## Running

```bash
uvicorn main:app --reload
```

## Project layout

```
main.py              FastAPI app and routes
models.py            Pydantic schemas
agent/
  analyzer.py        Two-step analysis: tool-calling agent + structured output
  chat.py            Streaming chat over ticket context
  tools.py           search_kb, lookup_customer, create_escalation
  prompts.py         Langfuse prompt fetch with local fallback
storage/
  store.py           In-memory run and conversation state
```
