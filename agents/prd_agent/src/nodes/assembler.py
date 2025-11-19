"""Assembler node writes the final PRD to disk."""
from __future__ import annotations

from pathlib import Path
from typing import List

from src.state import PRDState, TableSchema


class AssemblerNode:
    """Serializes the PRD sections and writes a markdown artifact."""

    def __init__(self, output_path: str = "outputs/prd.md") -> None:
        self.output_path = Path(output_path)

    def _render_features(self, state: PRDState) -> str:
        features = state.get("features", [])
        lines: List[str] = ["## 功能列表（Feature List)"]
        for idx, feature in enumerate(features, start=1):
            lines.append(f"### 功能 {idx}: {feature['name']}")
            lines.append(f"- 功能描述：{feature['description']}")
            lines.append(f"- 输入：{', '.join(feature['inputs'])}")
            lines.append(f"- 输出：{', '.join(feature['outputs'])}")
            lines.append(f"- 前置条件：{', '.join(feature['preconditions'])}")
            lines.append(f"- 后置条件：{', '.join(feature['postconditions'])}")
            lines.append(f"- 边界场景：{', '.join(feature['edge_cases'])}")
            lines.append(f"- 依赖：{', '.join(feature['dependencies'])}")
            lines.append("")
        return "\n".join(lines)

    def _render_tables(self, tables: List[TableSchema]) -> str:
        parts: List[str] = []
        for table in tables:
            parts.append(f"### {table['name']}")
            parts.append(f"描述：{table['description']}")
            parts.append(f"主键策略：{table['primary_key']}")
            parts.append("字段说明：")
            parts.append("| 字段 | 类型 | 描述 | 约束 |")
            parts.append("| --- | --- | --- | --- |")
            for field in table["fields"]:
                parts.append(
                    f"| {field['name']} | {field['type']} | {field['description']} | {field['constraints']} |"
                )
            parts.append("")
        return "\n".join(parts)

    def _render_api(self, state: PRDState) -> str:
        apis = state.get("apis", [])
        chunks: List[str] = ["## 接口设计（API Contract)"]
        for api in apis:
            chunks.append(f"### {api['name']}")
            chunks.append(f"- URL：`{api['url']}`")
            chunks.append(f"- Method：{api['method']}")
            chunks.append("- Request：")
            chunks.append("| 字段 | 类型 | 必填 | 说明 |")
            chunks.append("| --- | --- | --- | --- |")
            for field in api.get("request", []):
                required = "是" if field.get("required") else "否"
                chunks.append(
                    f"| {field.get('name','-')} | {field.get('type','-')} | {required} | {field.get('description','')} |"
                )
            chunks.append("- Response：")
            chunks.append("| 字段 | 类型 | 必填 | 说明 |")
            chunks.append("| --- | --- | --- | --- |")
            for field in api.get("response", []):
                required = "是" if field.get("required") else "否"
                chunks.append(
                    f"| {field.get('name','-')} | {field.get('type','-')} | {required} | {field.get('description','')} |"
                )
            if api.get("errors"):
                chunks.append("- 错误码：")
                for code, desc in api.get("errors", {}).items():
                    chunks.append(f"  - {code}：{desc}")
            if api.get("example"):
                chunks.append("- 样例：")
                chunks.append("```json")
                chunks.append(str(api["example"]))
                chunks.append("```")
            chunks.append("")
        return "\n".join(chunks)

    def _render_dtos(self, state: PRDState) -> str:
        dtos = state.get("dto_contracts", [])
        lines: List[str] = ["### 服务之间的数据契约（DTO)"]
        for dto in dtos:
            lines.append(
                f"- {dto['provider']} -> {dto['consumer']}：载荷 {dto['payload']}，备注：{dto['notes']}"
            )
        return "\n".join(lines)

    def __call__(self, state: PRDState) -> PRDState:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        title = f"# {state.get('project_name', '产品')} PRD"
        intro = "\n".join(
            [
                "## 项目背景与目标",
                f"### 背景\n{state.get('background', '')}",
                f"### 价值\n{state.get('value', '')}",
                "### 用户群体",
                "- " + "\n- ".join(state.get("user_segments", [])),
                f"### 未来愿景\n{state.get('vision', '')}",
            ]
        )
        frameworks = state.get("frameworks", {})
        framework_lines = ""
        if frameworks:
            items = []
            backend = ", ".join(frameworks.get("backend", []))
            frontend = ", ".join(frameworks.get("frontend", []))
            orchestration = ", ".join(frameworks.get("orchestration", []))
            if backend:
                items.append(f"- 后端栈：{backend}")
            if frontend:
                items.append(f"- 前端栈：{frontend}")
            if orchestration:
                items.append(f"- 编排与集成：{orchestration}")
            rationale = frameworks.get("rationale")
            if rationale:
                items.append(f"- 选型说明：{rationale}")
            framework_lines = "\n".join(["### 技术栈推荐"] + items)

        architecture_sections = [
            "## 总体架构设计",
            f"### 业务架构\n{state.get('business_architecture', '')}",
            f"### 技术架构\n{state.get('technical_architecture', '')}",
        ]
        if framework_lines:
            architecture_sections.append(framework_lines)
        architecture_sections.extend(
            [
                f"### 数据流/调用链\n{state.get('data_flow', '')}",
                f"### 扩展性考虑\n{state.get('scalability', '')}",
            ]
        )
        architecture = "\n".join(architecture_sections)
        feature_section = self._render_features(state)
        data_model = "\n".join(
            [
                "## 数据模型设计",
                "### 核心数据实体",
                "- " + "\n- ".join(state.get("core_entities", [])),
                "### 数据表结构",
                self._render_tables(state.get("tables", [])),
                self._render_dtos(state),
            ]
        )
        api_section = self._render_api(state)
        nfr = state.get("nfr", {})
        nfr_section = "\n".join(
            [
                "## 非功能性需求（NFR)",
                f"- 性能：{nfr.get('performance', '')}",
                f"- 安全：{nfr.get('security', '')}",
                f"- 可扩展性：{nfr.get('scalability', '')}",
                f"- 可观测性：{nfr.get('observability', '')}",
                f"- 国际化：{nfr.get('internationalization', '')}",
                f"- 依赖外部服务：{nfr.get('external_services', '')}",
            ]
        )
        risks = "\n".join(
            [
                "## 风险与难点分析",
                "- " + "\n- ".join(state.get("risks", [])),
            ]
        )
        glossary = "\n".join(
            [
                "## 附录",
                "### 术语表",
                "- " + "\n- ".join(state.get("glossary", [])),
            ]
        )

        content = "\n\n".join(
            [
                title,
                intro,
                architecture,
                feature_section,
                data_model,
                api_section,
                nfr_section,
                risks,
                glossary,
            ]
        )
        self.output_path.write_text(content, encoding="utf-8")
        return {**state, "prd_markdown": content}
