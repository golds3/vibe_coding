"""Typed state definitions shared across LangGraph nodes."""
from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class FeatureSpec(TypedDict):
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    preconditions: List[str]
    postconditions: List[str]
    edge_cases: List[str]
    dependencies: List[str]


class TableField(TypedDict):
    name: str
    type: str
    description: str
    constraints: str


class TableSchema(TypedDict):
    name: str
    description: str
    fields: List[TableField]
    primary_key: str


class DTOContract(TypedDict):
    provider: str
    consumer: str
    payload: Dict[str, Any]
    notes: str


class ApiField(TypedDict):
    name: str
    type: str
    required: bool
    description: str


class ApiSpec(TypedDict):
    name: str
    url: str
    method: str
    request: List[ApiField]
    response: List[ApiField]
    errors: Dict[str, str]
    example: Dict[str, Any]


class FrameworkInsight(TypedDict, total=False):
    language: str
    rationale: str
    backend: List[str]
    frontend: List[str]
    orchestration: List[str]


class PRDState(TypedDict, total=False):
    user_input: str
    domain: str
    project_name: str
    project_goal: str
    tech_stack: str
    frameworks: FrameworkInsight
    background: str
    value: str
    user_segments: List[str]
    vision: str
    features: List[FeatureSpec]
    business_architecture: str
    technical_architecture: str
    data_flow: str
    scalability: str
    core_entities: List[str]
    tables: List[TableSchema]
    dto_contracts: List[DTOContract]
    apis: List[ApiSpec]
    nfr: Dict[str, str]
    risks: List[str]
    glossary: List[str]
    prd_markdown: str


__all__ = [
    "ApiField",
    "ApiSpec",
    "DTOContract",
    "FeatureSpec",
    "FrameworkInsight",
    "PRDState",
    "TableField",
    "TableSchema",
]
