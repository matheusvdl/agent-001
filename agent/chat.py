import os
from typing import AsyncIterator

from langchain_openai import ChatOpenAI

from storage.store import append_message, get_conversation, get_run

_CHAT_SYSTEM = (
    "You are a helpful customer support assistant. "
    "You have access to a ticket analysis that was previously performed. "
    "Answer questions about the ticket and help the support agent take next steps."
)


async def stream_chat(run_id: str, user_message: str) -> AsyncIterator[str]:
    """Yield token chunks for the chat response, maintaining conversation history."""
    run = get_run(run_id)
    if not run:
        yield f"Run '{run_id}' not found."
        return

    # Build context from the ticket analysis if available
    context = ""
    if run.get("result"):
        r = run["result"]
        context = (
            f"\n\nTicket analysis on file:\n"
            f"- Category: {r.category}\n"
            f"- Priority: {r.priority}\n"
            f"- Needs human: {r.needs_human}\n"
            f"- Suggested reply: {r.suggested_reply}\n"
            f"- Next action: {r.next_action}"
        )

    # Persist user message
    append_message(run_id, "user", user_message)

    # Build message list: system + history
    messages = [{"role": "system", "content": _CHAT_SYSTEM + context}]
    messages.extend(get_conversation(run_id))

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.3,
        streaming=True,
    )

    full_response = ""
    async for chunk in llm.astream(messages):
        token = chunk.content
        if token:
            full_response += token
            yield token

    # Persist assistant reply after streaming completes
    append_message(run_id, "assistant", full_response)
