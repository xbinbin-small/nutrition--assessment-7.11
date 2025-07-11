在本项目中，我们优先使用以下技术栈进行开发：
- **项目架构**: 
  - 前端文件放在`frontend`目录中
  - 后端Python智能体代码放在`backend`目录中
  - 使用**Next.js API路由**作为前端与后端智能体之间的桥梁
- **前后端交互流程**:
  1. 前端(React)将患者数据(JSON格式)发送到Next.js API路由(`/src/app/api`)
  2. API路由通过子进程调用Python脚本(`/backend/main.py`)
  3. Python autogen工作流运行，完成评估
  4. 最终报告通过stdout返回给API路由
  5. API路由将结果返回给前端
- **前端框架**: **Next.js (稳定版)**。优先使用App Router (`/src/app`目录)
- **样式库**: **Tailwind CSS (最新版)**
- **前端编程语言**: **TypeScript**
- **后端智能体框架**: **autogen**
- **后端编程语言**: **Python**
- **AI 模型策略**:
  - **`gemini-2.5-pro-preview-06-05`**: 用于最终报告生成(`Diagnostic_Reporter`)
  - **`gemini-2.5-flash-preview-05-20`**: 用于中间分析步骤(`Clinical_Context_Analyzer`等)
- **虚拟运行环境**: Conda
- **包管理器**: **npm**
