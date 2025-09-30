# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 智能综合营养评估系统 (CNA)

这是一个基于多智能体系统的医疗营养评估应用，支持JSON直接输入和图像识别两种模式，使用 Gemini AI 进行智能分析和报告生成。

## 核心架构模式

### 前后端分离 + 进程通信架构
- **前端**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **后端**: Python多智能体系统 (Microsoft AutoGen框架)
- **通信方式**: Next.js API路由通过子进程调用Python脚本
- **数据流**: 前端 → API路由 → Python子进程(stdin/stdout) → 返回结果

### 智能体系统设计
所有智能体继承自`BaseAgent`基类，使用统一接口规范：
- **CNA_Coordinator**: 中央协调器，管理整个评估流程和数据追溯
- **ImageRecognizer**: 图像识别，支持批量医疗文书OCR
- **临床分析智能体**: Clinical_Context_Analyzer, Anthropometric_Evaluator, Biochemical_Interpreter, Dietary_Assessor
- **Diagnostic_Reporter**: 最终报告生成

### AI模型策略与配置

#### 模型版本规范 (2025年1月更新 - 双模型系列支持)

本项目支持**两大AI模型系列**，用户可在前端UI自由选择：

**📘 Gemini系列（Google AI）**

1. **gemini-2.5-flash** - 中间分析任务
   - 配置变量: `llm_config_gemini_flash_standard`
   - Temperature: 0.5
   - 用途: 5个分析智能体 + 图像识别 + 文本处理

2. **gemini-2.5-flash-preview-09-2025** - 协调管理与报告生成
   - 配置变量: `llm_config_gemini_flash_preview`
   - Temperature: 0.7
   - 用途: CNA_Coordinator + Diagnostic_Reporter

**🟣 DeepSeek系列（DeepSeek AI）**

1. **deepseek-chat** - 中间分析与协调任务
   - 配置变量: `llm_config_deepseek_chat`
   - Base URL: https://api.deepseek.com/v1
   - Temperature: 0.5 (分析), 0.7 (协调)
   - 用途: 5个分析智能体 + CNA_Coordinator + 文本处理

2. **deepseek-reasoner** - 最终报告生成
   - 配置变量: `llm_config_deepseek_reasoner`
   - Base URL: https://api.deepseek.com/v1
   - Temperature: 0.7
   - 用途: Diagnostic_Reporter (增强推理能力)

#### 模型配置文件 (backend/config.py)
```python
# ========== Gemini系列模型 ==========
llm_config_gemini_flash_standard = {
    "config_list": [{
        "model": "gemini-2.5-flash",
        "api_key": GEMINI_API_KEY,
        "api_type": "google",
    }],
    "temperature": 0.5,
}

llm_config_gemini_flash_preview = {
    "config_list": [{
        "model": "gemini-2.5-flash-preview-09-2025",
        "api_key": GEMINI_API_KEY,
        "api_type": "google",
    }],
    "temperature": 0.7,
}

# ========== DeepSeek系列模型 ==========
llm_config_deepseek_chat = {
    "config_list": [{
        "model": "deepseek-chat",
        "api_key": DEEPSEEK_API_KEY,
        "api_type": "openai",
        "base_url": "https://api.deepseek.com/v1",
    }],
    "temperature": 0.5,
}

llm_config_deepseek_reasoner = {
    "config_list": [{
        "model": "deepseek-reasoner",
        "api_key": DEEPSEEK_API_KEY,
        "api_type": "openai",
        "base_url": "https://api.deepseek.com/v1",
    }],
    "temperature": 0.7,
}
```

#### 前端模型选择器

用户在前端页面可以选择两种模型系列（src/app/page.tsx:595-639）：
- **Gemini系列**：快速响应，成本优化，稳定可靠
- **DeepSeek系列**：增强推理，高质量分析，更强的临床推理能力

## 完整复刻指南（Mac环境）

### 前置要求
```bash
# 系统要求
- macOS 10.15 或更高版本
- Xcode Command Line Tools: xcode-select --install

# 软件版本要求
- Node.js 18.x 或更高 (推荐使用 nvm 管理)
- Python 3.9+ (推荐使用 conda 管理)
- npm 9.x 或更高
```

### 第一步：克隆代码
```bash
git clone [repository_url]
cd autogens（kilo&gemini7.11）
```

