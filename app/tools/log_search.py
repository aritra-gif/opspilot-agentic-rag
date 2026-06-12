from pathlib import Path

from app.config import LOGS_DIR


def search_logs(service: str, keyword: str, max_results: int = 20) -> list[dict]:
    """
    Search local mock log files for a keyword.

    Args:
        service: Service name, for example "checkout-api".
        keyword: Keyword to search for, for example "PAYMENT_SERVICE_URL".
        max_results: Maximum number of matching log lines to return.

    Returns:
        A list of matching log records.
    """
    results: list[dict] = []

    log_files = list(Path(LOGS_DIR).glob("*.log"))

    for log_file in log_files:
        with log_file.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line_clean = line.strip()

                if service.lower() in line_clean.lower() and keyword.lower() in line_clean.lower():
                    results.append(
                        {
                            "file": log_file.name,
                            "line_number": line_number,
                            "line": line_clean,
                        }
                    )

                if len(results) >= max_results:
                    return results

    return results