import sys
import json
from agents.cna_coordinator import CNA_Coordinator
from config import llm_config_pro, llm_config_flash

def consolidate_patient_data(documents: list) -> dict:
    """
    Consolidates a list of medical documents into a single, structured patient data object.
    """
    consolidated_data = {
        "patient_info": {},
        "diagnoses": [],
        "lab_results": {"biochemistry": [], "complete_blood_count": [], "stool_routine": []},
        "symptoms_and_history": {},
        "treatment_plan": {},
        "consultation_record": {}
    }

    for doc in documents:
        doc_type = doc.get("document_type")

        if doc_type == "会诊记录":
            consolidated_data["consultation_record"] = doc
            if doc.get("人体测量"):
                consolidated_data["patient_info"].update(doc["人体测量"])
            if doc.get("主要诊断"):
                consolidated_data["diagnoses"].extend([{"type": "会诊诊断", "description": d} for d in doc["主要诊断"]])

        elif doc_type == "生化检查" and "items" in doc:
            consolidated_data["lab_results"]["biochemistry"].extend(doc["items"])

        elif doc_type == "血常规" and "indicators" in doc:
            consolidated_data["lab_results"]["complete_blood_count"].extend(doc["indicators"])
            if doc.get("patient_info"):
                 # Prioritize more detailed patient info if available
                for key, value in doc["patient_info"].items():
                    if key not in consolidated_data["patient_info"] or not consolidated_data["patient_info"][key]:
                        consolidated_data["patient_info"][key] = value

        elif doc_type == "病历" and "data" in doc:
            if doc["data"].get("主要诊断"):
                consolidated_data["diagnoses"].extend([{"type": "病历诊断", "description": d} for d in doc["data"]["主要诊断"]])
            if doc["data"].get("主要症状"):
                consolidated_data["symptoms_and_history"]["symptoms_from_record"] = doc["data"]["主要症状"]
            if doc["data"].get("治疗方案"):
                consolidated_data["treatment_plan"] = doc["data"]["治疗方案"]
        
        # Fallback for a different "病历" structure
        elif "病历" in doc and isinstance(doc["病历"], dict):
            record = doc["病历"]
            if record.get("主要诊断"):
                consolidated_data["diagnoses"].extend([{"type": "病历诊断", "description": d} for d in record["主要诊断"]])
            if record.get("主要症状"):
                consolidated_data["symptoms_and_history"]["symptoms_from_record_2"] = record["主要症状"]
            if record.get("人体测量"):
                for key, value in record["人体测量"].items():
                    if key not in consolidated_data["patient_info"] or not consolidated_data["patient_info"][key]:
                        consolidated_data["patient_info"][key] = value


    # Clean up diagnoses to remove duplicates
    seen_diagnoses = set()
    unique_diagnoses = []
    for d in consolidated_data["diagnoses"]:
        if d["description"] not in seen_diagnoses:
            unique_diagnoses.append(d)
            seen_diagnoses.add(d["description"])
    consolidated_data["diagnoses"] = unique_diagnoses

    return consolidated_data

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read()
        
        if not input_data:
            print(json.dumps({"error": "No input data received from stdin."}), file=sys.stderr)
            sys.exit(1)

        parsed_data = json.loads(input_data)
        
        # 检查是否包含图像数据
        image_data = None
        patient_json = None
        
        if isinstance(parsed_data, dict) and "patientData" in parsed_data and "imageData" in parsed_data:
            # 新格式：包含患者数据和图像数据
            patient_json = parsed_data["patientData"]
            image_data = parsed_data["imageData"]
        elif isinstance(parsed_data, list):
            # 旧格式：文档列表
            patient_json = consolidate_patient_data(parsed_data)
        elif isinstance(parsed_data, dict):
            # 旧格式：单个患者数据对象
            patient_json = parsed_data
        
        if patient_json is None:
            print(json.dumps({"error": "Invalid patient data format. Expected a JSON object or a list of documents."}), file=sys.stderr)
            sys.exit(1)

        # 初始化协调器并运行评估（可选传入图像数据）
        coordinator = CNA_Coordinator(patient_json, llm_config_pro, llm_config_flash, image_data=image_data)
        result = coordinator.run_assessment()
        
        # Print final result to stdout
        print(json.dumps(result, ensure_ascii=False))

    except json.JSONDecodeError:
        print(json.dumps({"error": "Failed to decode JSON from stdin.", "received_data": input_data}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"An unexpected error occurred: {str(e)}", "error_type": type(e).__name__}), file=sys.stderr)
        sys.exit(1)