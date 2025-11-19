"""Render PRD insights into an HTML mockup and capture a screenshot."""
from __future__ import annotations

import asyncio
import io
import logging
import os
from pathlib import Path
from typing import Dict, List, Sequence

from jinja2 import Template
from PIL import Image, ImageDraw, ImageFont
from pyppeteer import launch

from src.state import UIState

logger = logging.getLogger(__name__)


STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "极简": {
        "background": "#f6f7fb",
        "surface": "#ffffff",
        "card": "#ffffff",
        "text": "#1e2235",
        "muted_text": "#5f6274",
        "accent": "#2563eb",
        "accent_secondary": "#93c5fd",
        "border": "rgba(15, 23, 42, 0.08)",
        "shadow": "0 25px 55px rgba(15,23,42,0.18)",
    },
    "暗黑": {
        "background": "#05060b",
        "surface": "#0f172a",
        "card": "#111827",
        "text": "#f8fafc",
        "muted_text": "#9ca3af",
        "accent": "#38bdf8",
        "accent_secondary": "#6366f1",
        "border": "rgba(148,163,184,0.2)",
        "shadow": "0 30px 60px rgba(0,0,0,0.45)",
    },
    "玻璃拟态": {
        "background": "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)",
        "surface": "rgba(255,255,255,0.15)",
        "card": "rgba(255,255,255,0.35)",
        "text": "#0f172a",
        "muted_text": "#1f2937",
        "accent": "#ec4899",
        "accent_secondary": "#8b5cf6",
        "border": "rgba(255,255,255,0.45)",
        "shadow": "0 25px 55px rgba(31,41,55,0.25)",
    },
    "Material Design": {
        "background": "#eceff1",
        "surface": "#fefefe",
        "card": "#ffffff",
        "text": "#101828",
        "muted_text": "#475467",
        "accent": "#ff7a18",
        "accent_secondary": "#ffb347",
        "border": "rgba(16,24,40,0.08)",
        "shadow": "0 25px 50px rgba(15,23,42,0.15)",
    },
    "插画风": {
        "background": "#fdf5e6",
        "surface": "#fff8e1",
        "card": "#ffffff",
        "text": "#2f1c46",
        "muted_text": "#6a4c93",
        "accent": "#ff6b6b",
        "accent_secondary": "#ffa36c",
        "border": "rgba(106, 76, 147, 0.2)",
        "shadow": "0 25px 40px rgba(106,76,147,0.2)",
    },
}

