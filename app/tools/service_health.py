import json
from pathlib import Path

from app.config import DATA_DIR


HEALTH_FILE = Path(DATA_DIR) / "mock_api" / "service_health.json"


def check_service_health(service: str) -> dict:
    """
    Return mock health information for a service.

    Args:
        service: Service name, for example "checkout-api".

    Returns:
        A dictionary with service health details.
    """
    if not HEALTH_FILE.exists():
        return {
            "service": service,
            "found": False,
            "error": f"Health file not found: {HEALTH_FILE}",
        }

    with HEALTH_FILE.open("r", encoding="utf-8") as file:
        health_data = json.load(file)

    service_data = health_data.get(service)

    if not service_data:
        return {
            "service": service,
            "found": False,
            "error": f"No health data found for service: {service}",
            "available_services": list(health_data.keys()),
        }

    return {
        "service": service,
        "found": True,
        **service_data,
    }