from datetime import datetime
from typing import Any


def _parse_iso_z(timestamp: str) -> datetime | None:
    """
    Parse timestamps like 2026-06-11T10:06:00Z.
    """
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except Exception:
        return None


def make_rollback_decision(tool_outputs: dict[str, Any]) -> dict[str, Any]:
    """
    Make a deterministic rollback decision from tool evidence.

    This prevents the LLM from over-applying rollback guidance.
    """
    service_health = tool_outputs.get("service_health", {}).get("results", {})
    deployments = tool_outputs.get("deployments", {}).get("results", {}).get("deployments", [])

    if not deployments:
        return {
            "status": "insufficient_data",
            "recommendation": "No deployment history found, so rollback version cannot be determined.",
            "previous_stable_version": None,
            "reason": "Deployment tool returned no deployment records.",
        }

    latest_deployment = deployments[0]
    service = tool_outputs.get("deployments", {}).get("service", "unknown")

    health = service_health.get(service, {})

    error_rate = health.get("error_rate_percent")
    last_checked = health.get("last_checked")
    deployed_at = latest_deployment.get("deployed_at")
    previous_stable_version = latest_deployment.get("previous_stable_version")

    deployed_time = _parse_iso_z(deployed_at) if deployed_at else None
    checked_time = _parse_iso_z(last_checked) if last_checked else None

    minutes_since_deploy = None

    if deployed_time and checked_time:
        minutes_since_deploy = round((checked_time - deployed_time).total_seconds() / 60, 2)

    if error_rate is None:
        return {
            "status": "insufficient_data",
            "recommendation": "Prepare rollback only if customer impact is high or error rate remains elevated.",
            "previous_stable_version": previous_stable_version,
            "reason": "Service health did not provide error_rate_percent.",
            "minutes_since_deploy": minutes_since_deploy,
        }

    if error_rate > 5 and minutes_since_deploy is not None and minutes_since_deploy >= 10:
        return {
            "status": "rollback_recommended",
            "recommendation": f"Rollback to previous stable version {previous_stable_version}.",
            "previous_stable_version": previous_stable_version,
            "reason": (
                f"Error rate is {error_rate}% and has been observed at least "
                f"{minutes_since_deploy} minutes after deployment."
            ),
            "minutes_since_deploy": minutes_since_deploy,
        }

    if error_rate > 5:
        return {
            "status": "prepare_rollback",
            "recommendation": (
                f"Prepare rollback to {previous_stable_version}, but first verify whether "
                "the error rate remains above 5% for more than 10 minutes or customer impact is high."
            ),
            "previous_stable_version": previous_stable_version,
            "reason": (
                f"Error rate is {error_rate}%, but only {minutes_since_deploy} minutes "
                "have passed since deployment based on available evidence."
            ),
            "minutes_since_deploy": minutes_since_deploy,
        }

    return {
        "status": "rollback_not_recommended",
        "recommendation": "Rollback is not recommended based on current error rate evidence.",
        "previous_stable_version": previous_stable_version,
        "reason": f"Error rate is {error_rate}%, which is not above the 5% rollback threshold.",
        "minutes_since_deploy": minutes_since_deploy,
    }