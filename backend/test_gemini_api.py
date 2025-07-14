#!/usr/bin/env python3
"""
测试Gemini API连接
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# 加载环境变量
load_dotenv(dotenv_path='../.env')

def test_gemini_connection():
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"API Key loaded: {api_key[:10]}... (length: {len(api_key) if api_key else 0})")
    
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        return
    
    try:
        # 配置API
        genai.configure(api_key=api_key)
        
        # 创建模型
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 简单测试
        response = model.generate_content("Say 'API connection successful' and nothing else.")
        print(f"API Response: {response.text}")
        print("✅ Gemini API connection successful!")
        
    except Exception as e:
        print(f"❌ API Error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    test_gemini_connection()