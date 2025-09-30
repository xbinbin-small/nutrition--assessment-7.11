# Repository Guidelines

## 架构与智能体职责
- 中央协调器 `CNA_Coordinator`（backend/agents/cna_coordinator.py）串联评估流程与质量控制：收集中间结果、冲突检测、数据追溯（`get_trace_by_id`/`get_full_trace_chain`）。
- 分工智能体：
  - Clinical_Context_Analyzer：临床背景摘要与营养相关病因识别。
  - Anthropometric_Evaluator：BMI/体重变化与表型标准判定。
  - Biochemical_Interpreter：生化/血常规与炎症校正解读。
  - Dietary_Assessor：膳食摄入与需求对比评估。
  - Diagnostic_Reporter：整合生成中文临床营养诊断报告（避免Markdown符号）。
  - ImageRecognizer：可选前置步骤，识别医疗文书图片并产出结构化 JSON，合并入患者数据。

## 交互流程（数据流）
- 步骤0（可选）：ImageRecognizer 识别图片→`integrated_data` 合入 `patient_data`。
- 1 临床背景→2 人体测量→3 生化解读（依赖1）→4 膳食评估→协调器进行冲突检测→5 Reporter 生成最终报告。
- 全程生成 `trace_id` 便于追溯与复跑；错误与缺失字段在 `validation_results` 中暴露。

## 模型与配置
- `llm_config_flash`：`gemini-2.5-flash`（中间分析，温度0.5）。
- `llm_config_pro`：`gemini-2.5-flash-preview-09-2025`（协调/默认报告，温度0.7）。
- 可选 `llm_config_deepseek`：`deepseek-chat`（OpenAI 兼容，`base_url=https://api.deepseek.com`），仅用于 Reporter。前端可通过 `selected_model=deepseek` 切换。
- 环境变量：`GEMINI_API_KEY`（必填），`DEEPSEEK_API_KEY`（可选）。`backend/config.py` 依次加载 `.env` 与 `.env.local`。

## 项目结构与关键入口
- 前端：`src/app`(API路由与页面)、`src/components`、`public/`、`tailwind.config.ts`。
- 后端：`backend/agents` 智能体集，`backend/main.py`（STDIN→STDOUT 评估入口），`backend/image_recognition_service.py` 图像识别服务。

## 开发与运行
- 前端：`npm run dev | build | start | lint`
- 后端：`pip install -r backend/requirements.txt`
- 直接调用（示例）：`echo '{"patient_data":{}}' | python backend/main.py`
- API 示例：
  - 评估：`POST /api/assessment`，body：`{"patient_data":{...},"selected_model":"deepseek|gemini-pro"}`
  - 图文评估：`POST /api/assessment-with-images`（multipart，字段 `patientData` + 多个 `image_*` 文件）

## 代码风格与提交
- TypeScript：2 空格缩进；组件 PascalCase，函数/变量 camelCase，类型以 `*Type/*Props` 结尾。Tailwind 类名按“布局→颜色→细节”。
- Python：PEP8；模块 snake_case，类 PascalCase，函数 snake_case；单一职责与可组合性优先。
- 提交信息用祈使句、单一变更；PR 需含变更摘要、验证方式/截图或日志、潜在风险与待办。

## 测试指南
- 前端单元测试建议放在 `src/__tests__` 或同级 `*.spec.tsx`；提交前跑 `npm run lint`。
- 后端建议 `pytest`（`backend/tests/test_*.py`），并对关键代理的 I/O 进行最小可行桩测试。