### 第二步：安装前端环境
```bash
# 安装Node.js (如果未安装)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# 安装前端依赖（确保package-lock.json存在以锁定版本）
npm ci  # 使用ci而非install确保版本一致性

# 验证安装
npm list --depth=0
```

### 第三步：配置Python环境
```bash
# 安装Miniconda（如果未安装）
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh

# 创建并激活虚拟环境
conda create -n cna-env python=3.9
conda activate cna-env

# 安装后端依赖（精确版本）
cd backend
pip install -r requirements.txt

# 验证关键包版本
pip show pyautogen google-generativeai
```

### 第四步：配置API密钥
```bash
# 创建环境变量文件
cd ..  # 回到项目根目录
cp .env .env.local

# 编辑.env.local，添加API密钥
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env.local
echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" >> .env.local

# 获取API密钥：
# Gemini API:
#   1. 访问 https://makersuite.google.com/app/apikey
#   2. 创建新的API密钥
#   3. 确保开启 Gemini 2.5 Flash 模型权限
#
# DeepSeek API (可选):
#   1. 访问 https://platform.deepseek.com/
#   2. 注册账号并创建API密钥
#   3. 确保有足够的credits
#
# 注意：至少需要配置 GEMINI_API_KEY，DeepSeek为可选
```

### 第五步：验证安装
```bash
# 测试前端
npm run dev
# 访问 http://localhost:3000 确认页面加载

# 测试后端（无需API密钥）
cd backend
python demo_main.py

# 测试API连接（需要API密钥）
python test_gemini_api.py
```

## 常用开发命令

### 前端开发
```bash
# 开发服务器
npm run dev

# 构建生产版本
npm run build

# 生产服务器
npm run start

# 代码检查
npm run lint
```

### 后端开发与测试
```bash
# 激活conda环境
conda activate cna-env

# 安装Python依赖
pip install -r backend/requirements.txt

# 系统功能测试 (需要API密钥)
python backend/test_system.py

# 演示模式测试 (无需API密钥)
python backend/demo_main.py

# 图像识别功能测试
python backend/test_image_recognition.py

# 单独测试各个智能体
python backend/test_gemini_api.py

# 主程序 (通常由API路由调用)
python backend/main.py
```

## 关键技术实现

### 1. 双输入模式切换
前端支持JSON输入和图像识别两种模式：
- **JSON模式**: 直接输入结构化患者数据
- **图像模式**: 上传医疗文书图片，自动识别提取数据

核心实现：`src/app/page.tsx`中的`inputMode`状态管理

### 2. 子进程通信模式
API路由使用Node.js child_process与Python通信：
```typescript
// src/app/api/assessment/route.ts
const pythonProcess = spawn('python3', ['main.py'], { cwd: backendPath });
pythonProcess.stdin.write(JSON.stringify(patientData));
```

### 3. 数据追溯性系统
每个分析步骤生成唯一trace_id，支持完整的决策过程追溯：
- 原始数据 → 智能体分析 → 中间结论 → 最终报告
- 实现位置：`backend/agents/cna_coordinator.py`

### 4. 图像识别批处理
支持多张图片同时上传和处理：
- 实时进度显示
- 失败重试机制  
- 自动数据整合
- 实现位置：`src/app/page.tsx` + `backend/agents/image_recognizer.py`

## 环境配置要求

### 必需环境变量
```bash
# .env.local (不提交到版本控制)
GEMINI_API_KEY=your_gemini_api_key_here
```

### Python环境与依赖版本
```text
# Python版本
Python 3.9.x (推荐3.9.18)

# 核心依赖版本 (backend/requirements.txt)
pyautogen              # Microsoft AutoGen框架
python-dotenv          # 环境变量管理
openai                 # OpenAI API客户端（AutoGen依赖）
google-generativeai    # Google Gemini SDK
vertexai               # Google Vertex AI支持
Pillow                 # 图像处理库
jsonschema             # JSON数据验证
httpx>=0.28.1          # 异步HTTP客户端
certifi>=2025.6.15     # SSL证书验证
```

