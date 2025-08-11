import base64
import json
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from PIL import Image
import io
import os

class ImageRecognizer(BaseAgent):
    """
    图像识别智能体 - 负责识别和提取医疗文书图片中的关键信息
    
    使用 Gemini-2.5-flash 模型进行图像识别，提取医疗文书中的结构化数据
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        初始化图像识别智能体
        
        Args:
            llm_config: LLM配置（应使用 gemini-2.5-flash）
        """
        system_message = """
        你是一个专业的医疗文书图像识别智能体，负责从医疗图片中提取关键信息。
        
        你的任务包括：
        1. 识别医疗文书类型（病历、生化检查、血常规、营养评估、人体测量、护理记录、会诊记录等）
        2. 提取关键数据和信息
        3. 将提取的信息组织成结构化的JSON格式
        4. 确保数据的准确性和完整性
        
        提取规则：
        - 病历: 主要诊断、主要症状、治疗方案
        - 生化检查: 特定指标的名称、数值、单位以及检查结论
        - 血常规: 特定指标的名称、数值、单位以及检查结论
        - 营养评估: 营养评估的总体结论，以及关键营养指标的具体数据
        - 人体测量: 身高、体重、BMI值
        - 护理记录: 记录中体现的主要护理措施和效果，患者的重要反应或观察
        - 会诊记录: 会诊的最终结论和给出的主要建议
        
        输出格式要求：
        - 必须返回有效的JSON格式
        - 不同类型的医疗文书可以有不同的JSON结构
        - 确保字段名称清晰易懂
        - 如果某些信息不存在，对应字段可以为null或不包含
        """
        
        super().__init__("ImageRecognizer", llm_config, system_message)
        
    def process(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        处理图像数据，提取医疗信息
        
        Args:
            input_data: 包含图像数据的字典
                - images: 图像文件列表或base64编码的图像数据列表
                - file_paths: 可选的图像文件路径列表
            context: 可选的上下文信息
            
        Returns:
            处理结果，包含提取的医疗信息
        """
        try:
            # 验证输入
            is_valid, error_msg = self.validate_input(input_data)
            if not is_valid:
                return self._create_result({"error": error_msg}, success=False, error_message=error_msg)
            
            # 获取图像数据
            images = input_data.get("images", [])
            file_paths = input_data.get("file_paths", [])
            
            # 如果提供了文件路径，读取图像
            if file_paths and not images:
                images = self._load_images_from_paths(file_paths)
            
            if not images:
                return self._create_result(
                    {"error": "没有提供图像数据"}, 
                    success=False, 
                    error_message="没有提供图像数据"
                )
            
            # 处理每个图像
            all_results = []
            for idx, image_data in enumerate(images):
                result = self._process_single_image(image_data, idx)
                all_results.append(result)
            
            # 整合结果
            consolidated_result = self._consolidate_results(all_results)
            
            return self._create_result(consolidated_result)
            
        except Exception as e:
            self.logger.error(f"图像识别过程中发生错误: {str(e)}")
            return self._create_result(
                {"error": str(e)}, 
                success=False, 
                error_message=f"图像识别失败: {str(e)}"
            )
    
    def _load_images_from_paths(self, file_paths: List[str]) -> List[str]:
        """
        从文件路径加载图像并转换为base64编码
        
        Args:
            file_paths: 图像文件路径列表
            
        Returns:
            base64编码的图像数据列表
        """
        images = []
        for path in file_paths:
            try:
                if os.path.exists(path):
                    with open(path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        images.append(image_data)
                else:
                    self.logger.warning(f"图像文件不存在: {path}")
            except Exception as e:
                self.logger.error(f"加载图像文件失败 {path}: {str(e)}")
        
        return images
    
    def _process_single_image(self, image_data: str, index: int) -> Dict[str, Any]:
        """
        处理单个图像
        
        Args:
            image_data: base64编码的图像数据或文件路径
            index: 图像索引
            
        Returns:
            图像识别结果
        """
        try:
            self.logger.info(f"开始处理图像 {index + 1}")
            
            # 如果是文件路径，读取并转换为base64
            if not image_data.startswith('data:') and os.path.exists(image_data):
                with open(image_data, 'rb') as img_file:
                    image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # 构建Gemini API请求的提示
            prompt = """
            你是一个专业的临床数据提取AI助理，严格遵循指示。你的任务是分析所提供的医疗文书图片，为后续的【临床营养评估多智能体系统】提供高度结构化的JSON输入数据。请务必遵循以下规则：

            1. **最终目的**: 所有提取的数据都是为了进行临床营养评估，请优先关注与营养状况、炎症反应、疾病代谢、膳食摄入和治疗方案相关的信息。
            2. **严格的JSON格式**: 输出必须严格遵循下面定义的JSON结构。即使某些字段在图片中不存在，也请在JSON中保留该字段，并将其值设为`null`。
            3. **精确提取，禁止推断**: 仅提取图片中明确存在的原始数据。不要进行计算（如自行计算BMI）、总结或推断图片中没有的信息。数值必须与原文完全一致。

            【目标JSON结构】
            {
              "document_type": "<文档类型>",
              "patient_info": {
                "height_cm": <身高_数值>,
                "weight_kg": <体重_数值>,
                "bmi": <BMI_数值>
              },
              "diagnoses": [
                {
                  "type": "<诊断类型，如入院诊断、目前诊断>",
                  "description": "<诊断描述>"
                }
              ],
              "symptoms_and_history": {
                "chief_complaint": "<主诉>",
                "history_of_present_illness_summary": "<现病史摘要，重点关注消化道症状、食欲、体重变化>"
              },
              "lab_results": {
                "biochemistry": [
                  {
                    "name": "<指标名称>",
                    "value": "<数值>",
                    "unit": "<单位>",
                    "interpretation": "<箭头或结论，如↑, ↓, 正常, 阳性>"
                  }
                ],
                "complete_blood_count": [
                  {
                    "name": "<指标名称>",
                    "value": "<数值>",
                    "unit": "<单位>",
                    "interpretation": "<箭头或结论>"
                  }
                ],
                "stool_routine": [
                  {
                    "name": "<指标名称>",
                    "value": "<结果>",
                    "interpretation": "<箭头或结论>"
                  }
                ]
              },
              "treatment_plan": {
                "summary": "<治疗方案或诊疗经过摘要>",
                "key_medications": [
                  "<关键药物名称>"
                ]
              },
              "consultation_record": {
                "department": "<会诊科室>",
                "purpose": "<会诊目的>",
                "findings_and_conclusion": "<会诊意见或结论摘要>",
                "recommendations": "<会诊建议>",
                "NRS2002_score": <NRS2002评分>,
                "PES_statement_summary": "<营养诊断PES声明的摘要>"
              }
            }

            【具体提取指南】
            - **文档类型识别**: 首先，将`document_type`识别为以下之一: '病历首页', '生化检查', '血常规', '大便常规', '会诊记录', '营养评估', '人体测量', '护理记录', '其他'。
            - **生化检查**: **必须提取** `白蛋白(ALB)`, `总蛋白(TP)`, `谷丙转氨酶(ALT)`, `肌酐(CREA)`, `尿素(UREA)`, `血糖(GLU)`, `C-反应蛋白(CRP)`, `甘油三酯(TG)`, `总胆固醇(CHOL)`。如果存在，也提取`前白蛋白(PA)`。
            - **血常规**: **必须提取** `白细胞计数(WBC)`, `中性粒细胞计数(NEUT#)`, `淋巴细胞计数(LYM#)`, `血红蛋白(HGB)`, `红细胞计数(RBC)`, `血小板计数(PLT)`。
            - **病历/会诊记录**: 如果文书中提到身高、体重或BMI，请填入`patient_info`。尽可能将所有列出的诊断都填入`diagnoses`数组。从会诊记录中特别提取NRS2002评分和营养支持建议。

            请直接返回JSON格式的结果，不要包含任何其他说明文字、markdown标记或代码块标记。
            """
            
            try:
                # 对于autogen，我们需要使用纯文本方式处理
                # 由于autogen可能不直接支持图像，我们需要使用其他方式
                # 这里我们直接调用Gemini API
                import google.generativeai as genai
                
                # 配置API
                api_key = self.llm_config["config_list"][0]["api_key"]
                genai.configure(api_key=api_key)
                
                # 选择模型
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                self.logger.info(f"使用Gemini API处理图像，API密钥前缀: {api_key[:10]}...")
                
                # 准备图像
                if os.path.exists(image_data):
                    # 如果是文件路径
                    import PIL.Image
                    image = PIL.Image.open(image_data)
                    self.logger.info(f"从文件加载图像: {image_data}")
                else:
                    # 如果是base64数据
                    import io
                    from PIL import Image
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    self.logger.info("从base64数据加载图像")
                
                # 生成内容
                self.logger.info("调用Gemini API生成内容...")
                response = model.generate_content([prompt, image])
                
                # 解析响应
                response_text = response.text
                self.logger.info(f"收到响应，长度: {len(response_text)}")
                
                try:
                    # 尝试从响应中提取JSON
                    import re
                    
                    # 首先尝试提取标准的JSON格式
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        extracted_data = json.loads(json_match.group())
                        self.logger.info(f"成功提取JSON数据")
                        
                        # 验证和标准化提取的数据
                        extracted_data = self._standardize_extracted_data(extracted_data)
                    else:
                        self.logger.warning("无法从响应中找到JSON格式数据")
                        extracted_data = {
                            "error": "无法从响应中提取JSON格式数据",
                            "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
                        }
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败: {str(e)}")
                    extracted_data = {
                        "error": "JSON解析失败",
                        "parse_error": str(e),
                        "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
                    }
                
                return {
                    "image_index": index + 1,
                    "extracted_data": extracted_data,
                    "success": "error" not in extracted_data
                }
                
            except Exception as api_error:
                self.logger.error(f"Gemini API调用失败: {str(api_error)}")
                
                # 尝试备用方法或返回更详细的错误信息
                error_details = {
                    "error": f"API调用失败: {str(api_error)}",
                    "error_type": type(api_error).__name__
                }
                
                # 如果是配额或认证问题，提供更具体的提示
                if "quota" in str(api_error).lower():
                    error_details["suggestion"] = "API配额可能已用完，请检查您的Gemini API使用情况"
                elif "api key" in str(api_error).lower():
                    error_details["suggestion"] = "API密钥可能无效，请检查配置"
                    
                return {
                    "image_index": index + 1,
                    "error": str(api_error),
                    "error_details": error_details,
                    "success": False
                }
            
        except Exception as e:
            self.logger.error(f"处理图像 {index + 1} 时发生错误: {str(e)}")
            return {
                "image_index": index + 1,
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False
            }
    
    def _consolidate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        整合多个图像的识别结果
        
        Args:
            results: 各个图像的识别结果列表
            
        Returns:
            整合后的结果
        """
        consolidated = {
            "total_images": len(results),
            "successful_extractions": sum(1 for r in results if r.get("success", False)),
            "documents": []
        }
        
        # 按文档类型组织数据
        document_types = {
            "病历": [],
            "生化检查": [],
            "血常规": [],
            "营养评估": [],
            "人体测量": [],
            "护理记录": [],
            "会诊记录": [],
            "其他": []
        }
        
        for result in results:
            if result.get("success", False):
                extracted = result.get("extracted_data", {})
                
                # 尝试识别文档类型
                doc_type = self._identify_document_type(extracted)
                
                document_info = {
                    "image_index": result["image_index"],
                    "document_type": doc_type,
                    "data": extracted
                }
                
                consolidated["documents"].append(document_info)
                
                # 分类存储
                if doc_type in document_types:
                    document_types[doc_type].append(extracted)
                else:
                    document_types["其他"].append(extracted)
        
        # 添加分类统计
        consolidated["document_summary"] = {
            doc_type: len(docs) for doc_type, docs in document_types.items() if docs
        }
        
        # 尝试整合关键数据
        consolidated["integrated_data"] = self._integrate_key_data(document_types)
        
        return consolidated
    
    def _identify_document_type(self, extracted_data: Dict[str, Any]) -> str:
        """
        识别文档类型
        
        Args:
            extracted_data: 提取的数据
            
        Returns:
            文档类型
        """
        # 首先检查是否有明确的document_type字段
        if "document_type" in extracted_data:
            return extracted_data["document_type"]
            
        # 基于提取的字段内容判断文档类型
        data_str = str(extracted_data).lower()
        
        if any(key in data_str for key in ["入院诊断", "目前诊断", "主诉", "现病史", "病历"]):
            return "病历首页"
        elif any(key in data_str for key in ["白蛋白", "肌酐", "尿素", "转氨酶", "c-反应蛋白", "crp"]):
            return "生化检查"
        elif any(key in data_str for key in ["白细胞", "红细胞", "血红蛋白", "血小板", "wbc", "rbc"]):
            return "血常规"
        elif any(key in data_str for key in ["大便", "隐血", "粪便"]):
            return "大便常规"
        elif any(key in data_str for key in ["会诊", "营养科", "nrs2002", "pes"]):
            return "会诊记录"
        elif any(key in data_str for key in ["nrs2002", "营养风险", "营养评估"]):
            return "营养评估"
        elif any(key in data_str for key in ["身高", "体重", "bmi"]):
            return "人体测量"
        elif any(key in data_str for key in ["护理", "观察", "记录"]):
            return "护理记录"
        else:
            return "其他"
    
    def _integrate_key_data(self, document_types: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        整合关键数据用于后续分析
        
        Args:
            document_types: 按类型分组的文档数据
            
        Returns:
            整合后的关键数据
        """
        # 初始化标准化的整合数据结构
        integrated = {
            "document_type": "综合病例",
            "patient_info": {
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
        
        # 处理每种文档类型
        for doc_type, docs in document_types.items():
            for doc in docs:
                # 如果文档已经包含标准化结构，直接合并
                if isinstance(doc, dict) and "patient_info" in doc:
                    # 合并patient_info
                    if doc.get("patient_info"):
                        for key, value in doc["patient_info"].items():
                            if value is not None and integrated["patient_info"][key] is None:
                                integrated["patient_info"][key] = value
                    
                    # 合并diagnoses
                    if doc.get("diagnoses"):
                        integrated["diagnoses"].extend(doc["diagnoses"])
                    
                    # 合并symptoms_and_history
                    if doc.get("symptoms_and_history"):
                        for key, value in doc["symptoms_and_history"].items():
                            if value is not None and integrated["symptoms_and_history"][key] is None:
                                integrated["symptoms_and_history"][key] = value
                    
                    # 合并lab_results
                    if doc.get("lab_results"):
                        for result_type, results in doc["lab_results"].items():
                            if isinstance(results, list):
                                integrated["lab_results"][result_type].extend(results)
                    
                    # 合并treatment_plan
                    if doc.get("treatment_plan"):
                        if doc["treatment_plan"].get("summary") and not integrated["treatment_plan"]["summary"]:
                            integrated["treatment_plan"]["summary"] = doc["treatment_plan"]["summary"]
                        if doc["treatment_plan"].get("key_medications"):
                            integrated["treatment_plan"]["key_medications"].extend(doc["treatment_plan"]["key_medications"])
                    
                    # 合并consultation_record
                    if doc.get("consultation_record"):
                        for key, value in doc["consultation_record"].items():
                            if value is not None and integrated["consultation_record"][key] is None:
                                integrated["consultation_record"][key] = value
                
                # 处理旧格式数据（向后兼容）
                else:
                    self._integrate_legacy_format(doc, doc_type, integrated)
        
        # 去除重复的诊断
        seen_diagnoses = set()
        unique_diagnoses = []
        for diagnosis in integrated["diagnoses"]:
            diagnosis_key = f"{diagnosis.get('type', '')}_{diagnosis.get('description', '')}"
            if diagnosis_key not in seen_diagnoses:
                seen_diagnoses.add(diagnosis_key)
                unique_diagnoses.append(diagnosis)
        integrated["diagnoses"] = unique_diagnoses
        
        # 去除重复的药物
        integrated["treatment_plan"]["key_medications"] = list(set(integrated["treatment_plan"]["key_medications"]))
        
        return integrated
    
    def _integrate_legacy_format(self, doc: Dict, doc_type: str, integrated: Dict):
        """
        处理旧格式数据，向后兼容
        """
        if doc_type == "人体测量":
            # 提取身高、体重、BMI
            for key in ["身高", "height"]:
                if key in doc:
                    integrated["patient_info"]["height_cm"] = self._extract_numeric_value({key: doc[key]}, [key])
            for key in ["体重", "weight"]:
                if key in doc:
                    integrated["patient_info"]["weight_kg"] = self._extract_numeric_value({key: doc[key]}, [key])
            for key in ["bmi", "BMI"]:
                if key in doc:
                    integrated["patient_info"]["bmi"] = self._extract_numeric_value({key: doc[key]}, [key])
        
        elif doc_type == "生化检查":
            # 转换为标准格式
            for key, value in doc.items():
                if key not in ["检查日期", "document_type"]:
                    item = {
                        "name": key,
                        "value": None,
                        "unit": None,
                        "interpretation": None
                    }
                    if isinstance(value, str):
                        # 解析值、单位和解释
                        import re
                        match = re.match(r'([\d.]+)\s*([a-zA-Z/]+)?\s*(↑|↓)?', value)
                        if match:
                            item["value"] = match.group(1)
                            item["unit"] = match.group(2) or ""
                            item["interpretation"] = match.group(3) or ""
                        else:
                            item["value"] = value
                    integrated["lab_results"]["biochemistry"].append(item)
        
        elif doc_type == "血常规":
            # 转换为标准格式
            for key, value in doc.items():
                if key not in ["检查日期", "document_type"]:
                    item = {
                        "name": key,
                        "value": None,
                        "unit": None,
                        "interpretation": None
                    }
                    if isinstance(value, str):
                        # 解析值、单位和解释
                        import re
                        match = re.match(r'([\d.]+)\s*([a-zA-Z/^×]+)?\s*(↑|↓)?', value)
                        if match:
                            item["value"] = match.group(1)
                            item["unit"] = match.group(2) or ""
                            item["interpretation"] = match.group(3) or ""
                        else:
                            item["value"] = value
                    integrated["lab_results"]["complete_blood_count"].append(item)
        
        elif doc_type in ["会诊记录", "营养评估"]:
            # 提取NRS2002评分
            for key in ["nrs2002", "NRS2002", "NRS2002评分"]:
                if key in doc:
                    integrated["consultation_record"]["NRS2002_score"] = self._extract_numeric_value({key: doc[key]}, [key])
            
            # 提取PES声明
            for key in ["营养诊断", "PES", "pes", "结论"]:
                if key in doc and not integrated["consultation_record"]["PES_statement_summary"]:
                    integrated["consultation_record"]["PES_statement_summary"] = str(doc[key])
    
    def _extract_numeric_value(self, data: Dict[str, Any], keys: List[str]) -> Optional[float]:
        """
        从数据中提取数值
        
        Args:
            data: 数据字典
            keys: 可能的键名列表
            
        Returns:
            提取的数值或None
        """
        import re
        
        for key in keys:
            for k, v in data.items():
                if key.lower() in k.lower():
                    # 尝试从值中提取数字
                    if isinstance(v, (int, float)):
                        return float(v)
                    elif isinstance(v, str):
                        # 使用正则表达式提取数字
                        numbers = re.findall(r'\d+\.?\d*', v)
                        if numbers:
                            return float(numbers[0])
        
        return None
    
    def _extract_unit(self, value_str: str) -> str:
        """
        从值字符串中提取单位
        
        Args:
            value_str: 包含数值和单位的字符串
            
        Returns:
            提取的单位或空字符串
        """
        import re
        
        # 常见的医学单位
        common_units = [
            "g/L", "mg/L", "mmol/L", "umol/L", "IU/L", "U/L",
            "mg/dL", "g/dL", "cm", "kg", "kg/m²", "%"
        ]
        
        for unit in common_units:
            if unit in value_str:
                return unit
        
        # 尝试提取其他单位格式
        unit_match = re.search(r'[\d\.]+\s*([a-zA-Z/²³]+)', value_str)
        if unit_match:
            return unit_match.group(1)
        
        return ""
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            (是否有效, 错误信息)
        """
        is_valid, base_error = super().validate_input(input_data)
        if not is_valid:
            return False, base_error
        
        # 检查是否提供了图像数据或文件路径
        if "images" not in input_data and "file_paths" not in input_data:
            return False, "必须提供 'images' 或 'file_paths' 字段"
        
        # 验证图像数据格式
        if "images" in input_data:
            images = input_data["images"]
            if not isinstance(images, list):
                return False, "'images' 必须是列表格式"
            if not images:
                return False, "'images' 列表不能为空"
        
        # 验证文件路径格式
        if "file_paths" in input_data:
            file_paths = input_data["file_paths"]
            if not isinstance(file_paths, list):
                return False, "'file_paths' 必须是列表格式"
            if not file_paths:
                return False, "'file_paths' 列表不能为空"
        
        return True, ""
    
    def _standardize_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化提取的数据，确保所有必需字段都存在
        
        Args:
            data: 原始提取的数据
            
        Returns:
            标准化后的数据
        """
        # 定义标准模板
        template = {
            "document_type": None,
            "patient_info": {
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
        
        # 如果数据已经是标准格式，合并到模板中
        if "document_type" in data or "patient_info" in data:
            standardized = self._deep_merge(template, data)
        else:
            # 如果是旧格式，返回原始数据（后续会在_integrate_legacy_format中处理）
            standardized = data
        
        return standardized
    
    def _deep_merge(self, template: Dict, data: Dict) -> Dict:
        """
        深度合并两个字典，保留模板的结构
        """
        result = template.copy()
        
        for key, value in data.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                elif value is not None:
                    result[key] = value
            else:
                result[key] = value
        
        return result