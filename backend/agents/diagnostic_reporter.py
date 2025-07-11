import autogen

class DiagnosticReporter:
    def __init__(self, llm_config):
        self.agent = autogen.AssistantAgent(
            name="Diagnostic_Reporter",
            llm_config=llm_config,
            system_message="""
            你是一位专业的临床营养诊断报告专家。
            你的任务是综合所有提供的分析结果（临床背景、人体测量、生化指标、膳食评估），形成一份全面、专业的中文营养诊断报告。
            请遵循以下结构，并使用自然语言进行书写，避免使用Markdown的星号、井号等标记符号。

            报告结构应包括：
            1. 患者基本情况摘要
            2. 营养风险等级
            3. 关键评估发现
            4. 营养诊断 (使用PES格式)
            5. 主要营养问题
            6. 营养治疗目标 (遵循SMART原则)
            7. 营养干预措施

            报告必须清晰、简洁，语言通顺，符合中国临床医生的阅读习惯。
            """
        )

    def generate_report(self, intermediate_results):
        # 提取每个智能体的核心分析结果
        clinical_context = intermediate_results.get('clinical_context', {}).get('data', '无')
        anthropometric_eval = intermediate_results.get('anthropometric_evaluation', {}).get('data', '无')
        biochemical_interp = intermediate_results.get('biochemical_interpretation', {}).get('data', '无')
        dietary_assess = intermediate_results.get('dietary_assessment', {}).get('data', '无')

        # 构建一个更结构化、更具引导性的提示
        prompt = f"""
        请根据以下各方面评估结果，严格按照指定的报告结构，生成一份专业的临床营养诊断报告。
        **禁止**在报告开头添加任何引导性语句（如“好的，这是...”）。
        **禁止**在报告中使用任何Markdown格式（如'###', '*', '1.'）。
        每个部分标题后直接跟内容，部分之间用两个换行符分隔。

        --- 原始评估数据 ---
        1.  **临床背景分析**: {clinical_context}
        2.  **人体测量评估**: {anthropometric_eval}
        3.  **生化指标解读**: {biochemical_interp}
        4.  **膳食评估**: {dietary_assess}
        --- 报告生成指令 ---

        请严格按照以下标题和顺序生成报告：

        **患者基本情况摘要**
        [此处总结患者的核心临床问题和当前状况]

        **营养风险等级**
        [此处明确指出营养风险等级，并简要说明判断依据]

        **关键评估发现**
        [此处整合人体测量、生化和膳食评估的关键阳性发现]

        **营养诊断 (PES格式)**
        [此处以“问题(P) ... 与 ... 有关(E) ... 表现为 ...(S)”的格式写出结构化的PES声明]

        **主要营养问题**
        [此处列出1-3个最主要的营养问题]

        **营养治疗目标**
        [此处根据SMART原则，制定具体、可量化的短期和长期目标]

        **营养干预措施**
        [此处提供具体、可操作的营养干预建议]
        """
        
        response = self.agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        
        # 清理响应，移除潜在的Markdown和多余的换行符
        report_text = response if isinstance(response, str) else response.get("content", "")
        report_text = report_text.replace("###", "").replace("####", "").replace("*", "").strip()
        
        return report_text