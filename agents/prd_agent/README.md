# LangGraph PRD Agent

## 项目介绍
该项目实现了一个基于 LangGraph 的多节点 Agent，可根据用户输入的 "项目需求" 自动生成符合《PRD 标准结构》的 Markdown 文档。每个节点都会调用 LLM（默认 `gpt-4o-mini`，可配置）实时生成各章节内容，因此只需提供 API Key 即可获得高度定制化的 PRD。

## LangGraph 流程图说明
```
IntentNode -> FeatureNode -> ArchitectureNode -> DataModelNode -> ApiNode -> NfrNode -> AssemblerNode
```
- **IntentNode**：解析输入、识别领域与价值。
- **FeatureNode**：按领域生成功能列表。
- **ArchitectureNode**：描述业务与技术架构以及整体扩展性。
- **DataModelNode**：给出实体、表结构与 DTO 契约。
- **ApiNode**：输出接口定义与示例。
- **NfrNode**：补充非功能性需求、依赖及风险。
- **AssemblerNode**：拼装 Markdown 并写入 `outputs/prd.md`。

## 环境准备
1. 准备 LLM 凭证（默认使用 `langchain-openai` 提供的 `ChatOpenAI`），在 shell 中导出：
   ```bash
   export OPENAI_API_KEY=sk-***
   # 如需自定义模型/温度可设 LLM_MODEL、LLM_TEMPERATURE 或 CLI 参数
   ```
2. 可选：若使用自建兼容服务，设置 `OPENAI_BASE_URL`。

## 如何运行
```bash
cd project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --input "为我生成一个博客系统的prd" --language python --model gpt-4o-mini
```
运行过程中，Agent 会在架构阶段提示输入“想用什么语言开发”，以便 LLM 基于该语言推荐热门框架；若希望跳过交互，可加上 `--language python` 参数。执行完毕后，在 `outputs/prd.md` 中即可查看完整 PRD。

## 示例输入与输出
- **输入**：`python main.py --input "为我生成一个博客系统的prd"`
- **输出**：`outputs/prd.md`，包含项目背景、架构、功能列表、数据模型、API 契约、NFR、风险及附录等完整章节。
