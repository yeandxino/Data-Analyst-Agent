# Data-Analyst-Agent · 智能 CSV 数据分析多 Agent 智囊团

> 把一份 CSV 丢进去，三个 Agent 依次完成「探索 → 清洗 → 归因出报告」。
> 用代码层兜底，解决大模型的参数丢失、编码冲突与编造结论。

![python](https://img.shields.io/badge/python-3.10%2B-blue) ![llm](https://img.shields.io/badge/LLM-HelloAgents-orange)

---

## 为什么做这个

手工做一次数据分析要重复四步：看字段 → 处理缺失值 → 跑统计 → 写结论。耗时且易错。

而直接让大模型"分析一下这个表"会翻车：它会编造结论、丢参数、读错编码。

所以这里的设计原则是：**大模型负责判断，代码负责兜底。**

## 三个角色

| Agent | 输入 | 输出 |
|---|---|---|
| 🔍 数据探索官 | CSV 原始数据 | 前 5 行 + 字段类型 / 缺失 / 分布等统计信息 |
| 🧹 数据清洗员 | 探索结果 | 可执行的清洗策略（去重 / 填充 / 类型转换） |
| 📊 首席分析师 | 数据情况 + 清洗策略 | 结构化分析报告（数据概览、问题诊断、建议、结论） |

串行流水线：后一个 Agent 的输入是前一个的输出，出问题能定位到具体环节。

## 三个真实踩过的坑

**1. 大模型传参不稳定**
同一个工具，模型有时传 `file_path`、有时传 `path`、有时传 `filename`。
→ 工具层做**参数名兼容**：三种都接受，并且自动去掉路径两端的引号与空格。传什么都跑得起来。

**2. 路径与编码问题**
模型给的相对路径在不同工作目录下会失效；CSV 编码在 utf-8 / gbk / gb18030 之间漂移。
→ 路径统一按 `main.py` 所在目录解析（相对路径拼绝对路径、绝对路径失效则退回按文件名找）；
→ 读取时用容错模式，避免因个别脏字符整体读取失败。

**3. 编造结论（幻觉）**
模型会在没有依据时补一句"该品类增长显著"。
→ System Prompt 里明确要求结论必须基于给定数据，配合工具层只返回真实统计量，减少无依据推断。

## 快速开始

```bash
git clone https://github.com/yeandxino/Data-Analyst-Agent.git
cd Data-Analyst-Agent

pip install -r requirements.txt
```

**① 配置 API Key**

```bash
# 复制模板，填入你自己的 Key
cp .env.example .env      # Windows: copy .env.example .env
```

`.env` 里填：

```
MODELSCOPE_API_KEY=your_key_here
```

> 也支持任意 OpenAI 兼容服务：改 `LLM_BASE_URL` 与 `LLM_MODEL` 即可（如 DeepSeek）。
> `.env` 已在 `.gitignore` 中，不会被提交。

**② 准备数据**

把要分析的 CSV 放到与 `main.py` 同一目录，仓库自带一个 `data.csv` 示例。

**③ 运行**

```bash
python main.py
```

启动后是交互式对话，直接告诉它要分析哪个文件：

```
=== 数据分析智囊团已启动（输入 '退出' 结束）===

👤 你：帮我分析 data.csv
🔍 第一步：数据探索官正在读取数据...
🧹 第二步：数据清洗员正在制定清洗策略...
📊 第三步：首席分析师正在撰写报告...
```

输入 `退出` 结束。

## 设计取舍

- **为什么坚持串行、不做并行**：清洗策略依赖探索结果，并行会让下游拿到错误输入。稳定性优先。
- **为什么大量代码在"兜底"**：大模型的能力边界不在"会不会写代码"，而在"会不会稳定地按格式输出"。兜底代码就是它的人格补丁。
- **为什么用 HelloAgents 而不是 LangChain**：需要的是"多 Agent + 工具"的最小骨架，HelloAgents 更轻，改起来可控。

## Roadmap

- [ ] 支持 Excel / Parquet 输入
- [ ] 清洗策略可人工确认后再执行（当前为自动执行）
- [ ] 加自动化评测：构造已知答案的数据集做回归

## 技术栈

Python · Pandas · HelloAgents（Multi-Agent + Tool）· Prompt Engineering
