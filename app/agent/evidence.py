from typing import Any

from app.agent.rollback_decision import make_rollback_decision


def summarize_tool_outputs(tool_outputs: dict[str, Any]) -> str:
    """
    Create a deterministic evidence summary from tool outputs.

    This helps the LLM avoid mixing up what came from logs,
    service health, deployment history, and runbooks.
    """
    lines: list[str] = []

    log_search = tool_outputs.get("log_search", {})
    log_results = log_search.get("results", [])
    log_service = log_search.get("service", "unknown")
    log_keyword = log_search.get("keyword", "unknown")

    lines.append("LOG EVIDENCE:")
    lines.append(
        f"- log_search searched service '{log_service}' for keyword '{log_keyword}'."
    )
    lines.append(f"- log_search returned {len(log_results)} matching log lines.")

    if log_results:
        for result in log_results[:5]:
            line_number = result.get("line_number", "unknown")
            line = result.get("line", "")
            lines.append(f"- Match at line {line_number}: {line}")
    else:
        lines.append("- No matching log lines were found.")

    lines.append("")
    lines.append("SERVICE HEALTH EVIDENCE:")

    service_health = tool_outputs.get("service_health", {})
    health_results = service_health.get("results", {})

    if health_results:
        for service, health in health_results.items():
            status = health.get("status", "unknown")
            version = health.get("version", "unknown")
            error_rate = health.get("error_rate_percent", "not provided")
            latency = health.get("latency_p95_ms", "not provided")

            lines.append(
                f"- {service}: status={status}, version={version}, "
                f"error_rate_percent={error_rate}, latency_p95_ms={latency}"
            )
    else:
        lines.append("- No service health data was provided.")

    lines.append("")
    lines.append("DEPLOYMENT EVIDENCE:")

    deployments = tool_outputs.get("deployments", {})
    deployment_results = deployments.get("results", {}).get("deployments", [])
    deployment_service = deployments.get("service", "unknown")

    if deployment_results:
        latest = deployment_results[0]
        lines.append(
            f"- Latest deployment for {deployment_service}: "
            f"version={latest.get('version')}, "
            f"deployed_at={latest.get('deployed_at')}, "
            f"status={latest.get('status')}, "
            f"change_summary={latest.get('change_summary')}"
        )
        lines.append(
            f"- Previous stable version from deployment data: "
            f"{latest.get('previous_stable_version')}"
        )
    else:
        lines.append("- No deployment records were found.")

    rollback_decision = make_rollback_decision(tool_outputs)

    lines.append("")
    lines.append("ROLLBACK DECISION:")
    lines.append(f"- status: {rollback_decision.get('status')}")
    lines.append(f"- recommendation: {rollback_decision.get('recommendation')}")
    lines.append(f"- reason: {rollback_decision.get('reason')}")
    lines.append(
        f"- previous_stable_version: {rollback_decision.get('previous_stable_version')}"
    )
    lines.append(
        f"- minutes_since_deploy: {rollback_decision.get('minutes_since_deploy')}"
    )

    return "\n".join(lines)