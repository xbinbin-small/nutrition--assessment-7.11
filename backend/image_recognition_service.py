#!/usr/bin/env python3
"""
图像识别服务
接收图像文件路径，使用ImageRecognizer智能体识别医疗文书内容
"""

import sys
import json
import logging
from agents.image_recognizer import ImageRecognizer
from config import llm_config_flash

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        # 从stdin读取输入数据
        input_data = sys.stdin.read()
        
        if not input_data:
            result = {"error": "No input data provided"}
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(1)
        
        # 解析输入数据
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            result = {"error": f"Invalid JSON input: {str(e)}"}
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(1)
        
        # 创建图像识别智能体
        try:
            image_recognizer = ImageRecognizer(llm_config=llm_config_flash)
        except Exception as e:
            result = {"error": f"Failed to initialize ImageRecognizer: {str(e)}"}
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(1)
        
        # 处理图像
        try:
            recognition_result = image_recognizer.process(data)
        except Exception as e:
            result = {"error": f"Image recognition failed: {str(e)}"}
            print(json.dumps(result, ensure_ascii=False))
            sys.exit(1)
        
        # 提取识别结果
        if recognition_result.get("success", False):
            output = recognition_result.get("data", {})
        else:
            output = {
                "error": recognition_result.get("error", "图像识别失败"),
                "details": recognition_result
            }
        
        # 输出结果
        print(json.dumps(output, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            "error": f"Service error: {str(e)}",
            "type": type(e).__name__
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()