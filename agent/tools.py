from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Mock data — replace with real DB / search index calls in production
# ---------------------------------------------------------------------------

_KB_ARTICLES: dict[str, str] = {
    "password_reset": "To reset your password go to Settings › Security › Reset Password.",
    "billing_cycle": "Billing runs on the 1st of each month. Disputes: billing@company.com.",
    "api_limits": "Free tier: 100 req/day. Pro: 10 000 req/day. Enterprise: unlimited.",
    "refund_policy": "Refunds are accepted within 30 days of purchase for annual plans.",
    "downtime": "For ongoing incidents check status.company.com.",
}

_CUSTOMERS: dict[str, dict] = {
    "cust_001": {"name": "Alice Silva", "plan": "pro", "open_tickets": 1, "since": "2023-01"},
    "cust_002": {"name": "Bob Santos", "plan": "free", "open_tickets": 3, "since": "2024-06"},
    "cust_003": {"name": "Carol Lima", "plan": "enterprise", "open_tickets": 0, "since": "2022-03"},
}

_escalations: list[dict] = []


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool
def search_kb(query: str) -> str:
    """Search the internal knowledge base for articles related to the query."""
    q = query.lower()
    matches = [text for key, text in _KB_ARTICLES.items() if any(w in q for w in key.split("_"))]
    return "\n".join(matches) if matches else "No relevant articles found."


@tool
def lookup_customer(customer_id: str) -> str:
    """Look up a customer's plan, open ticket count, and tenure by customer ID."""
    c = _CUSTOMERS.get(customer_id)
    if not c:
        return f"Customer '{customer_id}' not found."
    return (
        f"Name: {c['name']} | Plan: {c['plan']} | "
        f"Open tickets: {c['open_tickets']} | Customer since: {c['since']}"
    )


@tool
def create_escalation(customer_id: str, reason: str, priority: str) -> str:
    """Create an escalation record for a ticket that requires human review."""
    esc_id = f"ESC-{len(_escalations) + 1:04d}"
    _escalations.append({"id": esc_id, "customer_id": customer_id, "reason": reason, "priority": priority})
    return f"Escalation created: {esc_id}"


TOOLS = [search_kb, lookup_customer, create_escalation]
