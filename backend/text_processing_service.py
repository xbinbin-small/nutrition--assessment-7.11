#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文本处理服务
用于处理医疗文档文本，提取结构化数据
支持Gemini和DeepSeek两种模型系列
"""

import json
import sys
import logging
import traceback
from datetime import datetime
import re
import google.generativeai as genai
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path='../.env')
load_dotenv(dotenv_path='../.env.local', override=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

def setup_gemini():
    """配置Gemini API"""
    try:
        if not GEMINI_API_KEY:
            logger.error("Gemini API密钥未配置")
            raise ValueError("Gemini API密钥未配置")

        genai.configure(api_key=GEMINI_API_KEY)
        logger.info(f"使用Gemini API处理文本，API密钥前缀: {GEMINI_API_KEY[:10]}...")
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        logger.error(f"配置Gemini API失败: {e}")
        raise

def setup_deepseek():
    """配置DeepSeek API"""
    try:
        if not DEEPSEEK_API_KEY:
            logger.error("DeepSeek API密钥未配置")
            raise ValueError("DeepSeek API密钥未配置")

        logger.info(f"使用DeepSeek API处理文本，API密钥前缀: {DEEPSEEK_API_KEY[:10]}...")
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    except Exception as e:
        logger.error(f"配置DeepSeek API失败: {e}")
        raise

def extract_medical_data_from_text_gemini(text, model):
    """使用Gemini从医疗文本中提取结构化数据"""

    prompt = f"""
你是一位经验丰富的医疗信息分析专家。请从以下医疗文本中提取结构化信息，并按照指定的JSON格式返回。

医疗文本内容：
{text}

请提取以下信息并返回标准JSON格式：

{{
  "document_type": "文档类型（病历/检查报告/会诊记录/营养评估等）",
  "patient_info": {{
    "name": "患者姓名",
    "age": "年龄",
    "gender": "性别",
    "height_cm": 身高（厘米，数值），
    "weight_kg": 体重（公斤，数值），
    "bmi": BMI值（数值）
  }},
  "diagnoses": [
    {{
      "type": "诊断类型",
      "description": "诊断描述"
    }}
  ],
  "symptoms_and_history": {{
    "chief_complaint": "主诉",
    "history_of_present_illness_summary": "现病史摘要"
  }},
  "lab_results": {{
    "biochemistry": [
      {{
        "name": "检查项目名称",
        "value": "检查数值",
        "unit": "单位",
        "interpretation": "异常标识（↑/↓/正常）"
      }}
    ],
    "complete_blood_count": [
      {{
        "name": "检查项目名称",
        "value": "检查数值",
        "unit": "单位",
        "interpretation": "异常标识（↑/↓/正常）"
      }}
    ],
    "stool_routine": []
  }},
  "treatment_plan": {{
    "summary": "治疗方案摘要",
    "key_medications": ["主要药物列表"]
  }},
  "consultation_record": {{
    "department": "会诊科室",
    "purpose": "会诊目的",
    "findings_and_conclusion": "会诊发现和结论",
    "recommendations": "建议",
    "NRS2002_score": NRS2002评分（数值），
    "PES_statement_summary": "PES陈述摘要"
  }}
}}

注意事项：
1. 如果某些信息在文本中不存在，请设为null或空数组
2. 数值类型的字段请提取纯数字，不要包含单位
3. 对于检查结果，请识别异常标识（如↑表示偏高，↓表示偏低）
4. 返回标准JSON格式，不要包含其他文字
5. 确保JSON格式正确，可以被解析
"""

    try:
        logger.info("调用Gemini API分析文本...")
        response = model.generate_content(prompt)

        if response.text:
            logger.info(f"收到响应，长度: {len(response.text)}")
            return parse_json_response(response.text)
        else:
            logger.error("Gemini API返回空响应")
            return create_basic_structure()

    except Exception as e:
        logger.error(f"调用Gemini API失败: {e}")
        logger.error(traceback.format_exc())
        return create_basic_structure()

def extract_medical_data_from_text_deepseek(text, client):
    """使用DeepSeek从医疗文本中提取结构化数据"""

    prompt = f"""
你是一位经验丰富的医疗信息分析专家。请从以下医疗文本中提取结构化信息，并按照指定的JSON格式返回。

医疗文本内容：
{text}

请提取以下信息并返回标准JSON格式：

