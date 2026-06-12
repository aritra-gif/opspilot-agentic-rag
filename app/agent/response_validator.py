REQUIRED_SECTIONS = [
    "Likely root cause:",
    "Evidence from tools:",
    "Relevant runbook guidance:",
    "Recommended next steps:",
    "Rollback recommendation:",
    "Missing information:",
    "Confidence:",
    "Sources and tools used:",
]


def find_missing_sections(answer: str) -> list[str]:
    """
    Check whether the LLM answer contains all required sections.
    """
    missing_sections: list[str] = []

    answer_lower = answer.lower()

    for section in REQUIRED_SECTIONS:
        if section.lower() not in answer_lower:
            missing_sections.append(section)

    return missing_sections


def _tool_is_mentioned(answer_lower: str, tool: str) -> bool:
    """
    Check whether a selected tool is mentioned in the answer.

    We allow natural variants because LLMs may say:
    - deployment tool instead of deployments
    - health check instead of service_health
    - log search instead of log_search
    """
    tool_lower = tool.lower()

    aliases = {
        "log_search": ["log_search", "log search", "logs", "log lines"],
        "service_health": ["service_health", "service health", "health check", "health data"],
        "deployments": ["deployments", "deployment tool", "deployment data", "deployment history"],
    }

    allowed_mentions = aliases.get(tool_lower, [tool_lower])

    return any(mention in answer_lower for mention in allowed_mentions)


def find_quality_issues(
    answer: str,
    evidence_summary: str = "",
    selected_tools: list[str] | None = None,
) -> list[str]:
    """
    Detect simple factual or traceability issues in the final answer.

    This is intentionally rule-based for v1.
    Later we can add stronger evals.
    """
    issues: list[str] = []

    answer_lower = answer.lower()
    evidence_lower = evidence_summary.lower()
    selected_tools = selected_tools or []

    evidence_mentions_missing_payment_url = (
        "payment_service_url is not configured" in evidence_lower
        or "missing payment_service_url" in evidence_lower
    )

    answer_denies_missing_env_vars = (
        "no missing environment variables" in answer_lower
        or "no missing env" in answer_lower
    )

    if evidence_mentions_missing_payment_url and answer_denies_missing_env_vars:
        issues.append(
            "Answer contradicts log evidence: evidence shows PAYMENT_SERVICE_URL is missing, but answer says there are no missing environment variables."
        )

    evidence_says_prepare_rollback = "status: prepare_rollback" in evidence_lower

    if evidence_says_prepare_rollback:
        has_negated_rollback_phrase = (
            "no immediate rollback is recommended" in answer_lower
            or "rollback is not recommended" in answer_lower
            or "not fully recommended" in answer_lower
            or "not recommended yet" in answer_lower
            or "not fully recommend" in answer_lower
            or "prepare rollback" in answer_lower
            or "preparing rollback" in answer_lower
        )

        has_rollback_recommended_phrase = (
            "rollback is recommended" in answer_lower
            or "immediate rollback is recommended" in answer_lower
            or "fully recommended" in answer_lower
        )

        overstates_rollback = (
            has_rollback_recommended_phrase
            and not has_negated_rollback_phrase
        ) or "rollback immediately" in answer_lower

        claims_threshold_met = (
            "given that the error rate remains above 5% for more than 10 minutes" in answer_lower
            or "has remained above 5% for more than 10 minutes" in answer_lower
            or "has been above 5% for more than 10 minutes" in answer_lower
            or "threshold was met" in answer_lower
            or "rollback threshold was met" in answer_lower
        )

        if overstates_rollback:
            issues.append(
                "Answer overstates rollback: evidence says prepare_rollback, not full rollback_recommended."
            )

        if claims_threshold_met:
            issues.append(
                "Answer incorrectly claims the rollback time threshold was met. Evidence says rollback status is prepare_rollback, not rollback_recommended."
            )

    evidence_has_deployment_timestamp = (
        "deployed_at=" in evidence_lower
        or "deployed_at" in evidence_lower
        or "latest deployment" in evidence_lower
    )

    answer_says_deployment_timestamp_missing = (
        "exact timestamp of the deployment is not available" in answer_lower
        or "deployment timestamp is not available" in answer_lower
        or "deployment time is not available" in answer_lower
    )

    if evidence_has_deployment_timestamp and answer_says_deployment_timestamp_missing:
        issues.append(
            "Answer contradicts deployment evidence: deployment timestamp is available in the deployments tool output."
        )

    sources_section_present = "sources and tools used:" in answer_lower

    if sources_section_present:
        for tool in selected_tools:
            if not _tool_is_mentioned(answer_lower, tool):
                issues.append(
                    f"Answer sources section does not mention selected tool: {tool}"
                )

    return issues


def is_valid_answer(answer: str) -> bool:
    """
    Return True if all required sections are present.
    """
    return len(find_missing_sections(answer)) == 0


def is_quality_acceptable(
    answer: str,
    evidence_summary: str = "",
    selected_tools: list[str] | None = None,
) -> bool:
    """
    Return True if no obvious quality issues are detected.
    """
    return len(find_quality_issues(answer, evidence_summary, selected_tools)) == 0