HTML_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Inter', 'HarmonyOS Sans', 'PingFang SC', sans-serif;
      background: {{ palette.background }};
      color: {{ palette.text }};
      padding: 32px;
    }
    .canvas {
      max-width: 1280px;
      margin: 0 auto;
      background: {{ palette.surface }};
      border-radius: 32px;
      padding: 48px;
      box-shadow: {{ palette.shadow }};
      border: 1px solid {{ palette.border }};
    }
    .hero {
      background: linear-gradient(135deg, {{ palette.accent }} 0%, {{ palette.accent_secondary }} 100%);
      padding: 48px;
      border-radius: 28px;
      color: white;
      display: flex;
      justify-content: space-between;
      gap: 32px;
    }
    .hero h1 { margin: 0 0 12px; font-size: 40px; }
    .hero p { margin: 0; font-size: 18px; line-height: 1.6; }
    .hero .style-tag {
      font-size: 16px;
      padding: 8px 16px;
      border: 1px solid rgba(255,255,255,0.5);
      border-radius: 999px;
      display: inline-block;
      margin-bottom: 16px;
      letter-spacing: 2px;
      text-transform: uppercase;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 24px;
    }
    .page-card {
      background: {{ palette.card }};
      border: 1px solid {{ palette.border }};
      border-radius: 24px;
      padding: 32px;
      box-shadow: {{ palette.shadow }};
    }
    .page-card h2 {
      margin: 0 0 12px;
      font-size: 24px;
      color: {{ palette.text }};
    }
    .page-card p {
      margin: 0 0 16px;
      color: {{ palette.muted_text }};
    }
    .pill {
      display: inline-flex;
      padding: 6px 14px;
      margin: 4px 8px 4px 0;
      border-radius: 999px;
      background: rgba(37,99,235,0.08);
      color: {{ palette.accent }};
      font-size: 13px;
      font-weight: 600;
    }
    .list {
      list-style: none;
      margin: 12px 0 0;
      padding: 0;
      color: {{ palette.muted_text }};
    }
    .list li { margin-bottom: 6px; font-size: 14px; }
    .section-title {
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: {{ palette.muted_text }};
      margin-top: 20px;
      margin-bottom: 8px;
    }
    .interactions {
      margin-top: 40px;
      padding: 32px;
      background: {{ palette.card }};
      border-radius: 24px;
      border: 1px solid {{ palette.border }};
    }
    .interaction-item {
      padding: 16px 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .interaction-item:last-child { border-bottom: 0; }
    .interaction-item strong {
      color: {{ palette.accent }};
      display: block;
      font-size: 15px;
      margin-bottom: 6px;
    }
    .prompt-box {
      margin-top: 32px;
      padding: 24px;
      border-radius: 20px;
      border: 1px dashed {{ palette.border }};
      background: rgba(255,255,255,0.25);
      color: {{ palette.muted_text }};
      font-size: 13px;
    }
  </style>
</head>
<body>
  <div class="canvas">
    <section class="hero">
      <div>
        <div class="style-tag">{{ style_label }}</div>
        <h1>{{ hero_title }}</h1>
        <p>{{ hero_summary }}</p>
      </div>
      <div>
        <p>关键信息：</p>
        <ul class="list">
          {% for point in hero_highlights %}
            <li>• {{ point }}</li>
          {% endfor %}
        </ul>
      </div>
    </section>

    <section class="grid" style="margin-top: 40px;">
      {% for block in blocks %}
      <article class="page-card">
        <h2>{{ block.page }}</h2>
        <p>{{ block.summary or '核心流程与价值叙事' }}</p>
        <div>
          {% for section in block.sections %}
            <span class="pill">{{ section }}</span>
          {% endfor %}
        </div>
        <div class="section-title">重点组件</div>
        <div>
          {% for component in block.components %}
            <span class="pill" style="background: rgba(255,255,255,0.1); color: {{ palette.text }};">{{ component }}</span>
          {% endfor %}
        </div>
        <div class="section-title">数据点</div>
        <ul class="list">
          {% for dp in block.data_points %}
            <li>{{ dp }}</li>
          {% endfor %}
        </ul>
        <div class="section-title">核心任务</div>
        <ul class="list">
          {% for task in block.tasks %}
            <li>{{ task }}</li>
          {% endfor %}
        </ul>
        {% if block.layout %}
        <div class="section-title">布局策略</div>
        <ul class="list">
          <li>栅格：{{ block.layout.grid }}</li>
          <li>流向：{{ block.layout.flow }}</li>
          <li>响应式：{{ block.layout.responsive }}</li>
        </ul>
        {% endif %}
      </article>
      {% endfor %}
    </section>

    <section class="interactions">
      <h2>交互与反馈</h2>
      {% for item in interactions %}
      <div class="interaction-item">
        <strong>{{ item.trigger }}</strong>
        <div>{{ item.response }}</div>
        <small>{{ item.feedback }}</small>
      </div>
      {% endfor %}
    </section>

    <div class="prompt-box">
      <strong>Prompt 概述：</strong>
      <div>{{ prompt }}</div>
    </div>
  </div>
</body>
</html>
"""
)


def _resolve_palette(style_label: str) -> Dict[str, str]:
    return STYLE_PRESETS.get(style_label, STYLE_PRESETS["极简"])


def _build_blocks(state: UIState) -> List[Dict[str, Sequence[str]]]:
    pages = {page.get("name"): page for page in state.get("pages", [])}
    components = {comp.get("page"): comp for comp in state.get("component_tree", [])}
    layouts = {layout.get("page"): layout for layout in state.get("layout_plan", [])}

    blocks: List[Dict[str, Sequence[str]]] = []
    for info in state.get("information_blocks", []):
        page_name = info.get("page", "Screen")
        block = {
            "page": page_name,
            "summary": pages.get(page_name, {}).get("summary", ""),
            "sections": info.get("sections", []),
            "data_points": info.get("data_points", []),
            "tasks": info.get("user_tasks", []),
            "components": components.get(page_name, {}).get("components", []),
            "layout": layouts.get(page_name),
        }
        blocks.append(block)

    if not blocks and pages:
        first_page = next(iter(pages.values()))
        blocks.append(
            {
                "page": first_page.get("name", "Primary Screen"),
                "summary": first_page.get("summary", ""),
                "sections": ["Hero", "Highlights", "Actions"],
                "data_points": ["主要指标", "价值陈述", "CTA 状态"],
                "tasks": ["引导用户完成主要流程"],
                "components": ["Hero Title", "CTA Button", "Benefit Cards"],
                "layout": layouts.get(first_page.get("name")),
            }
        )
    return blocks


def render_ui_html(state: UIState, prompt: str) -> str:
    blocks = _build_blocks(state)
    style_label = state.get("preferred_style", "极简")
    palette = _resolve_palette(style_label)

    hero_title = blocks[0]["page"] if blocks else "UI Draft"
    hero_summary = blocks[0]["summary"] if blocks else "自动生成的 UI 方案预览"
    hero_highlights = [
        f"信息区块：{len(blocks)} 个",
        f"组件数：{sum(len(block['components']) for block in blocks)}",
        f"交互条目：{len(state.get('interaction_map', []))}",
    ]

    html = HTML_TEMPLATE.render(
        style_label=style_label,
        palette=palette,
        hero_title=hero_title,
        hero_summary=hero_summary,
        hero_highlights=hero_highlights,
        blocks=blocks,
        interactions=state.get("interaction_map", []),
        prompt=prompt,
    )
    return html


def _resolve_browser_executable() -> str | None:
    env_override = os.getenv("CHROMIUM_PATH") or os.getenv("PUPPETEER_EXECUTABLE_PATH")
    if env_override and Path(env_override).exists():
        return env_override
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


async def _screenshot_html(
    html_path: Path, width: int, height: int, wait_ms: int = 1000
) -> bytes:
    launch_kwargs = {
        "headless": True,
        "args": ["--no-sandbox", "--disable-setuid-sandbox"],
        "handleSIGINT": False,
        "handleSIGHUP": False,
        "handleSIGTERM": False,
    }
    executable = _resolve_browser_executable()
    if executable:
        launch_kwargs["executablePath"] = executable

    browser = await launch(**launch_kwargs)
    try:
        page = await browser.newPage()
        await page.setViewport({"width": width, "height": height})
        await page.goto(html_path.as_uri())
        await asyncio.sleep(wait_ms / 1000)
        data = await page.screenshot(fullPage=True)
        return data
    finally:
        await browser.close()


def _parse_size(size: str) -> tuple[int, int]:
    try:
        width_str, height_str = size.lower().split("x")
        return int(width_str), int(height_str)
    except ValueError as exc:
        raise ValueError(f"Invalid size format: {size}") from exc


def text2im(
    prompt: str,
    size: str = "1440x1024",
    *,
    state: UIState | None = None,
    html_output_path: str | Path | None = None,
) -> bytes:
    """Render the UI HTML for the given state and capture a PNG screenshot."""

    if state is None:
        raise ValueError("state must be provided to render UI HTML.")

    html = render_ui_html(state, prompt)
    html_path = Path(html_output_path) if html_output_path else Path("outputs/ui_design.html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    logger.info("UI HTML mockup written to %s", html_path)

    width, height = _parse_size(size)

    try:
        try:
            return asyncio.run(_screenshot_html(html_path, width, height))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(_screenshot_html(html_path, width, height))
            finally:
                loop.close()
    except Exception as exc:
        logger.error("HTML screenshot failed, falling back to placeholder: %s", exc, exc_info=True)
        return _placeholder_image(prompt, width, height)


def _placeholder_image(prompt: str, width: int, height: int) -> bytes:
    image = Image.new("RGB", (width, height), color=(244, 246, 252))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    snippet = (prompt[:300] + "...") if len(prompt) > 300 else prompt
    content = (
        "HTML Mockup Screenshot\n"
        "未能启动浏览器，已回退为占位图。\n"
        f"{snippet}"
    )
    draw.multiline_text((40, 40), content, fill=(46, 56, 86), font=font, spacing=10)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


__all__ = ["render_ui_html", "text2im"]
