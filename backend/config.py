import os
from dotenv import load_dotenv

# 先加载 .env，然后加载 .env.local （优先级更高）
load_dotenv(dotenv_path='../.env')
load_dotenv(dotenv_path='../.env.local', override=True)

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# ==================== 模型配置 ====================
# 本项目支持两大模型系列：Gemini和DeepSeek
# 用户可在前端选择使用哪个系列的模型进行分析和报告生成

# ========== Gemini系列模型 ==========

# LLM Configuration for Gemini Flash Standard (中间分析任务)
# 用途：Clinical_Context_Analyzer, Anthropometric_Evaluator, Biochemical_Interpreter,
#       Dietary_Assessor, ImageRecognizer, 文本处理服务
llm_config_gemini_flash_standard = {
    "config_list": [
        {
            "model": "gemini-2.5-flash",
            "api_key": GEMINI_API_KEY,
            "api_type": "google",
        }
    ],
    "temperature": 0.5,  # 较低温度，保证分析准确性
}

# LLM Configuration for Gemini Flash Preview (协调管理与报告生成)
# 用途：CNA_Coordinator (协调管理), Diagnostic_Reporter (默认报告生成)
llm_config_gemini_flash_preview = {
    "config_list": [
        {
            "model": "gemini-2.5-flash-preview-09-2025",
            "api_key": GEMINI_API_KEY,
            "api_type": "google",
        }
    ],
    "temperature": 0.7,  # 较高温度，生成更自然的报告
}

# ========== DeepSeek系列模型 ==========

# LLM Configuration for DeepSeek Chat (中间分析任务)
# 用途：Clinical_Context_Analyzer, Anthropometric_Evaluator, Biochemical_Interpreter,
#       Dietary_Assessor, 文本处理服务（用户选择DeepSeek时）
llm_config_deepseek_chat = {
    "config_list": [
        {
            "model": "deepseek-chat",
            "api_key": DEEPSEEK_API_KEY,
            "api_type": "openai",
            "base_url": "https://api.deepseek.com/v1",
        }
    ],
    "temperature": 0.5,  # 与Gemini Flash相同温度，保证分析准确性
}

# LLM Configuration for DeepSeek Reasoner (最终报告生成)
# 用途：Diagnostic_Reporter (用户选择DeepSeek时)
# 优势：提供更强的推理能力和高质量的临床分析
llm_config_deepseek_reasoner = {
    "config_list": [
        {
            "model": "deepseek-reasoner",
            "api_key": DEEPSEEK_API_KEY,
            "api_type": "openai",
            "base_url": "https://api.deepseek.com/v1",
        }
    ],
    "temperature": 0.7,  # 较高温度，生成更自然的报告
}

# ==================== 向后兼容的别名 ====================
# 为了保持代码兼容性，保留旧的命名作为别名
llm_config_flash_standard = llm_config_gemini_flash_standard
llm_config_flash_preview = llm_config_gemini_flash_preview
llm_config_flash = llm_config_gemini_flash_standard  # 最旧的别名
llm_config_pro = llm_config_gemini_flash_preview     # 最旧的别名
llm_config_deepseek = llm_config_deepseek_reasoner   # 旧的DeepSeek配置，指向reasoner