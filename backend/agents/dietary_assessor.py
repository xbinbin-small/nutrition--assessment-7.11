import autogen

class DietaryAssessor:
    def __init__(self, llm_config):
        self.agent = autogen.AssistantAgent(
            name="Dietary_Assessor",
            llm_config=llm_config,
            system_message="""
            你是一名膳食评估员。你的任务是评估患者的食物和营养素摄入量。
            根据患者的临床背景估算其能量、蛋白质和液体的需求。
            分析膳食摄入数据，并与估算需求进行比较。
            识别饮食的定性方面（如质地、不耐受等）。
            确定是否满足营养不良的病因标准（摄入减少/吸收障碍）。
            请用中文提供摘要。
            """
        )

    def assess(self, patient_data):
        prompt = f"Assess the dietary intake and needs for the following patient: {patient_data}"
        response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        return response if isinstance(response, str) else response.get("content", "")