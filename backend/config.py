import os
from dotenv import load_dotenv

# 先加载 .env，然后加载 .env.local （优先级更高）
load_dotenv(dotenv_path='../.env')
load_dotenv(dotenv_path='../.env.local', override=True)

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# LLM Configuration for the Pro model (for final reporting)
# 符合CLAUDE.md新规范：gemini-2.5-pro用于Diagnostic_Reporter的最终报告生成
llm_config_pro = {
    "config_list": [
        {
            "model": "gemini-2.5-pro",
            "api_key": GEMINI_API_KEY,
            "api_type": "google",  # 修复autogen配置
        }
    ],
    "temperature": 0.7,
}

# LLM Configuration for the Flash model (for intermediate analysis)
# 符合CLAUDE.md新规范：gemini-2.5-flash用于Clinical_Context_Analyzer等中间分析步骤  
llm_config_flash = {
    "config_list": [
        {
            "model": "gemini-2.5-flash",
            "api_key": GEMINI_API_KEY,
            "api_type": "google",  # 修复autogen配置
        }
    ],
    "temperature": 0.5,
}