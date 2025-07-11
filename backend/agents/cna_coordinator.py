import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

import autogen
from .clinical_context_analyzer import ClinicalContextAnalyzer
from .anthropometric_evaluator import AnthropometricEvaluator
from .biochemical_interpreter import BiochemicalInterpreter
from .dietary_assessor import DietaryAssessor
from .diagnostic_reporter import DiagnosticReporter


class CNA_Coordinator:
    """
    中央协调器 - 负责管理整个CNA评估流程
    
    职责：
    - 接收和验证患者数据
    - 协调各专门智能体的工作
    - 管理数据流转和依赖关系
    - 收集中间结果
    - 触发最终报告生成
    - 提供数据追溯性管理
    """
    
    def __init__(self, patient_data: Dict[str, Any], llm_config_pro: Dict, llm_config_flash: Dict):
        """
        初始化CNA协调器
        
        Args:
            patient_data: 患者数据
            llm_config_pro: Pro模型配置
            llm_config_flash: Flash模型配置
        """
        self.patient_data = patient_data
        self.intermediate_results = {}
        self.data_trace = {}  # 数据追溯映射
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        
        # CNA_Coordinator使用Pro模型进行协调和管理任务
        # 符合CLAUDE.md规范：作为中央协调器，需要最强推理能力保证系统质量
        self.llm_config = llm_config_pro
        self.agent = autogen.AssistantAgent(
            name="CNA_Coordinator",
            llm_config=llm_config_pro,
            system_message="""
            你是CNA系统的中央协调器，负责整个营养评估流程的质量控制和决策管理。
            
            核心职责：
            1. 深度分析数据质量和完整性，识别关键缺失信息
            2. 运用医学知识检测智能体结果间的逻辑冲突和不一致
            3. 智能决策评估流程控制：是否需要重新分析、补充数据或终止评估
            4. 生成专业的协调决策解释和质量保证说明
            5. 确保最终报告的医学准确性和逻辑一致性
            
            专业要求：
            - 具备营养学和临床医学知识背景
            - 运用批判性思维进行深度分析
            - 提供循证医学支持的决策建议
            - 保持最高标准的质量控制
            - 用专业、清晰的中文进行分析和解释
            
            作为中央协调器，你的决策直接影响整个CNA系统的可靠性和准确性。
            """
        )
        
        # 初始化专门智能体
        self.clinical_analyzer = ClinicalContextAnalyzer(llm_config=llm_config_flash)
        self.anthropometric_evaluator = AnthropometricEvaluator(llm_config=llm_config_flash)
        self.biochemical_interpreter = BiochemicalInterpreter(llm_config=llm_config_flash)
        self.dietary_assessor = DietaryAssessor(llm_config=llm_config_flash)
        self.diagnostic_reporter = DiagnosticReporter(llm_config=llm_config_pro)
        
        # 验证数据完整性
        self.validation_results = self._validate_data()
        
    def _validate_data(self) -> Dict[str, Any]:
        """
        验证输入数据的完整性和基本格式
        
        Returns:
            验证结果，包含是否有效和缺失信息
        """
        validation = {
            "is_valid": True,
            "missing_fields": [],
            "warnings": [],
            "critical_missing": []
        }
        
        # 检查必需字段
        required_fields = ["patient_info", "diagnoses", "lab_results"]
        for field in required_fields:
            if field not in self.patient_data:
                validation["missing_fields"].append(field)
                validation["critical_missing"].append(field)
                validation["is_valid"] = False
        
        # 检查患者基本信息
        if "patient_info" in self.patient_data:
            patient_info = self.patient_data["patient_info"]
            if "height_cm" not in patient_info:
                validation["missing_fields"].append("patient_info.height_cm")
            if "weight_kg" not in patient_info:
                validation["missing_fields"].append("patient_info.weight_kg")
        
        # 检查实验室结果
        if "lab_results" in self.patient_data:
            lab_results = self.patient_data["lab_results"]
            if "biochemistry" not in lab_results:
                validation["warnings"].append("缺少生化检验结果")
            if "complete_blood_count" not in lab_results:
                validation["warnings"].append("缺少血常规结果")
        
        # 检查营养风险评分
        if "consultation_record" in self.patient_data:
            consultation = self.patient_data["consultation_record"]
            if "NRS2002_score" not in consultation:
                validation["warnings"].append("缺少NRS2002评分")
        
        return validation
    
    def _generate_trace_id(self, agent_name: str, data_type: str) -> str:
        """
        生成数据追溯ID
        
        Args:
            agent_name: 智能体名称
            data_type: 数据类型
            
        Returns:
            唯一的追溯ID
        """
        trace_id = f"{agent_name}_{data_type}_{uuid.uuid4().hex[:8]}"
        return trace_id
    
    def _add_trace_record(self, trace_id: str, agent_name: str, input_data: Any, output_data: Any, dependencies: List[str] = None):
        """
        添加数据追溯记录
        
        Args:
            trace_id: 追溯ID
            agent_name: 智能体名称
            input_data: 输入数据
            output_data: 输出数据
            dependencies: 依赖的其他追溯ID
        """
        self.data_trace[trace_id] = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "input_data": input_data,
            "output_data": output_data,
            "dependencies": dependencies or [],
            "session_id": self.session_id
        }
    
    def run_assessment(self) -> Dict[str, Any]:
        """
        运行完整的CNA评估流程
        
        Returns:
            最终的评估报告
        """
        try:
            # 检查数据验证结果
            if not self.validation_results["is_valid"]:
                return {
                    "error": "数据验证失败",
                    "validation_results": self.validation_results,
                    "session_id": self.session_id
                }
            
            # 步骤1: 临床背景分析
            clinical_trace_id = self._generate_trace_id("Clinical_Context_Analyzer", "clinical_analysis")
            clinical_summary = self.clinical_analyzer.analyze(self.patient_data)
            self._add_trace_record(
                clinical_trace_id,
                "Clinical_Context_Analyzer",
                {"diagnoses": self.patient_data.get("diagnoses", []), 
                 "symptoms": self.patient_data.get("symptoms_and_history", {}),
                 "consultation": self.patient_data.get("consultation_record", {})},
                clinical_summary
            )
            self.intermediate_results['clinical_context'] = {
                "data": clinical_summary,
                "trace_id": clinical_trace_id
            }
            
            # 步骤2: 人体测量评估
            anthro_trace_id = self._generate_trace_id("Anthropometric_Evaluator", "anthropometric_eval")
            anthropometric_summary = self.anthropometric_evaluator.evaluate(self.patient_data)
            self._add_trace_record(
                anthro_trace_id,
                "Anthropometric_Evaluator",
                {"patient_info": self.patient_data.get("patient_info", {})},
                anthropometric_summary
            )
            self.intermediate_results['anthropometric_evaluation'] = {
                "data": anthropometric_summary,
                "trace_id": anthro_trace_id
            }
            
            # 步骤3: 生化指标解读（依赖临床背景）
            biochem_trace_id = self._generate_trace_id("Biochemical_Interpreter", "biochemical_interp")
            biochemical_summary = self.biochemical_interpreter.interpret(
                self.patient_data, 
                clinical_summary
            )
            self._add_trace_record(
                biochem_trace_id,
                "Biochemical_Interpreter",
                {"lab_results": self.patient_data.get("lab_results", {}),
                 "clinical_context": clinical_summary},
                biochemical_summary,
                dependencies=[clinical_trace_id]
            )
            self.intermediate_results['biochemical_interpretation'] = {
                "data": biochemical_summary,
                "trace_id": biochem_trace_id
            }
            
            # 步骤4: 膳食评估
            dietary_trace_id = self._generate_trace_id("Dietary_Assessor", "dietary_assessment")
            dietary_summary = self.dietary_assessor.assess(self.patient_data)
            self._add_trace_record(
                dietary_trace_id,
                "Dietary_Assessor",
                {"patient_info": self.patient_data.get("patient_info", {}),
                 "consultation": self.patient_data.get("consultation_record", {})},
                dietary_summary
            )
            self.intermediate_results['dietary_assessment'] = {
                "data": dietary_summary,
                "trace_id": dietary_trace_id
            }
            
            # 步骤5: 智能冲突检测 (使用CNA_Coordinator的AI能力)
            conflict_analysis = self._intelligent_conflict_detection(self.intermediate_results)
            
            # 记录冲突检测结果
            conflict_trace_id = self._generate_trace_id("CNA_Coordinator", "conflict_analysis")
            self._add_trace_record(
                conflict_trace_id,
                "CNA_Coordinator",
                {k: v["data"] for k, v in self.intermediate_results.items()},
                conflict_analysis,
                dependencies=[clinical_trace_id, anthro_trace_id, biochem_trace_id, dietary_trace_id]
            )
            
            # 根据冲突检测结果决定是否继续
            if not conflict_analysis.get("proceed_to_final_report", True):
                return {
                    "error": "智能体结果存在严重冲突，终止评估",
                    "conflict_analysis": conflict_analysis,
                    "session_id": self.session_id,
                    "conflict_trace_id": conflict_trace_id
                }
            
            # 步骤6: 生成最终报告
            report_trace_id = self._generate_trace_id("Diagnostic_Reporter", "final_report")
            final_report = self.diagnostic_reporter.generate_report(self.intermediate_results)
            
            # 收集所有依赖
            all_trace_ids = [clinical_trace_id, anthro_trace_id, biochem_trace_id, dietary_trace_id, conflict_trace_id]
            self._add_trace_record(
                report_trace_id,
                "Diagnostic_Reporter",
                {k: v["data"] for k, v in self.intermediate_results.items()},
                final_report,
                dependencies=all_trace_ids
            )
            
            # 构建最终响应
            response = {
                "report": final_report,
                "session_id": self.session_id,
                "assessment_time": datetime.now().isoformat(),
                "processing_duration": (datetime.now() - self.start_time).total_seconds(),
                "validation_results": self.validation_results,
                "conflict_analysis": conflict_analysis,  # 包含冲突分析结果
                "trace_summary": {
                    "total_steps": len(all_trace_ids) + 1,
                    "final_report_trace_id": report_trace_id,
                    "conflict_analysis_trace_id": conflict_trace_id,
                    "intermediate_trace_ids": all_trace_ids
                }
            }
            
            return response
            
        except Exception as e:
            error_trace_id = self._generate_trace_id("CNA_Coordinator", "error")
            self._add_trace_record(
                error_trace_id,
                "CNA_Coordinator",
                {"error": str(e)},
                {"error_type": type(e).__name__, "error_message": str(e)}
            )
            
            return {
                "error": f"评估过程中发生错误: {str(e)}",
                "error_type": type(e).__name__,
                "session_id": self.session_id,
                "error_trace_id": error_trace_id,
                "validation_results": self.validation_results
            }
    
    def get_trace_info(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定追溯ID的详细信息
        
        Args:
            trace_id: 追溯ID
            
        Returns:
            追溯信息，如果不存在则返回None
        """
        return self.data_trace.get(trace_id)
    
    def get_full_trace_chain(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        获取完整的追溯链
        
        Args:
            trace_id: 起始追溯ID
            
        Returns:
            完整的追溯链
        """
        trace_chain = []
        visited = set()
        
        def _collect_dependencies(current_id: str):
            if current_id in visited or current_id not in self.data_trace:
                return
            
            visited.add(current_id)
            trace_info = self.data_trace[current_id]
            
            # 先收集依赖
            for dep_id in trace_info.get("dependencies", []):
                _collect_dependencies(dep_id)
            
            # 再添加当前项
            trace_chain.append(trace_info)
        
        _collect_dependencies(trace_id)
        return trace_chain
    
    def _intelligent_conflict_detection(self, intermediate_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用AI智能检测智能体结果间的冲突和不一致
        
        Args:
            intermediate_results: 中间结果字典
            
        Returns:
            冲突检测结果和建议
        """
        try:
            # 构建冲突检测提示
            prompt = f"""
            请分析以下CNA系统各智能体的评估结果，检测是否存在逻辑冲突或不一致：

            临床背景分析结果：
            {intermediate_results.get('clinical_context', {}).get('data', '无数据')}

            人体测量评估结果：
            {intermediate_results.get('anthropometric_evaluation', {}).get('data', '无数据')}

            生化指标解读结果：
            {intermediate_results.get('biochemical_interpretation', {}).get('data', '无数据')}

            膳食评估结果：
            {intermediate_results.get('dietary_assessment', {}).get('data', '无数据')}

            请检查：
            1. 各评估结果是否在逻辑上一致？
            2. 是否存在明显的矛盾或冲突？
            3. 数据质量是否足够支持最终诊断？
            4. 是否需要某个智能体重新分析？

            请用中文回复，格式为JSON：
            {{
                "has_conflicts": true/false,
                "conflicts_detected": ["具体冲突描述"],
                "data_quality_issues": ["数据质量问题"],
                "recommendations": ["改进建议"],
                "proceed_to_final_report": true/false
            }}
            """
            
            response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
            
            # 解析AI响应
            if isinstance(response, str):
                try:
                    # 尝试从响应中提取JSON
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        conflict_analysis = json.loads(json_match.group())
                    else:
                        # 如果没有找到JSON，创建默认结果
                        conflict_analysis = {
                            "has_conflicts": False,
                            "conflicts_detected": [],
                            "data_quality_issues": [],
                            "recommendations": ["AI分析结果格式异常，建议人工review"],
                            "proceed_to_final_report": True,
                            "ai_response": response
                        }
                except:
                    conflict_analysis = {
                        "has_conflicts": False,
                        "conflicts_detected": [],
                        "data_quality_issues": [],
                        "recommendations": ["AI分析过程中出现异常，建议人工review"],
                        "proceed_to_final_report": True,
                        "ai_response": response
                    }
            else:
                conflict_analysis = {
                    "has_conflicts": False,
                    "conflicts_detected": [],
                    "data_quality_issues": [],
                    "recommendations": ["AI响应格式异常，建议人工review"],
                    "proceed_to_final_report": True
                }
            
            return conflict_analysis
            
        except Exception as e:
            return {
                "has_conflicts": False,
                "conflicts_detected": [],
                "data_quality_issues": [f"冲突检测过程中发生错误: {str(e)}"],
                "recommendations": ["冲突检测功能异常，建议人工review"],
                "proceed_to_final_report": True,
                "error": str(e)
            }