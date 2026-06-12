import json
from pathlib import Path

from app.config import DATA_DIR


DEPLOYMENTS_FILE = Path(DATA_DIR) / "mock_api" / "deployments.json"


def get_recent_deployments(service: str, limit: int = 3) -> dict:
    """
    Return recent deployment records for a service.

    Args:
        service: Service name, for example "checkout-api".
        limit: Maximum number of deployments to return.

    Returns:
        A dictionary containing deployment history.
    """
    if not DEPLOYMENTS_FILE.exists():
        return {
            "service": service,
            "found": False,
            "error": f"Deployments file not found: {DEPLOYMENTS_FILE}",
        }

    with DEPLOYMENTS_FILE.open("r", encoding="utf-8") as file:
        deployment_data = json.load(file)

    service_deployments = deployment_data.get(service)

    if not service_deployments:
        return {
            "service": service,
            "found": False,
            "error": f"No deployment data found for service: {service}",
            "available_services": list(deployment_data.keys()),
        }

    return {
        "service": service,
        "found": True,
        "deployments": service_deployments[:limit],
    }