"""Entry-point for running the LangGraph PRD agent."""
from __future__ import annotations

from pathlib import Path

import typer

from src.graph import build_graph
from src.llm import configure_llm
from src.state import PRDState

app = typer.Typer(help="生成结构化 PRD 的 LangGraph Agent")


@app.command()
def main(
    input: str = typer.Option(..., "--input", "-i", help="项目需求描述"),
    language: str | None = typer.Option(
        None, "--language", "-l", help="若已确定技术栈，可直接在此指定"
    ),
    model: str | None = typer.Option(
        None, "--model", help="自定义 LLM 模型（默认 gpt-4o-mini，可通过 LLM_MODEL env 覆盖）"
    ),
    temperature: float = typer.Option(
        0.15,
        "--temperature",
        help="LLM 温度（可通过 LLM_TEMPERATURE env 覆盖）",
    ),
) -> None:
    configure_llm(model=model, temperature=temperature)
    graph = build_graph()
    initial_state: PRDState = {"user_input": input}
    if language:
        initial_state["tech_stack"] = language
    result = graph.invoke(initial_state)
    output_path = Path("outputs/prd.md").resolve()
    typer.secho(f"PRD 已生成：{output_path}", fg="green")
    if result.get("project_name"):
        typer.echo(f"项目：{result['project_name']}")


if __name__ == "__main__":
    app()
