def ensure_tool_footer(answer: str, selected_tools: list[str]) -> str:
    """
    Ensure the final answer explicitly lists all selected tools.

    This improves traceability and avoids relying on the LLM
    to consistently mention every tool it used.
    """
    if not selected_tools:
        return answer

    answer_lower = answer.lower()

    missing_tools = [
        tool for tool in selected_tools
        if tool.lower() not in answer_lower
    ]

    if not missing_tools:
        return answer

    footer = "\n\nTool trace:\n" + "\n".join(
        f"- {tool}" for tool in missing_tools
    )

    return answer.strip() + footer