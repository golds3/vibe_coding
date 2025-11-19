"""Graph builder wiring every node in the required order."""
from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph

from src.nodes import (
    AskStyleNode,
    AssemblerNode,
    ComponentInferNode,
    ImageGenNode,
    InfoExtractorNode,
    InteractionInferNode,
    LayoutInferNode,
    PageDetectorNode,
)
from src.state import UIState


def build_graph(checkpointer: BaseCheckpointSaver | None = None):
    """Constructs and compiles the LangGraph pipeline."""

    builder = StateGraph(UIState)

    builder.add_node("page", PageDetectorNode())
    builder.add_node("info", InfoExtractorNode())
    builder.add_node("component", ComponentInferNode())
    builder.add_node("layout", LayoutInferNode())
    builder.add_node("interaction", InteractionInferNode())
    builder.add_node("ask_style", AskStyleNode(), human=True)
    builder.add_node("image", ImageGenNode())
    builder.add_node("assemble", AssemblerNode())

    builder.set_entry_point("page")
    builder.add_edge("page", "info")
    builder.add_edge("info", "component")
    builder.add_edge("component", "layout")
    builder.add_edge("layout", "interaction")
    builder.add_edge("interaction", "ask_style")
    builder.add_edge("ask_style", "image")
    builder.add_edge("image", "assemble")

    return builder.compile(checkpointer=checkpointer)


__all__ = ["build_graph"]