### Node.js环境与依赖版本
```json
// package.json 核心依赖
{
  "dependencies": {
    "next": "^14.2.30",     // Next.js框架
    "react": "^18",         // React 18
    "react-dom": "^18",     // React DOM
    "uuid": "^9.0.0"        // UUID生成器
  },
  "devDependencies": {
    "typescript": "^5",     // TypeScript 5
    "tailwindcss": "^3.4.1", // Tailwind CSS
    "@types/react": "^18",  // React类型定义
    "@types/node": "^20"    // Node类型定义
  }
}
```

### 版本锁定策略
- 前端：使用`package-lock.json`锁定精确版本
- 后端：使用`pip freeze > requirements.txt`导出精确版本
- 建议定期更新并测试兼容性

## API端点

### `/api/assessment` (POST)
主要营养评估接口：
- 输入：`{patient_data: {...}, selected_model: "gemini-flash-preview" | "deepseek"}`
- 输出：营养评估报告
- 模型选择：
  - `gemini-flash-preview` (默认): 使用 gemini-2.5-flash-preview-09-2025
  - `deepseek`: 使用 deepseek-chat (需配置DEEPSEEK_API_KEY)

### `/api/process-text` (POST)
文本处理接口：
- 输入：`{text: "医疗文本内容..."}`
- 输出：结构化患者数据JSON
- 使用模型：gemini-2.5-flash

### `/api/recognize-single-image` (POST)
单张图像识别：
- 输入：FormData包含image文件
- 输出：识别结果JSON
- 使用模型：gemini-2.5-flash

### `/api/recognize-images` (POST)
批量图像识别：
- 输入：多个图像文件
- 输出：整合后的患者数据
- 使用模型：gemini-2.5-flash (多次调用)

### `/api/assessment-with-images` (POST)
图像+评估一体化接口：
- 输入：图像文件 + 可选的额外数据
- 输出：完整评估报告
- 使用模型：gemini-2.5-flash (识别) + 用户选择的报告模型

## 测试策略

### 单元测试
- `backend/test_*.py` 系列脚本测试各个组件
- 使用真实的测试图像：`test_biochem.png`, `test_nutrition.png`, `test_anthropometry.png`

### 系统测试
- `backend/test_system.py`: 完整工作流测试
- `test_patient_data.json`: 标准测试数据集

### 演示模式
- `backend/demo_main.py`: 无需API密钥的模拟测试
- 用于开发环境调试和功能验证

## 关键设计决策

### 1. 为什么使用子进程而非HTTP API？
- 简化部署：避免运行独立的Python服务
- 数据安全：避免敏感患者数据通过网络传输
- 资源管理：每次评估独立的进程，避免内存泄露

### 2. 为什么采用多智能体架构？
- 专业化分工：每个智能体专注特定医学领域
- 可追溯性：清晰的决策链条和责任划分
- 可扩展性：易于添加新的分析维度

### 3. 为什么使用混合AI模型策略？
- **成本优化**: Flash Standard模型处理中间分析任务，成本更低
- **质量保证**: Flash Preview模型用于协调管理和报告生成，能力更强
- **灵活选择**: 支持DeepSeek模型作为可选方案，提供更强推理能力
- **性能平衡**: 在成本、质量和速度间找到最佳平衡点
- **重要说明**: 项目未使用真正的Gemini Pro模型，完全依赖Flash系列，这是有意的架构决策

## 开发注意事项

### 智能体开发
- 继承`BaseAgent`基类确保接口一致性
- 使用结构化输出格式
- 实现完善的错误处理和重试机制
- 位置：`backend/agents/`

### API路由开发
- 使用TypeScript确保类型安全
- 实现适当的超时和错误处理
- 位置：`src/app/api/`

### 前端组件开发
- 优先使用Tailwind CSS工具类
- 实现响应式设计
- 位置：`src/components/`, `src/app/`

### 配置管理
- 环境变量通过`backend/config.py`统一管理
- 模型配置命名规范化 (2025年1月更新):
  - 新命名：`llm_config_flash_standard`, `llm_config_flash_preview`, `llm_config_deepseek`
  - 向后兼容别名：`llm_config_flash`, `llm_config_pro`
- 模型配置支持温度和其他参数调整
- API密钥安全存储，不提交到版本控制

## 故障排查

### 复刻环境常见问题

