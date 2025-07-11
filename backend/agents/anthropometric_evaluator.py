import autogen

class AnthropometricEvaluator:
    def __init__(self, llm_config):
        self.agent = autogen.AssistantAgent(
            name="Anthropometric_Evaluator",
            llm_config=llm_config,
            system_message="""
            你是一名人体测量评估师。你的任务是处理和解读身体测量数据。
            请用中文计算BMI、体重变化百分比，并与标准进行比较。
            解读上臂围、皮褶厚度等测量值，以评估脂肪和肌肉储备。
            识别是否满足营养不良的表型标准（如低BMI、体重减轻、肌肉量减少），并量化其严重程度。
            请用中文提供摘要。
            """
        )

    def evaluate(self, patient_data):
        prompt = f"Evaluate the anthropometric data for the following patient: {patient_data}"
        response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        return response if isinstance(response, str) else response.get("content", "")