#!/usr/bin/env python3
"""
测试图像识别功能
"""

import json
import base64
import sys
sys.path.append('.')

from agents.image_recognizer import ImageRecognizer
from config import llm_config_flash

def test_image_recognition():
    """测试图像识别功能"""
    print("=== 测试图像识别功能 ===\n")
    
    # 创建图像识别智能体
    recognizer = ImageRecognizer(llm_config=llm_config_flash)
    
    # 测试数据 - 可以替换为实际的图像路径
    test_images = [
        # 在此添加测试图像路径
        # "/path/to/medical_image1.jpg",
        # "/path/to/medical_image2.jpg"
    ]
    
    if not test_images:
        print("警告：没有配置测试图像路径")
        print("请编辑此文件并添加实际的医疗文书图像路径进行测试")
        
        # 使用模拟数据进行演示
        print("\n使用模拟数据进行演示...")
        mock_result = {
            "total_images": 2,
            "successful_extractions": 2,
            "documents": [
                {
                    "image_index": 1,
                    "document_type": "生化检查",
                    "data": {
                        "白蛋白": "34.3 g/L ↓",
                        "C-反应蛋白": "292.8 mg/L ↑",
                        "肌酐": "129.2 umol/L"
                    }
                },
                {
                    "image_index": 2,
                    "document_type": "营养评估",
                    "data": {
                        "NRS2002评分": 4,
                        "营养风险": "存在营养风险",
                        "建议": "需要营养干预"
                    }
                }
            ],
            "document_summary": {
                "生化检查": 1,
                "营养评估": 1
            },
            "integrated_data": {
                "lab_results": {
                    "biochemistry": [
                        {"name": "白蛋白", "value": "34.3", "unit": "g/L"},
                        {"name": "C-反应蛋白", "value": "292.8", "unit": "mg/L"},
                        {"name": "肌酐", "value": "129.2", "unit": "umol/L"}
                    ]
                },
                "NRS2002_score": 4
            }
        }
        
        print("\n模拟识别结果:")
        print(json.dumps(mock_result, ensure_ascii=False, indent=2))
        return
    
    # 执行图像识别
    input_data = {
        "file_paths": test_images
    }
    
    print(f"正在识别 {len(test_images)} 个图像...")
    result = recognizer.process(input_data)
    
    # 显示结果
    if result.get("success"):
        print("\n识别成功！")
        print("\n识别结果:")
        print(json.dumps(result.get("data"), ensure_ascii=False, indent=2))
    else:
        print("\n识别失败！")
        print(f"错误信息: {result.get('error')}")

def test_integration_with_coordinator():
    """测试与CNA协调器的集成"""
    print("\n\n=== 测试与CNA协调器的集成 ===\n")
    
    from agents.cna_coordinator import CNA_Coordinator
    from config import llm_config_pro
    
    # 基础患者数据
    patient_data = {
        "patient_info": {
            "age": 65,
            "gender": "男"
        },
        "diagnoses": [
            {"type": "入院诊断", "description": "冠状动脉粥样硬化性心脏病"}
        ]
    }
    
    # 图像数据（使用模拟路径）
    image_data = {
        "file_paths": [
            # 在此添加实际图像路径
        ]
    }
    
    if not image_data["file_paths"]:
        print("跳过集成测试（没有配置图像路径）")
        return
    
    print("创建CNA协调器...")
    coordinator = CNA_Coordinator(
        patient_data, 
        llm_config_pro, 
        llm_config_flash,
        image_data=image_data
    )
    
    print("运行评估...")
    result = coordinator.run_assessment()
    
    # 显示结果
    if "error" not in result:
        print("\n评估成功！")
        print("\n最终报告:")
        print(result.get("report", ""))
        
        if "image_recognition_results" in result:
            print("\n\n图像识别结果摘要:")
            img_results = result["image_recognition_results"]
            print(f"- 总图像数: {img_results.get('total_images', 0)}")
            print(f"- 成功识别: {img_results.get('successful_extractions', 0)}")
            if "document_summary" in img_results:
                print(f"- 文档类型: {img_results['document_summary']}")
    else:
        print("\n评估失败！")
        print(f"错误信息: {result.get('error')}")

if __name__ == "__main__":
    # 运行测试
    test_image_recognition()
    test_integration_with_coordinator()
    
    print("\n\n测试完成！")
    print("\n注意事项:")
    print("1. 请编辑此文件并添加实际的医疗文书图像路径进行真实测试")
    print("2. 确保已安装所有依赖: pip install -r requirements.txt")
    print("3. 确保已配置GEMINI_API_KEY环境变量")