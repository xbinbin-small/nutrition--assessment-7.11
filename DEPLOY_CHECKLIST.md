# Render部署快速清单

## 部署前准备 ✓

### 1. 环境准备
- [ ] 获取Gemini API密钥: https://makersuite.google.com/app/apikey
- [ ] 获取DeepSeek API密钥（可选）: https://platform.deepseek.com/
- [ ] 注册Render账号: https://render.com

### 2. 代码检查
```bash
# 检查依赖安装
npm ci
pip install -r backend/requirements.txt

# 本地构建测试
npm run build

# 本地运行测试
npm start
# 访问 http://localhost:3000 验证功能
```

### 3. Git提交
```bash
git status
git add .
git commit -m "准备Render部署"
git push origin main
```

## Render配置步骤 ⚡

### Step 1: 创建服务
1. 登录 https://dashboard.render.com
2. 点击 **New +** → **Web Service**
3. 连接GitHub仓库
4. 选择项目仓库

### Step 2: 基本配置
- **Name**: `nutrition-assessment-app`
- **Runtime**: Node
- **Branch**: main
- **Build Command**:
  ```bash
  npm ci && pip install -r backend/requirements.txt && npm run build
  ```
- **Start Command**:
  ```bash
  npm start
  ```

### Step 3: 环境变量
在Environment标签页添加：

```
NODE_ENV=production
GEMINI_API_KEY=你的_Gemini_API_密钥
DEEPSEEK_API_KEY=你的_DeepSeek_API_密钥（可选）
PYTHON_VERSION=3.11
```

### Step 4: 实例选择
- 测试: **Free** ($0/月)
- 推荐: **Starter** ($7/月) ⭐
- 生产: **Standard** ($25/月)

### Step 5: 部署
点击 **Create Web Service** 开始部署

## 部署后验证 ✅

### 功能测试
- [ ] 访问Render提供的URL
- [ ] 首页加载正常
- [ ] JSON输入模式可用
- [ ] 图像识别模式可用
- [ ] 文本录入模式可用
- [ ] Gemini模型生成报告成功
- [ ] DeepSeek模型生成报告成功（如配置）

### 日志检查
```
Dashboard → Logs → 查看无严重错误
```

### 性能检查
- [ ] 首次加载时间 < 5秒
- [ ] 报告生成时间 < 3分钟
- [ ] 无内存溢出错误

## 常见问题快速修复 🔧

### 构建失败
```bash
# 检查render.yaml语法
cat render.yaml

# 检查requirements.txt
cat backend/requirements.txt
```

### Python未找到
确保环境变量中设置：
```
PYTHON_VERSION=3.11
```

### API密钥无效
1. 重新生成API密钥
2. 在Render Dashboard更新环境变量
3. Manual Deploy → Clear cache & deploy

### 500错误
查看Render Logs中的Python错误输出（stderr）

## 成本参考 💰

| 计划 | 月费 | RAM | 休眠 | 适用 |
|------|------|-----|------|------|
| Free | $0 | 512MB | 15分钟 | 测试 |
| Starter | $7 | 512MB | 无 | 个人 ⭐ |
| Standard | $25 | 2GB | 无 | 生产 |

## 支持资源 📚

- 完整部署指南: `RENDER_DEPLOYMENT.md`
- 项目文档: `CLAUDE.md`
- Render文档: https://render.com/docs
- GitHub Issues: 报告问题

---

**快速部署**: 15分钟完成 🚀
**最后更新**: 2025-09-30
