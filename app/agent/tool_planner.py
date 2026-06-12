from typing import Any


def plan_tools(question: str) -> dict[str, Any]:
    """
    Create a simple deterministic tool plan from the user question.

    This is intentionally rule-based for v1.
    Later, we can replace or enhance this with LLM-based planning.
    """
    question_lower = question.lower()

    service = "checkout-api"
    log_keyword = "PAYMENT_SERVICE_URL"

    if "payment-service" in question_lower or "payment service" in question_lower:
        service = "payment-service"
        log_keyword = "gateway_timeout"

    if "database" in question_lower or "db" in question_lower or "migration" in question_lower:
        log_keyword = "migration"

    if "payment_service_url" in question_lower or "payment service url" in question_lower:
        log_keyword = "PAYMENT_SERVICE_URL"

    tools = [
        "log_search",
        "service_health",
        "deployments",
    ]

    return {
        "service": service,
        "log_keyword": log_keyword,
        "tools": tools,
    }