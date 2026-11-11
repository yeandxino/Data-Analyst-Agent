import os
import pandas as pd
from typing import List, Any, Dict
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import Tool, ToolParameter
from dotenv import load_dotenv

load_dotenv()


# ==================== 定义工具 ====================
class ReadCSVTool(Tool):
    def __init__(self):
        super().__init__(
            name="read_csv",
            description="读取CSV文件，返回前5行数据以及总体统计信息。"
        )

    def run(self, parameters: Dict[str, Any]) -> str:
        # 兼容多种参数名
        file_path = parameters.get("file_path") or parameters.get("path") or parameters.get("filename") or ""
        file_path = file_path.strip().strip('"').strip("'")

        if not file_path:
            return "错误：未提供文件路径。请使用 file_path 参数。"

        # 🎉 终极兜底：不管大模型传什么，都把它按在当前 main.py 所在的目录下！
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(file_path):
            # 如果是相对路径，拼成绝对路径
            full_path = os.path.join(base_dir, file_path)
        else:
            # 如果是绝对路径，先检查原路径，不存在再尝试按文件名拼到当前目录
            full_path = file_path
            if not os.path.exists(full_path):
                full_path = os.path.join(base_dir, os.path.basename(file_path))

        if not os.path.exists(full_path):
            return f"错误：文件 '{file_path}' 不存在。请确认文件与 main.py 在同一目录下。当前寻找的绝对路径是：{full_path}"

        try:
            # 🎉 终极暴力破解：直接读取字节，跳过所有编码报错
            import io
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                csv_text = f.read()

            # 用 StringIO 把文本变成类似文件的对象，直接丢给 pandas
            df = pd.read_csv(io.StringIO(csv_text))

            # 数据读取成功，继续原有逻辑
            head_str = df.head(5).to_string()
            describe_str = df.describe(include='all').to_string()

            result = f"文件 '{file_path}' 读取成功。\n\n【前5行数据】\n{head_str}\n\n【数据统计】\n{describe_str}"
            return result
        except Exception as e:
            return f"读取CSV失败：{str(e)}"

    def get_parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="file_path",
                type="string",
                description="要读取的CSV文件路径，例如 'data.csv'",
                required=True
            )
        ]


# ==================== 创建 Agent ====================
# 从 .env / 环境变量读取，不在代码里写死 Key
API_KEY = os.getenv("MODELSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api-inference.modelscope.cn/v1")
MODEL_NAME = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V4.1-Flash")

if not API_KEY:
    raise SystemExit(
        "未找到 API Key。请复制 .env.example 为 .env，并填入：\n"
        "  MODELSCOPE_API_KEY=your_key_here\n"
        "（或在系统环境变量里设置同名变量）"
    )

llm = HelloAgentsLLM(
    model=MODEL_NAME,
    api_key=API_KEY,
    base_url=BASE_URL
)

agent = SimpleAgent(
    name="数据分析师",
    llm=llm,
    system_prompt="你是一个专业的数据分析师。当用户要求分析数据时，必须调用 read_csv 工具读取文件，并根据读取到的数据给出分析和建议。"
)
agent.add_tool(ReadCSVTool())

# ==================== 多 Agent 智囊团 ====================
# 1. 创建三个拥有不同角色的 Agent
explorer_agent = SimpleAgent(
    name="数据探索官",
    llm=llm,
    system_prompt="你是一个数据探索专家。请调用 read_csv 工具读取用户指定的文件，并汇报数据的基本情况、字段类型以及存在的缺失值。只输出事实，不要给建议。"
)
explorer_agent.add_tool(ReadCSVTool())  # 探索官需要读文件的工具

cleaner_agent = SimpleAgent(
    name="数据清洗员",
    llm=llm,
    system_prompt="你是一个数据清洗专家。请根据用户提供的数据情况汇报，给出清理缺失值、异常值的具体策略（比如：用什么值填补，为什么）。不要写代码，只写策略和业务建议。"
)

chief_agent = SimpleAgent(
    name="首席分析师",
    llm=llm,
    system_prompt="你是一个首席数据分析师。请综合数据和清洗策略，写出一份结构清晰、专业的数据分析报告。包含数据概览、问题诊断、清洗建议和最终结论。"
)

# ==================== 多 Agent 协作主循环 ====================
if __name__ == "__main__":
    print("\n=== 数据分析智囊团已启动（输入 '退出' 结束）===\n")
    while True:
        user_input = input("👤 你：")
        if user_input.strip() == '退出':
            break
        if not user_input.strip():
            continue

        print("🔍 第一步：数据探索官正在读取数据...")
        raw_data = explorer_agent.run(user_input)

        print("🧹 第二步：数据清洗员正在制定清洗策略...")
        strategy = cleaner_agent.run(f"请根据以下数据情况，制定清洗策略：\n{raw_data}")

        print("📊 第三步：首席分析师正在撰写报告...")
        final_report = chief_agent.run(
            f"请基于以下数据情况和清洗策略，撰写最终报告：\n数据情况：{raw_data}\n清洗策略：{strategy}")

        print(f"\n🤖 最终分析报告：\n{final_report}\n")
