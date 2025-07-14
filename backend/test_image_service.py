#!/usr/bin/env python3
"""
测试图像识别服务
"""

import json
import subprocess
import sys
import os

def test_image_service():
    # 准备测试数据
    test_data = {
        "file_paths": ["/path/to/test/image.jpg"]  # 这里使用一个测试路径
    }
    
    # 运行图像识别服务
    process = subprocess.Popen(
        [sys.executable, 'image_recognition_service.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送测试数据
    stdout, stderr = process.communicate(input=json.dumps(test_data))
    
    print("=== STDOUT ===")
    print(stdout)
    print("\n=== STDERR ===")
    print(stderr)
    print("\n=== Return Code ===")
    print(process.returncode)
    
    # 尝试解析结果
    try:
        result = json.loads(stdout)
        print("\n=== Parsed Result ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"\nFailed to parse result: {e}")

if __name__ == "__main__":
    # 切换到backend目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    test_image_service()