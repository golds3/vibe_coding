"""Typed state objects shared between LangGraph nodes."""
from __future__ import annotations

from typing import List, TypedDict


class PageSummary(TypedDict, total=False):
    """High level description of a screen detected in the PRD."""

    name: str
    summary: str
    intent: str
    priority: int


class InformationBlock(TypedDict, total=False):
    """Information hierarchy inferred for a page."""

    page: str
    sections: List[str]
    data_points: List[str]
    user_tasks: List[str]


class ComponentBlueprint(TypedDict, total=False):
    """Component tree describing UI widgets and their grouping."""

    page: str
    group: str
    components: List[str]
    rationale: str


class LayoutInstruction(TypedDict, total=False):
    """Layout level details for arranging components on a canvas."""

    page: str
    grid: str
    hero: str
    flow: str
    responsive: str
    emphasis: List[str]


class InteractionModel(TypedDict, total=False):
    """Interaction logic tying triggers to expected responses."""

    trigger: str
    response: str
    feedback: str
    priority: str


class UIState(TypedDict, total=False):
    """State object propagated between LangGraph nodes."""

    prd_text: str
    pages: List[PageSummary]
    information_blocks: List[InformationBlock]
    component_tree: List[ComponentBlueprint]
    layout_plan: List[LayoutInstruction]
    interaction_map: List[InteractionModel]
    preferred_style: str
    style_question: str
    ui_prompt: str
    ui_document_path: str
    image_bytes: bytes
    image_path: str
