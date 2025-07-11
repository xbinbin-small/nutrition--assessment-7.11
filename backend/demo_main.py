#!/usr/bin/env python3
"""
CNA系统演示版本 - 不需要真实API密钥
"""

import sys
import json
from datetime import datetime

def mock_assessment(patient_data):
    """模拟营养评估结果"""
    
    # 提取患者基本信息
    patient_info = patient_data.get("patient_info", {})
    height = patient_info.get("height_cm", 0)
    weight = patient_info.get("weight_kg", 0)
    bmi = patient_info.get("bmi", 0)
    
    # 提取诊断信息
    diagnoses = patient_data.get("diagnoses", [])
    diagnosis_list = [d.get("description", "") for d in diagnoses]
    
    # 提取实验室结果
    lab_results = patient_data.get("lab_results", {})
    biochemistry = lab_results.get("biochemistry", [])
    
    # 寻找关键指标
    albumin = None
    crp = None
    hemoglobin = None
    
    for item in biochemistry:
        name = item.get("name", "")
        if "白蛋白" in name:
            albumin = item.get("value", "")
        elif "C-反应蛋白" in name:
            crp = item.get("value", "")
    
    cbc = lab_results.get("complete_blood_count", [])
    for item in cbc:
        name = item.get("name", "")
        if "血红蛋白" in name:
            hemoglobin = item.get("value", "")
    
    # 提取会诊信息
    consultation = patient_data.get("consultation_record", {})
    nrs_score = consultation.get("NRS2002_score", 0)
    
    # 生成模拟报告
    mock_report = f"""
# 智能综合营养评估报告

## 1. 患者基本情况摘要
患者，身高{height}cm，体重{weight}kg，BMI {bmi}。主要诊断包括：
{chr(10).join([f"• {d}" for d in diagnosis_list[:3]])}

## 2. 营养风险等级
NRS2002评分：{nrs_score}分
评估结果：{'存在营养风险' if nrs_score >= 3 else '营养风险较低'}

## 3. 关键评估发现

### 生化评估
• 血清白蛋白：{albumin} g/L {'(偏低)' if albumin and float(albumin) < 35 else ''}
• C-反应蛋白：{crp} mg/L {'(明显升高，提示炎症状态)' if crp and float(crp) > 10 else ''}

### 血液学评估  
• 血红蛋白：{hemoglobin} g/L {'(偏低，提示贫血)' if hemoglobin and float(hemoglobin) < 110 else ''}

### 人体测量评估
• BMI评估：{bmi} kg/m² {'(正常范围)' if 18.5 <= bmi <= 24 else '(需关注)'}

### 膳食评估
• 根据会诊记录，患者存在营养摄入不足的情况
• 推荐能量摄入：1600-1700 kcal/日
• 推荐蛋白质摄入：65-70 g/日

## 4. 营养诊断
基于GLIM标准评估：
• 表型标准：{'体重下降/BMI偏低' if bmi < 20 else 'BMI正常范围'}
• 病因标准：疾病相关炎症，摄入减少

**营养诊断**：蛋白质-能量营养不良，与心血管疾病相关的炎症状态和摄入减少有关

## 5. 主要营养问题
1. 蛋白质营养状态不佳（白蛋白偏低）
2. 存在炎症状态影响营养代谢
3. 可能存在铁缺乏性贫血
4. 能量和蛋白质摄入不足

## 6. 营养治疗目标（SMART原则）
1. 在1周内，将每日能量摄入提高到1600-1700 kcal
2. 在2周内，将蛋白质摄入量增加到65-70g/日
3. 在4周内，血清白蛋白水平提升至36 g/L以上
4. 在6周内，血红蛋白水平改善至100 g/L以上

## 7. 营养干预措施
1. **肠内营养支持**：
   - 低钠配方肠内营养粉，每日850 kcal，蛋白13.5g
   - 餐间补充能全素营养液
   
2. **饮食调整**：
   - 高蛋白、适量能量的饮食
   - 注意钠盐限制（心血管疾病）
   - 血糖控制饮食（糖尿病）
   
3. **营养监测**：
   - 每周监测体重变化
   - 每2周复查血清白蛋白
   - 每月评估营养风险评分

4. **多学科协作**：
   - 与内分泌科协调血糖管理
   - 与心内科协调心血管治疗
   - 定期营养科随访

---
报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
评估系统：CNA智能综合营养评估系统 v2.0
"""
    
    return {
        "report": mock_report.strip(),
        "session_id": "demo-session-" + datetime.now().strftime('%Y%m%d-%H%M%S'),
        "assessment_time": datetime.now().isoformat(),
        "processing_duration": 2.5,
        "validation_results": {
            "is_valid": True,
            "missing_fields": [],
            "warnings": []
        },
        "trace_summary": {
            "total_steps": 6,
            "final_report_trace_id": "demo_report_trace_001",
            "intermediate_trace_ids": [
                "demo_clinical_trace_001",
                "demo_anthro_trace_001", 
                "demo_biochem_trace_001",
                "demo_dietary_trace_001"
            ]
        },
        "demo_mode": True,
        "note": "这是演示版本，使用模拟数据生成报告。实际版本需要配置Gemini API密钥。"
    }

def main():
    """主函数"""
    try:
        # 读取输入数据
        input_data = sys.stdin.read()
        patient_data = json.loads(input_data)
        
        # 处理患者数据
        if isinstance(patient_data, list) and len(patient_data) > 0:
            patient_json = patient_data[0]
        elif isinstance(patient_data, dict):
            patient_json = patient_data
        else:
            raise ValueError("Invalid patient data format")
        
        # 生成评估结果
        result = mock_assessment(patient_json)
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "error": f"评估过程中发生错误: {str(e)}",
            "error_type": type(e).__name__,
            "demo_mode": True
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()