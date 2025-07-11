import autogen

class BiochemicalInterpreter:
    def __init__(self, llm_config):
        self.agent = autogen.AssistantAgent(
            name="Biochemical_Interpreter",
            llm_config=llm_config,
            system_message="""
            你是一名生化指标解读员。你的任务是分析与营养状况相关的实验室数据。
            请结合临床背景（特别是炎症指标如CRP），解读血清蛋白（白蛋白、前白蛋白）。
            评估免疫功能、维生素/矿物质状态和电解质平衡的标志物。
            区分营养不良和炎症引起的低蛋白水平。
            请用中文提供摘要。
            """
        )

    def interpret(self, patient_data, clinical_context):
        prompt = f"""
        Given the following clinical context: {clinical_context}.
        Interpret the biochemical lab results for the patient: {patient_data.get('lab_results')}
        """
        response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        return response if isinstance(response, str) else response.get("content", "")