{{
  "document_type": "文档类型（病历/检查报告/会诊记录/营养评估等）",
  "patient_info": {{
    "name": "患者姓名",
    "age": "年龄",
    "gender": "性别",
    "height_cm": 身高（厘米，数值），
    "weight_kg": 体重（公斤，数值），
    "bmi": BMI值（数值）
  }},
  "diagnoses": [
    {{
      "type": "诊断类型",
      "description": "诊断描述"
    }}
  ],
  "symptoms_and_history": {{
    "chief_complaint": "主诉",
    "history_of_present_illness_summary": "现病史摘要"
  }},
  "lab_results": {{
    "biochemistry": [
      {{
        "name": "检查项目名称",
        "value": "检查数值",
        "unit": "单位",
        "interpretation": "异常标识（↑/↓/正常）"
      }}
    ],
    "complete_blood_count": [
      {{
        "name": "检查项目名称",
        "value": "检查数值",
        "unit": "单位",
        "interpretation": "异常标识（↑/↓/正常）"
      }}
    ],
    "stool_routine": []
  }},
  "treatment_plan": {{
    "summary": "治疗方案摘要",
    "key_medications": ["主要药物列表"]
  }},
  "consultation_record": {{
    "department": "会诊科室",
    "purpose": "会诊目的",
    "findings_and_conclusion": "会诊发现和结论",
    "recommendations": "建议",
    "NRS2002_score": NRS2002评分（数值），
    "PES_statement_summary": "PES陈述摘要"
  }}
}}

注意事项：
1. 如果某些信息在文本中不存在，请设为null或空数组
2. 数值类型的字段请提取纯数字，不要包含单位
3. 对于检查结果，请识别异常标识（如↑表示偏高，↓表示偏低）
4. 返回标准JSON格式，不要包含其他文字
5. 确保JSON格式正确，可以被解析
"""

    try:
        logger.info("调用DeepSeek API分析文本...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content
            logger.info(f"收到响应，长度: {len(content)}")
            return parse_json_response(content)
        else:
            logger.error("DeepSeek API返回空响应")
            return create_basic_structure()

    except Exception as e:
        logger.error(f"调用DeepSeek API失败: {e}")
        logger.error(traceback.format_exc())
        return create_basic_structure()

def parse_json_response(text):
    """解析JSON响应"""
    # 清理响应文本，去除markdown格式
    cleaned_text = text.strip()
    if cleaned_text.startswith('```json'):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.endswith('```'):
        cleaned_text = cleaned_text[:-3]
    cleaned_text = cleaned_text.strip()

    # 解析JSON
    try:
        extracted_data = json.loads(cleaned_text)
        logger.info("成功提取JSON数据")
        return extracted_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        logger.error(f"原始响应: {text}")
        # 返回基础结构
        return create_basic_structure()

def create_basic_structure():
    """创建基本的数据结构"""
    return {
        "document_type": "文本文档",
        "patient_info": {
            "name": None,
            "age": None,
            "gender": None,
            "height_cm": None,
            "weight_kg": None,
            "bmi": None
        },
        "diagnoses": [],
        "symptoms_and_history": {
            "chief_complaint": None,
            "history_of_present_illness_summary": None
        },
        "lab_results": {
            "biochemistry": [],
            "complete_blood_count": [],
            "stool_routine": []
        },
        "treatment_plan": {
            "summary": None,
            "key_medications": []
        },
        "consultation_record": {
            "department": None,
            "purpose": None,
            "findings_and_conclusion": None,
            "recommendations": None,
            "NRS2002_score": None,
            "PES_statement_summary": None
        }
    }

def main():
    """主函数"""
    try:
        logger.info("开始文本处理")

        # 从stdin读取输入
        input_data = sys.stdin.read()
        logger.info(f"收到输入数据，长度: {len(input_data)}")

        # 解析JSON输入
        try:
            data = json.loads(input_data)
            text = data.get('text', '')
            model_series = data.get('model_series', 'gemini')  # 默认使用Gemini
        except json.JSONDecodeError as e:
            logger.error(f"输入JSON解析失败: {e}")
            result = {
                "success": False,
                "error": "输入数据格式错误",
                "extracted_data": create_basic_structure()
            }
            print(json.dumps(result, ensure_ascii=False))
            return

        if not text:
            logger.error("未提供文本内容")
            result = {
                "success": False,
                "error": "未提供文本内容",
                "extracted_data": create_basic_structure()
            }
            print(json.dumps(result, ensure_ascii=False))
            return

        # 根据选择的模型系列进行处理
        if model_series == 'deepseek':
            logger.info("使用DeepSeek模型系列")
            client = setup_deepseek()
            extracted_data = extract_medical_data_from_text_deepseek(text, client)
        else:
            logger.info("使用Gemini模型系列")
            model = setup_gemini()
            extracted_data = extract_medical_data_from_text_gemini(text, model)

        # 返回结果
        result = {
            "success": True,
            "extracted_data": extracted_data,
            "model_used": model_series,
            "processing_time": datetime.now().isoformat()
        }

        logger.info("文本处理完成")
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        logger.error(f"文本处理失败: {e}")
        logger.error(traceback.format_exc())

        result = {
            "success": False,
            "error": str(e),
            "extracted_data": create_basic_structure()
        }
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()