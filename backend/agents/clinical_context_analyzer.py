import autogen

class ClinicalContextAnalyzer:
    def __init__(self, llm_config):
        self.agent = autogen.AssistantAgent(
            name="Clinical_Context_Analyzer",
            llm_config=llm_config,
            system_message="""
            你是一名临床背景分析师。你的任务是解读患者的医疗状况及其对营养的影响。
            请用中文分析主要诊断、合并症、严重程度和当前治疗。
            识别与疾病相关的潜在营养影响，如高代谢、炎症、吸收不良或器官功能障碍。
            提供一份关于临床背景和潜在营养不良病因的中文摘要。
            """
        )

    def analyze(self, patient_data):
        # In a real scenario, you would craft a detailed prompt based on patient_data
        prompt = f"Analyze the clinical context for the following patient data: {patient_data}"
        
        # This is a simplified interaction. A real implementation might use a UserProxyAgent.
        response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        # Extract the string content from the response
        return response if isinstance(response, str) else response.get("content", "")