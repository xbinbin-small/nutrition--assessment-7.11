# Gemini 配置

本项目使用 Gemini 服务来生成评估模型。请注意以下配置和步骤：

- **模型使用策略**:
  - **`gemini-2.5-pro` (Pro 模型)**: 用于最终的 `Diagnostic_Reporter` 智能体生成综合评估报告
  - **`gemini-2.5-flash` (Flash 模型)**: 用于中间分析步骤(`Clinical_Context_Analyzer`, `Anthropometric_Evaluator`, `Biochemical_Interpreter`, `Dietary_Assessor`)

- **API 交互**: 在 Next.js 的 API 路由中实现与 Gemini API 的交互。使用 `fetch` 向 Gemini API 发送 POST 请求。

- **API 端点**: Gemini 的文本生成 API 端点为 `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent`

- **请求头**:
  ```json
  {
    "Content-Type": "application/json",
    "Authorization": "Bearer ${process.env.GEMINI_API_KEY}"
  }
  ```

- **请求体结构**:
  ```json
  {
    "model": "models/gemini-2.5-pro",
    "prompt": {
      "text": "您的提示内容"
    }
  }
  ```

- **提示工程最佳实践**:
  1. 使用结构化 JSON 格式传递患者数据
  2. 明确指定输出格式要求
  3. 提供上下文信息（如评估类型、报告格式要求）
  4. 分步骤引导模型思考过程


- **错误处理**:
  - 网络错误: 重试机制（最多3次）
  - API错误: 检查错误代码和消息
  - 模型生成错误: 验证输出格式和内容完整性
