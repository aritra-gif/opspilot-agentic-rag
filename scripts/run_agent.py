import argparse
from unittest import result

from rich import print

from app.agent.graph import build_graph


def print_tool_evidence_summary(tool_outputs: dict) -> None:
    log_search = tool_outputs.get("log_search", {})
    service_health = tool_outputs.get("service_health", {})
    deployments = tool_outputs.get("deployments", {})

    log_results = log_search.get("results", [])
    health_results = service_health.get("results", {})
    deployment_results = deployments.get("results", {}).get("deployments", [])

    print("\n[bold cyan]Tool evidence summary:[/bold cyan]")
    print(f"- log_search matches: {len(log_results)}")

    for service, health in health_results.items():
        status = health.get("status", "unknown")
        print(f"- service_health {service}: {status}")

    print(f"- deployments found: {len(deployment_results)}")

    if deployment_results:
        latest = deployment_results[0]
        print(
            f"- latest deployment: {latest.get('version')} at {latest.get('deployed_at')}"
        )
        print(
            f"- previous stable version: {latest.get('previous_stable_version')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str)
    args = parser.parse_args()

    graph = build_graph()

    result = graph.invoke(
        {
            "question": args.question,
        }
    )

    print("\n[bold cyan]Tool plan:[/bold cyan]")
    tool_plan = result.get("tool_plan", {})
    print(f"- service: {tool_plan.get('service')}")
    print(f"- log keyword: {tool_plan.get('log_keyword')}")

    print("\n[bold cyan]Selected tools:[/bold cyan]")
    for tool in result.get("selected_tools", []):
        print(f"- {tool}")

    print("\n[bold cyan]Retrieved chunks:[/bold cyan]")
    for item in result.get("retrieved_chunks", []):
        source = item["metadata"].get("source")
        similarity = item["similarity"]
        print(f"- {source} | similarity={similarity:.3f}")

    print_tool_evidence_summary(result.get("tool_outputs", {}))

    print("\n[bold cyan]Deterministic evidence summary:[/bold cyan]")
    print(result.get("evidence_summary", "No evidence summary generated."))

    print("\n[bold cyan]Answer validation:[/bold cyan]")
    print(f"- format valid: {result.get('answer_valid')}")
    print(f"- missing sections: {result.get('missing_sections', [])}")
    print(f"- quality ok: {result.get('answer_quality_ok')}")
    print(f"- quality issues: {result.get('quality_issues', [])}")
    print(f"- correction applied: {result.get('correction_applied')}") 

    print("\n[bold green]OpsPilot Agent Answer:[/bold green]\n")
    print(result.get("final_answer", "No final answer generated."))

if __name__ == "__main__":
    main()