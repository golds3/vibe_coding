"""CLI entry point for running the UI design LangGraph agent."""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Iterable

# Ensure src/ is importable when running `python main.py`
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, Interrupt

from src.graph import build_graph


def _read_prd(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"PRD 文件不存在：{path}")
    return path.read_text(encoding="utf-8")


def _format_interrupt(value: object) -> str:
    if isinstance(value, dict):
        message = value.get("message") or value.get("prompt")
        if message:
            return str(message)
    return str(value)


def _prompt_user(interrupts: Iterable[Interrupt]) -> str:
    text = "\n".join(_format_interrupt(item.value) for item in interrupts)
    while True:
        answer = input(f"\n{text}\n> ").strip()
        if answer:
            return answer
        print("请输入有效选项，例如 A/B/C/D/E。")


def run(prd_file: Path) -> None:
    prd_text = _read_prd(prd_file)
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    payload: Command | dict | None = {"prd_text": prd_text}
    while payload is not None:
        stream = graph.stream(payload, config, stream_mode="updates")
        payload = None
        for event in stream:
            if "__interrupt__" in event:
                user_answer = _prompt_user(event["__interrupt__"])
                payload = Command(resume=user_answer)
                break

    final_state = graph.get_state(config).values
    image_path = final_state.get("image_path")
    if image_path:
        print(f"UI 设计图已生成：{image_path}")
    else:
        print("未能生成 UI 设计图，请检查日志。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI 设计 LangGraph Agent")
    parser.add_argument(
        "--prd-file",
        required=True,
        type=Path,
        help="指向 PRD 文档 (markdown 或 txt)",
    )
    args = parser.parse_args()
    run(args.prd_file)
