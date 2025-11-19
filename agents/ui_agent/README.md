# UI Agent

基于 LangGraph 构建的 "UI 设计 Agent"，输入一份 PRD 或需求文档后，会完成页面识别、信息架构推断、组件树拆解、布局/交互设计，并在人机协同节点确认偏好的视觉风格。随后会把结构化结果渲染成一份前端风格的 HTML 页面，并通过 headless Chromium 截图生成最终 UI PNG。

## 流程节点
- **PageDetectorNode**：扫描 PRD 文本中的标题与语义，生成候选页面清单与优先级。
- **InfoExtractorNode**：根据每个页面的概要提炼信息结构、展示区块和关键数据点。
- **ComponentInferNode**：把信息区块映射成组件树，包含导航、卡片、CTA 等复用模块。
- **LayoutInferNode**：给出布局描述（栅格、响应式策略、视觉流向）。
- **InteractionInferNode**：推导触发 -> 响应的交互逻辑与反馈层次。
- **AskStyleNode**（Human-in-the-loop）：暂停图执行，向操作者提问“偏好的 UI 风格”，等待输入 A/B/C/D/E。
- **ImageGenNode**：把组件、布局、交互与风格整合成专业 prompt，调用 `image_gen.text2im(..., size="1440x1024")` 渲染 HTML 模板并截图得到 PNG。
- **AssemblerNode**：把 PNG 写入 `outputs/ui_design.png`（同时镜像一份 `outputs/ui_homepage.png`），并输出提示文本方便审阅。

节点连接顺序严格遵循：PageDetector → InfoExtractor → ComponentInfer → LayoutInfer → InteractionInfer → AskStyle → ImageGen → Assembler。

## 运行方式
1. （推荐）创建虚拟环境并安装依赖：
   ```bash
   cd ui_agent
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 准备一份 PRD 文档，例如 `examples/prd.md`（见下方示例）。
3. 执行脚本，并在 AskStyle 节点输入 A/B/C/D/E：
   ```bash
   python main.py --prd-file examples/prd.md
   ```
4. 首次运行会自动下载 headless Chromium（pyppeteer 依赖），稍等片刻即可完成。成功后会看到提示 `UI 设计图已生成：.../outputs/ui_design.png`，同目录下包含 HTML 模型和 prompt 摘要。

> 若企业环境无法访问 `storage.googleapis.com`，可在运行前设置 `CHROMIUM_PATH=/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome`（或其他浏览器可执行文件），系统会优先使用本地浏览器进行截图。

## 示例 PRD 片段
```markdown
# 智能理财助手 App
## 目标
帮助新手跟踪收益、制定投资计划，并提供 AI 问答。
## 功能
- 首页：展示实时收益、关键 CTA、快捷入口
- 投资组合详情：呈现资产分布、趋势图、调仓建议
- 任务面板：列出待办（补充资产、完成问卷等）
```

## 示例输出
- PNG：`outputs/ui_design.png`（运行后即可在 README 中替换真实截图）。
- 摘要文本：`outputs/ui_design.txt`，包含 prompt 与选定风格。

![UI Design Placeholder](outputs/ui_design.png)