1. **Python进程启动失败**
   ```bash
   # 问题：spawn python3 ENOENT
   # 解决方案：
   which python3  # 检查python3路径
   conda activate cna-env  # 激活虚拟环境
   python --version  # 确认版本>=3.9
   
   # 如果python3命令不存在，创建符号链接
   ln -s $(which python) /usr/local/bin/python3
   ```

2. **npm ci失败或包版本不一致**
   ```bash
   # 问题：npm ERR! code EINTEGRITY
   # 解决方案：
   rm -rf node_modules package-lock.json
   npm install  # 重新生成lock文件
   
   # 或者使用完全相同的npm版本
   npm --version  # 检查npm版本
   npm install -g npm@9.x.x  # 安装特定版本
   ```

3. **Gemini API配置问题**
   ```bash
   # 问题：401 Unauthorized或API_KEY_INVALID
   # 检查步骤：
   
   # 1. 确认.env.local文件位置正确（项目根目录）
   ls -la | grep .env
   
   # 2. 检查API密钥格式（应该以AIza开头）
   cat .env.local
   
   # 3. 测试API连接
   cd backend
   python -c "from config import GEMINI_API_KEY; print(f'Key loaded: {bool(GEMINI_API_KEY)}')"
   
   # 4. 验证模型权限
   # 访问 https://makersuite.google.com/app/prompts
   # 确认可以使用 gemini-2.5-flash-preview-09-2025 和 gemini-2.5-flash
   ```

4. **M1/M2 Mac架构兼容性**
   ```bash
   # 问题：某些Python包在ARM架构上安装失败
   # 解决方案：
   
   # 使用Rosetta 2模式安装
   arch -x86_64 pip install -r backend/requirements.txt
   
   # 或者使用conda-forge channel
   conda install -c conda-forge pyautogen
   ```

5. **端口占用问题**
   ```bash
   # 问题：Port 3000 is already in use
   # 解决方案：
   lsof -i :3000  # 查找占用进程
   kill -9 <PID>  # 结束进程
   
   # 或使用不同端口
   PORT=3001 npm run dev
   ```

### 验证复刻成功

```bash
# 完整验证清单
echo "=== 前端环境检查 ==="
node --version  # 应该显示 v18.x.x
npm --version   # 应该显示 9.x.x
npm list next react  # 检查核心包版本

echo "=== 后端环境检查 ==="
conda activate cna-env
python --version  # 应该显示 Python 3.9.x
pip show pyautogen google-generativeai  # 检查关键包

echo "=== API配置检查 ==="
cat .env.local | grep GEMINI  # 应该看到API密钥

echo "=== 功能测试 ==="
cd backend
python demo_main.py  # 应该输出模拟报告

echo "=== 服务启动测试 ==="
cd ..
npm run dev  # 应该在3000端口启动
```

## 部署考虑

### 生产环境
- 确保Python环境在服务器上可用
- 配置适当的进程超时和资源限制
- 设置日志和监控机制

### 安全要求
- 妥善管理API密钥
- 实施患者数据隐私保护
- 输入数据验证和清理

## 快速复刻总结

### 最小化步骤（适用于熟悉开发环境的用户）
```bash
# 1. 克隆并进入项目
git clone [repo] && cd autogens（kilo&gemini7.11）

# 2. 前端设置
npm ci && echo "GEMINI_API_KEY=your_key" > .env.local

# 3. 后端设置  
conda create -n cna-env python=3.9 -y
conda activate cna-env
cd backend && pip install -r requirements.txt && cd ..

# 4. 启动应用
npm run dev  # 访问 http://localhost:3000
```

### 关键文件清单
```
必需文件（确保这些文件存在）：
├── package.json          # 前端依赖定义
├── package-lock.json     # 前端依赖版本锁定
├── backend/
│   ├── requirements.txt  # 后端依赖定义
│   ├── config.py         # 模型配置
│   └── agents/           # 所有智能体实现
└── .env.local            # API密钥（需创建）
```

### 模型一致性保证
1. **API版本**: 使用Google AI Studio的`gemini-2.5-flash-preview-09-2025`和`gemini-2.5-flash`
2. **Temperature设置**: Flash=0.5, Pro=0.7
3. **AutoGen配置**: `api_type: "google"`确保正确路由

---

**版本**: 2.2  
**更新日期**: 2024-12-19
**适用范围**: Claude Code开发指南 - 完整复刻版