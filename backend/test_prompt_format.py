#!/usr/bin/env python3
"""
简单测试：直接调用ImageRecognizer
"""

import sys
import json
from agents.image_recognizer import ImageRecognizer
from config import llm_config_flash

# 创建一个测试"图像"路径
test_path = "/test/image.jpg"

# 创建识别器
recognizer = ImageRecognizer(llm_config=llm_config_flash)

# 测试_process_single_image方法中的prompt格式
try:
    index = 0
    prompt = f"""
    请分析这张医疗文书图片（图片 {index + 1}），提取其中的关键数据、评分或结论。
    
    示例输出格式：
    对于生化检查：
    {{
      "检查日期": "2024-01-15",
      "白蛋白": "34.3 g/L ↓"
    }}
    """
    print("✅ Prompt formatting successful!")
    print("Prompt preview:")
    print(prompt[:200] + "...")
    
except Exception as e:
    print(f"❌ Prompt formatting failed: {type(e).__name__}: {str(e)}")

print("\nTest completed.")