import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from agent.prompts import get_system_prompt
from agent.tools import TOOLS
from models import AnalysisResult


def _make_langfuse_callback(run_id: str):
    """Return a Langfuse CallbackHandler if credentials are available, else None."""
    try:
        import os

        if not os.getenv("LANGFUSE_PUBLIC_KEY"):
            return None
        from langfuse.callback import CallbackHandler

        return CallbackHandler(trace_id=run_id, tags=["ticket-analyzer"])
    except Exception:
        return None


def _build_llm(run_id: str, streaming: bool = False) -> ChatOpenAI:
    callbacks = []
    cb = _make_langfuse_callback(run_id)
    if cb:
        callbacks.append(cb)

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        streaming=streaming,
        callbacks=callbacks or None,
    )


async def analyze_ticket(
    run_id: str,
    title: str,
    description: str,
    customer_id: str,
) -> AnalysisResult:
    """Two-step analysis:
    1. Agent with tools gathers context (KB search, customer lookup, optional escalation).
    2. Structured output call synthesises everything into AnalysisResult.
    """
    system_prompt = get_system_prompt()

    # ── Step 1: tool-calling agent ──────────────────────────────────────────
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    llm = _build_llm(run_id)
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)

    user_input = (
        f"Ticket title: {title}\n"
        f"Description: {description}\n"
        f"Customer ID: {customer_id}"
    )
    agent_result = await executor.ainvoke({"input": user_input})
    agent_summary = agent_result.get("output", "")

    # ── Step 2: structured output ────────────────────────────────────────────
    # A fresh LLM call so Langfuse traces both steps separately.
    structured_llm = _build_llm(run_id).with_structured_output(AnalysisResult)
    result: AnalysisResult = await structured_llm.ainvoke(
        [
            SystemMessage(
                content=(
                    "Based on the agent analysis below, return a structured JSON response "
                    "with the fields: category, priority, needs_human, suggested_reply, next_action."
                )
            ),
            HumanMessage(
                content=f"Original ticket:\n{user_input}\n\nAgent findings:\n{agent_summary}"
            ),
        ]
    )
    return result
