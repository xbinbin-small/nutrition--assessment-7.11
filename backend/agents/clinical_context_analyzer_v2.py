from .base_agent import BaseAgent
from typing import Dict, Any, Optional

class ClinicalContextAnalyzerV2(BaseAgent):
    """
    临床背景分析智能体 - 增强版
    
    继承BaseAgent，实现统一接口规范
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        system_message = """
        你是一名临床背景分析师。你的任务是解读患者的医疗状况及其对营养的影响。
        请用中文分析主要诊断、合并症、严重程度和当前治疗。
        识别与疾病相关的潜在营养影响，如高代谢、炎症、吸收不良或器官功能障碍。
        
        分析要点：
        1. 主要诊断和合并症的营养影响
        2. 疾病的急慢性状态
        3. 当前治疗对营养状态的影响
        4. 炎症水平评估（基于CRP等指标）
        5. 器官功能状态（肝、肾、心等）
        6. 营养风险筛查评分的解读
        
        输出要求：
        - 使用结构化的中文描述
        - 明确指出营养相关的风险因素
        - 提供炎症水平的评估
        - 识别GLIM标准中的病因因素
        """
        
        super().__init__(
            agent_name="Clinical_Context_Analyzer_V2",
            llm_config=llm_config,
            system_message=system_message
        )
    
    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理临床背景分析
        
        Args:
            input_data: 患者数据
            context: 可选的上下文信息
            
        Returns:
            临床背景分析结果
        """
        # 验证输入
        is_valid, error_msg = self.validate_input(input_data)
        if not is_valid:
            return self._create_result(None, False, error_msg)
        
        try:
            # 提取相关数据
            diagnoses = input_data.get("diagnoses", [])
            symptoms = input_data.get("symptoms_and_history", {})
            consultation = input_data.get("consultation_record", {})
            lab_results = input_data.get("lab_results", {})
            
            # 构建分析提示
            prompt = self._build_analysis_prompt(diagnoses, symptoms, consultation, lab_results)
            
            # 生成分析结果
            analysis_result = self._safe_generate_reply(prompt)
            
            # 构建结构化结果
            structured_result = {
                "clinical_summary": analysis_result,
                "diagnoses_count": len(diagnoses),
                "has_inflammation_markers": self._check_inflammation_markers(lab_results),
                "nrs2002_score": consultation.get("NRS2002_score"),
                "risk_factors": self._extract_risk_factors(diagnoses, symptoms)
            }
            
            return self._create_result(structured_result, True)
            
        except Exception as e:
            self.logger.error(f"临床背景分析失败: {str(e)}")
            return self._create_result(None, False, f"分析过程中发生错误: {str(e)}")
    
    def _build_analysis_prompt(self, diagnoses: list, symptoms: dict, consultation: dict, lab_results: dict) -> str:
        """构建分析提示"""
        prompt = f"""
        请分析以下患者的临床背景及其对营养状态的影响：

        ## 诊断信息：
        {self._format_diagnoses(diagnoses)}

        ## 症状和病史：
        主诉：{symptoms.get('chief_complaint', '未提供')}
        现病史摘要：{symptoms.get('history_of_present_illness_summary', '未提供')}

        ## 会诊记录：
        {self._format_consultation(consultation)}

        ## 实验室指标（炎症相关）：
        {self._format_lab_results(lab_results)}

        请提供：
        1. 临床背景对营养状态的影响分析
        2. 疾病相关的代谢状态评估（高代谢/正常/低代谢）
        3. 炎症水平评估（基于可用指标）
        4. 器官功能对营养的影响
        5. 潜在的营养不良病因因素（GLIM标准）
        6. 营养风险评估
        """
        return prompt
    
    def _format_diagnoses(self, diagnoses: list) -> str:
        """格式化诊断信息"""
        if not diagnoses:
            return "无诊断信息"
        
        formatted = []
        for i, diagnosis in enumerate(diagnoses, 1):
            if isinstance(diagnosis, dict):
                diagnosis_type = diagnosis.get("type", "诊断")
                description = diagnosis.get("description", "未描述")
                formatted.append(f"{i}. [{diagnosis_type}] {description}")
            else:
                formatted.append(f"{i}. {diagnosis}")
        
        return "\n".join(formatted)
    
    def _format_consultation(self, consultation: dict) -> str:
        """格式化会诊记录"""
        if not consultation:
            return "无会诊记录"
        
        parts = []
        if "department" in consultation:
            parts.append(f"会诊科室：{consultation['department']}")
        if "purpose" in consultation:
            parts.append(f"会诊目的：{consultation['purpose']}")
        if "findings_and_conclusion" in consultation:
            parts.append(f"发现和结论：{consultation['findings_and_conclusion']}")
        if "NRS2002_score" in consultation:
            parts.append(f"NRS2002评分：{consultation['NRS2002_score']}分")
        
        return "\n".join(parts) if parts else "无详细会诊信息"
    
    def _format_lab_results(self, lab_results: dict) -> str:
        """格式化实验室结果（重点关注炎症指标）"""
        if not lab_results:
            return "无实验室结果"
        
        inflammation_markers = []
        
        # 检查生化指标中的炎症标志物
        biochemistry = lab_results.get("biochemistry", [])
        for item in biochemistry:
            if isinstance(item, dict):
                name = item.get("name", "")
                if "C-反应蛋白" in name or "CRP" in name.upper():
                    value = item.get("value", "未知")
                    unit = item.get("unit", "")
                    interpretation = item.get("interpretation", "")
                    inflammation_markers.append(f"C-反应蛋白：{value} {unit} {interpretation}")
                elif "白蛋白" in name:
                    value = item.get("value", "未知")
                    unit = item.get("unit", "")
                    interpretation = item.get("interpretation", "")
                    inflammation_markers.append(f"白蛋白：{value} {unit} {interpretation}")
        
        # 检查血常规中的炎症指标
        cbc = lab_results.get("complete_blood_count", [])
        for item in cbc:
            if isinstance(item, dict):
                name = item.get("name", "")
                if "白细胞" in name:
                    value = item.get("value", "未知")
                    unit = item.get("unit", "")
                    interpretation = item.get("interpretation", "")
                    inflammation_markers.append(f"白细胞计数：{value} {unit} {interpretation}")
        
        return "\n".join(inflammation_markers) if inflammation_markers else "无明显炎症标志物数据"
    
    def _check_inflammation_markers(self, lab_results: dict) -> bool:
        """检查是否有炎症标志物数据"""
        if not lab_results:
            return False
        
        biochemistry = lab_results.get("biochemistry", [])
        for item in biochemistry:
            if isinstance(item, dict):
                name = item.get("name", "")
                if "C-反应蛋白" in name or "CRP" in name.upper():
                    return True
        
        return False
    
    def _extract_risk_factors(self, diagnoses: list, symptoms: dict) -> list:
        """提取营养风险因素"""
        risk_factors = []
        
        # 基于诊断提取风险因素
        for diagnosis in diagnoses:
            if isinstance(diagnosis, dict):
                description = diagnosis.get("description", "").lower()
            else:
                description = str(diagnosis).lower()
            
            if any(keyword in description for keyword in ["心肌梗死", "心梗", "冠心病"]):
                risk_factors.append("心血管疾病")
            if any(keyword in description for keyword in ["感染", "炎症", "肺炎"]):
                risk_factors.append("感染/炎症状态")
            if any(keyword in description for keyword in ["糖尿病"]):
                risk_factors.append("糖尿病")
            if any(keyword in description for keyword in ["肾", "肾功能"]):
                risk_factors.append("肾功能异常")
            if any(keyword in description for keyword in ["肝", "肝功能"]):
                risk_factors.append("肝功能异常")
        
        return list(set(risk_factors))  # 去重
    
    # 保持向后兼容的旧接口
    def analyze(self, patient_data: Dict[str, Any]) -> str:
        """
        向后兼容的分析方法
        
        Args:
            patient_data: 患者数据
            
        Returns:
            分析结果文本
        """
        result = self.process(patient_data)
        if result["success"]:
            return result["data"]["clinical_summary"]
        else:
            return result.get("error", "分析失败")