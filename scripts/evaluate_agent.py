import json
from pathlib import Path
from typing import Any

from rich import print

from app.agent.graph import build_graph
from app.config import DATA_DIR


EVAL_FILE = Path(DATA_DIR) / "eval" / "eval_cases.json"
OUTPUT_FILE = Path(DATA_DIR) / "eval" / "eval_results.json"


def load_eval_cases() -> list[dict[str, Any]]:
    with EVAL_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_case(case: dict[str, Any], graph) -> dict[str, Any]:
    result = graph.invoke(
        {
            "question": case["question"],
        }
    )

    tool_plan = result.get("tool_plan", {})
    selected_tools = result.get("selected_tools", [])

    expected_tools = sorted(case["expected_tools"])
    actual_tools = sorted(selected_tools)

    checks = {
        "service_match": tool_plan.get("service") == case["expected_service"],
        "log_keyword_match": tool_plan.get("log_keyword") == case["expected_log_keyword"],
        "tools_match": actual_tools == expected_tools,
        "answer_valid": result.get("answer_valid") is True,
        "answer_quality_ok": result.get("answer_quality_ok") is True,
    }

    passed = all(checks.values())

    return {
        "id": case["id"],
        "passed": passed,
        "checks": checks,
        "expected": {
            "service": case["expected_service"],
            "log_keyword": case["expected_log_keyword"],
            "tools": expected_tools,
        },
        "actual": {
            "service": tool_plan.get("service"),
            "log_keyword": tool_plan.get("log_keyword"),
            "tools": actual_tools,
            "missing_sections": result.get("missing_sections", []),
            "quality_issues": result.get("quality_issues", []),
            "correction_applied": result.get("correction_applied"),
        },
    }


def main() -> None:
    cases = load_eval_cases()
    graph = build_graph()

    results: list[dict[str, Any]] = []

    print(f"[bold cyan]Running {len(cases)} eval cases...[/bold cyan]\n")

    for case in cases:
        eval_result = evaluate_case(case, graph)
        results.append(eval_result)

        status = "[bold green]PASS[/bold green]" if eval_result["passed"] else "[bold red]FAIL[/bold red]"
        print(f"{status} {eval_result['id']}")

        for check_name, check_passed in eval_result["checks"].items():
            check_status = "✅" if check_passed else "❌"
            print(f"  {check_status} {check_name}")

        if not eval_result["passed"]:
            print("  [yellow]Expected:[/yellow]", eval_result["expected"])
            print("  [yellow]Actual:[/yellow]", eval_result["actual"])

        print()

    passed_count = sum(1 for result in results if result["passed"])
    total_count = len(results)

    summary = {
        "total": total_count,
        "passed": passed_count,
        "failed": total_count - passed_count,
        "pass_rate": round(passed_count / total_count, 2) if total_count else 0,
    }

    report = {
        "summary": summary,
        "results": results,
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("[bold cyan]Evaluation summary:[/bold cyan]")
    print(f"- passed: {passed_count}/{total_count}")
    print(f"- failed: {total_count - passed_count}/{total_count}")
    print(f"- pass rate: {summary['pass_rate']}")
    print(f"- report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()