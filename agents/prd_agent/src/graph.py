"""LangGraph pipeline definition."""
from __future__ import annotations

from langgraph.graph import StateGraph

from src.nodes.api import ApiNode
from src.nodes.architecture import ArchitectureNode
from src.nodes.assembler import AssemblerNode
from src.nodes.datamodel import DataModelNode
from src.nodes.features import FeatureNode
from src.nodes.intent import IntentNode
from src.nodes.nfr import NfrNode
from src.state import PRDState


def build_graph() -> StateGraph:
    """Constructs and compiles the LangGraph state machine."""
    builder: StateGraph = StateGraph(PRDState)
    builder.add_node("intent", IntentNode())
    builder.add_node("features", FeatureNode())
    builder.add_node("architecture", ArchitectureNode())
    builder.add_node("datamodel", DataModelNode())
    builder.add_node("api", ApiNode())
    builder.add_node("nfr", NfrNode())
    builder.add_node("assembler", AssemblerNode())

    builder.set_entry_point("intent")
    builder.add_edge("intent", "features")
    builder.add_edge("features", "architecture")
    builder.add_edge("architecture", "datamodel")
    builder.add_edge("datamodel", "api")
    builder.add_edge("api", "nfr")
    builder.add_edge("nfr", "assembler")

    return builder.compile()


__all__ = ["build_graph"]
