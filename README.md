# 智能 CSV 数据分析多 Agent 智囊团

> 基于多智能体协作的智能 CSV 数据分析助手，将原始 CSV 数据自动转化为具备统计学意义的分析报告与清洗策略。

## 📌 项目简介

本项目是一个基于多 Agent 协作（Orchestrator-Workers 模式）的智能数据分析系统。用户只需上传一个 CSV 文件并提出分析需求，系统即可自动完成数据读取、质量诊断、清洗策略制定，并最终生成一份结构化的数据分析报告。

项目的核心价值在于**解耦**与**稳定性**：通过将“数据探索”、“数据清洗”、“报告撰写”三个职责分配给独立的 Agent，避免了单 Agent 在处理复杂任务时容易出现的上下文混乱与决策瘫痪问题。

## ✨ 核心功能

- **多 Agent 协作**：探索官（读取数据）、清洗员（制定策略）、首席分析师（撰写报告），职责分明，协同工作。
- **多级编码回退**：自动尝试 `utf-8` / `gbk` / `gb18030` 等多种编码，并支持 `errors='ignore'` 兜底，解决 Windows 环境下的跨平台文件兼容问题。
- **LLM 幻觉防御**：不依赖大模型自行调错，由 Python 代码层完成文件路径与编码的强校验与重试，避免模型“甩锅”给用户。
- **专业数据诊断**：自动识别缺失值、异常值、分布偏度，并给出符合统计学原理的清洗建议（如右偏数据使用中位数填充）。

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| AI 框架 | HelloAgents (SimpleAgent, Tool) |
| 大语言模型 | DeepSeek V4.1 |
| 数据处理 | Pandas |
| 后端服务 | FastAPI |
| 语言 | Python 3.11 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install hello-agents[all] pandas fastapi uvicorn requests
2. 配置 API 密钥
在项目根目录创建 .env 文件：

env
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_api_base_url
LLM_MODEL_ID=your_model_name
3. 准备数据
在项目根目录放置一个 CSV 文件，例如 data.csv：

csv
id,name,age,salary,department
1,张三,25,15000,技术部
2,李四,30,25000,技术部
3,王五,28,,产品部
4,赵六,35,40000,市场部
5,孙七,22,8000,技术部
4. 运行项目
终端交互模式：

bash
python main.py
输入你希望分析的文件名，例如：帮我分析一下 data.csv 这个文件。

API 服务模式：

bash
python server.py
# 浏览器访问 http://localhost:8000/docs 测试 API
📖 使用示例
text
👤 你：帮我分析一下 data.csv 这个文件，看看有没有什么问题

🔍 第一步：数据探索官正在读取数据...
🧹 第二步：数据清洗员正在制定清洗策略...
📊 第三步：首席分析师正在撰写报告...

🤖 最终分析报告：
## 一、数据概况
- 数据规模：7 行数据，5 个字段
- 字段类型：id/age/salary 为数值型，name/department 为文本型

## 二、发现的问题
### 1. ⚠️ salary 字段存在缺失值
- 对应记录为“王五”，部门为“产品部”

### 2. ⚠️ 数据分布偏度分析
- salary 均值 26,000，中位数 21,500，分布右偏
- 建议：缺失值不应使用均值填充，应使用中位数

## 三、处理建议
1. 优先联系业务方补录王五的薪资
2. 若无法补录，使用全局中位数 21,500 填充，并新增 `salary_is_imputed` 标记
3. 当前不删除任何记录，50,000 在 IQR 法下无统计异常
🧠 踩坑记录与工程经验
在开发过程中，我解决了以下核心痛点：

1. 大模型工具调用死循环
当本地文件读取失败时，模型会陷入“重试-报错-重试”的瘫痪状态。
解决方案：修改 System Prompt，明确禁止写建议书，强制要求遇到失败立即切换至 search_web 或其他降级策略。

2. 大模型参数丢失/改名
模型调用工具时会将 query 改名为 search_query 导致搜索失败。
解决方案：在 Python 代码层面做防御性编程，用 or 兼容多种参数名，并返回明确的错误提示迫使模型修正。

3. 跨平台文件编码壁垒
Windows 下 Excel 保存的 CSV 默认为 GBK 编码，而 Python 默认按 UTF-8 读取会报 UnicodeDecodeError。
解决方案：在工具层实现多级编码回退（utf-8 → gbk → gb18030 → utf-8-sig），并最终使用 errors='ignore' 结合 io.StringIO 绕过 Pandas 的路径强校验。

4. 大模型“甩锅”行为
当工具连续报错时，大模型倾向于生成长篇诊断报告，建议用户手动排查。
解决方案：作为工程师，不能盲目听信大模型的诊断。直接深入底层 Python 代码，用绝对可靠的工程手段修补漏洞。

🗂️ 项目结构
text
Data-Analyst-Agent/
├── main.py              # 主程序（多 Agent 协作逻辑）
├── server.py            # FastAPI 后端服务
├── client.py            # Python 客户端测试脚本
├── index.html           # 前端聊天界面
├── data.csv             # 示例数据
├── requirements.txt     # 依赖列表
├── .env.example         # 环境变量示例
├── .gitignore           # Git 忽略规则
└── README.md            # 项目文档
🔮 未来计划
□ 支持更多数据格式（Excel、JSON、Parquet）
□ 集成数据可视化工具（自动生成柱状图、折线图）
□ 引入向量数据库，实现基于语义的字段检索
□ 支持多轮对话式数据分析
□ 部署为 Web 服务，支持文件上传与报告下载
👤 作者
GitHub: @yeandxino

🙏 致谢
感谢 Datawhale 社区和 Hello-Agents 项目提供的学习资源与框架支持。
