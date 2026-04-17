import logging
import os

logger = logging.getLogger(__name__)

# Fallback used when Langfuse is not configured or the prompt fetch fails.
_FALLBACK_SYSTEM_PROMPT = """\
You are a customer support AI agent. Your job is to analyze support tickets and produce a structured analysis.

Steps you MUST follow:
1. Call `lookup_customer` with the provided customer_id to understand the customer's plan and history.
2. Call `search_kb` with relevant keywords from the ticket to find related knowledge base articles.
3. Decide whether the ticket needs human escalation. Criteria for escalation:
   - Customer on enterprise plan with any complaint
   - Customer has more than 2 open tickets
   - Issue is about data loss, security, or billing disputes
4. If escalation is needed, call `create_escalation` with a concise reason and the priority level.
5. Draft a clear, empathetic reply to the customer based on the KB articles found.

After completing the steps, produce your final analysis.
"""


def get_system_prompt(name: str = "ticket-analyzer") -> str:
    """Fetch the versioned prompt from Langfuse (label=production).

    Falls back to the local default if Langfuse is not configured.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")

    if not public_key or not secret_key:
        logger.debug("Langfuse credentials not set — using fallback prompt.")
        return _FALLBACK_SYSTEM_PROMPT

    try:
        from langfuse import Langfuse  # imported lazily so the app boots without Langfuse

        lf = Langfuse()
        prompt = lf.get_prompt(name, label="production")
        return prompt.compile()
    except Exception as exc:
        logger.warning("Failed to fetch prompt from Langfuse (%s) — using fallback.", exc)
        return _FALLBACK_SYSTEM_PROMPT
