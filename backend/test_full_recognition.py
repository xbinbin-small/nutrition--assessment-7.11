#!/usr/bin/env python3
"""
测试图像识别服务的完整流程
"""

import json
import subprocess
import sys
import os
import tempfile
import shutil

def test_with_real_image():
    # 创建一个简单的测试图像
    from PIL import Image, ImageDraw
    
    # 创建测试图像
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "生化检查\n白蛋白: 34.3 g/L", fill='black')
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        img.save(tmp.name)
        temp_image_path = tmp.name
    
    print(f"Created test image: {temp_image_path}")
    
    # 准备数据
    test_data = {
        "file_paths": [temp_image_path]
    }
    
    # 运行图像识别服务
    process = subprocess.Popen(
        [sys.executable, 'image_recognition_service.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送数据
    stdout, stderr = process.communicate(input=json.dumps(test_data))
    
    print("\n=== STDOUT ===")
    print(stdout)
    print("\n=== STDERR ===")
    print(stderr)
    print(f"\n=== Return Code ===")
    print(process.returncode)
    
    # 清理临时文件
    try:
        os.unlink(temp_image_path)
        print(f"\nCleaned up: {temp_image_path}")
    except:
        pass
    
    # 分析输出
    try:
        result = json.loads(stdout)
        print("\n=== Parsed Result ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 检查结果结构
        if "error" in result:
            print(f"\n❌ Error found: {result['error']}")
            if "details" in result:
                print(f"Details: {result['details']}")
        elif "documents" in result:
            print(f"\n✅ Success! Found {len(result['documents'])} documents")
        else:
            print("\n⚠️ Unexpected result structure")
            
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to parse JSON: {e}")

if __name__ == "__main__":
    test_with_real_image()