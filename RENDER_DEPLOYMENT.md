# Render部署指南

## 项目概述

智能综合营养评估系统（CNA）是一个**单体全栈应用**，包含：
- **前端**: Next.js 14 + React 18 + TypeScript
- **后端**: Python多智能体系统（通过子进程调用）
- **AI模型**: Gemini 2.5 Flash / DeepSeek系列

## 架构说明

⚠️ **重要**: 这不是前后端分离架构！

- Next.js应用通过API路由（`spawn`子进程）调用本地Python脚本
- 前后端必须部署在**同一个服务实例**上
- Python环境必须在Node.js运行环境中可用

## 部署前准备

### 1. 获取API密钥

**Gemini API（必需）**:
1. 访问 https://makersuite.google.com/app/apikey
2. 创建新的API密钥
3. 确保开启 `gemini-2.5-flash` 和 `gemini-2.5-flash-preview-09-2025` 模型权限

**DeepSeek API（可选）**:
1. 访问 https://platform.deepseek.com/
2. 注册并获取API密钥
3. 确保账户有足够余额

### 2. 检查代码

确保以下文件存在且配置正确：
- `render.yaml` - Render服务配置
- `backend/requirements.txt` - Python依赖（精确版本）
- `package.json` - Node.js依赖
- `.env.example` - 环境变量模板

## Render部署步骤

### 第一步：连接GitHub仓库

1. **推送代码到GitHub**:
```bash
# 提交所有更改
git add .
git commit -m "准备Render部署"
git push origin main
```

2. **登录Render**:
   - 访问 https://render.com
   - 使用GitHub账号登录

### 第二步：创建Web Service

1. 点击 **"New +"** → **"Web Service"**
2. 连接你的GitHub仓库
3. 选择项目仓库：`autogens（kilo&gemini7.11）`

### 第三步：配置服务

Render会自动读取`render.yaml`，但你也可以手动配置：

**基本配置**:
- **Name**: `nutrition-assessment-app`
- **Runtime**: `Node`
- **Region**: 选择离你最近的区域（如Singapore）
- **Branch**: `main`
- **Root Directory**: 留空（项目根目录）

**构建配置**:
- **Build Command**:
```bash
npm ci && pip install -r backend/requirements.txt && npm run build
```

- **Start Command**:
```bash
npm start
```

**实例类型**:
- 免费层: `Free` (512MB RAM, 共享CPU)
- 推荐: `Starter` ($7/月, 512MB RAM, 专用资源)
- 生产环境: `Standard` ($25/月, 2GB RAM)

### 第四步：配置环境变量

在Render Dashboard → Environment标签页添加：

| Key | Value | 说明 |
|-----|-------|------|
| `NODE_ENV` | `production` | 生产环境标识 |
| `GEMINI_API_KEY` | `AIza...` | 你的Gemini API密钥 |
| `DEEPSEEK_API_KEY` | `sk-...` | DeepSeek密钥（可选） |
| `PYTHON_VERSION` | `3.11` | Python版本 |

⚠️ **安全提示**:
- 不要将API密钥提交到Git仓库
- 在Render中设置为"Secret"（默认已加密）

### 第五步：部署

1. 点击 **"Create Web Service"**
2. Render会自动开始构建和部署
3. 查看构建日志，确保没有错误

**预期构建时长**: 5-10分钟

**构建步骤**:
```
1. Cloning repository...
2. Installing Node.js dependencies (npm ci)
3. Installing Python dependencies (pip install)
4. Building Next.js app (npm run build)
5. Starting production server (npm start)
```

### 第六步：验证部署

1. 构建完成后，访问Render提供的URL：
   ```
   https://nutrition-assessment-app.onrender.com
   ```

2. 测试功能：
   - 切换到"JSON输入"标签
   - 输入测试患者数据
   - 选择AI模型（Gemini/DeepSeek）
   - 点击"生成营养评估报告"
   - 确认报告正常生成

## 常见问题排查

### 1. Python命令未找到

**错误信息**: `spawn python3 ENOENT`

**解决方案**:
```yaml
# render.yaml中添加
envVars:
  - key: PYTHON_VERSION
    value: "3.11"
```

Render会自动安装Python 3.11并将其添加到PATH。

### 2. Python包安装失败

**错误信息**: `pip install failed`

**原因**:
- 内存不足（Free层512MB可能不够）
- 某些包需要编译（如Pillow）

**解决方案**:
1. 升级到Starter计划（512MB专用内存）
2. 或在requirements.txt中使用预编译的wheel包

### 3. 构建超时

**错误信息**: `Build timed out`

**原因**:
- Free层构建时间限制（15分钟）
- Python依赖下载/编译耗时过长

**解决方案**:
1. 使用`npm ci`替代`npm install`（更快）
2. 固定Python包版本（避免重新解析依赖）
3. 升级到付费计划

### 4. API路由500错误

**错误信息**: `POST /api/assessment 500 Internal Server Error`

**排查步骤**:

1. **查看Render日志**:
   - Dashboard → Logs标签页
   - 查找Python进程错误

2. **检查环境变量**:
   - 确认`GEMINI_API_KEY`已设置
   - 测试API密钥有效性

3. **检查Python脚本**:
```bash
# 在Render Shell中测试
python3 backend/main.py <<< '{"patient_data":{},"model_series":"gemini"}'
```

### 5. 图像识别功能不工作

**原因**: Pillow库依赖系统级图像库

**解决方案**:
Render的Node运行时已包含必要的系统库，但如果遇到问题：

```yaml
# render.yaml中添加
buildCommand: |
  apt-get update && apt-get install -y libjpeg-dev zlib1g-dev
  npm ci
  pip install -r backend/requirements.txt
  npm run build
```

### 6. 冷启动延迟

**现象**: 首次访问响应慢（10-30秒）

**原因**:
- Free层服务在不活动15分钟后休眠
- 唤醒需要时间

**解决方案**:
1. 升级到Starter或以上计划（无休眠）
2. 或使用Cron Job保持活跃：
   - 每10分钟ping一次你的URL
   - 可使用UptimeRobot等服务

## 性能优化建议

### 1. 减少构建时间

**优化前** (10-15分钟):
```bash
npm install && pip install -r requirements.txt && npm run build
```

**优化后** (5-8分钟):
```bash
npm ci && pip install --no-cache-dir -r backend/requirements.txt && npm run build
```

### 2. 启用Next.js缓存

在`next.config.js`中：
```javascript
module.exports = {
  experimental: {
    outputFileTracingRoot: path.join(__dirname, '../../'),
  },
  // 启用生产优化
  compress: true,
  poweredByHeader: false,
}
```

### 3. 配置日志级别

在`backend/main.py`中已配置：
```python
logging.basicConfig(
    level=logging.WARNING,  # 生产环境只记录警告及以上
    stream=sys.stderr,
)
```

### 4. 使用CDN（可选）

对于静态资源，可以配置Render的CDN：
- Dashboard → Settings → Static Assets
- 开启"Serve via CDN"

## 监控和维护

### 1. 查看日志

**实时日志**:
```
Dashboard → Logs → Live Logs
```

**搜索历史日志**:
```
Dashboard → Logs → Search
```

### 2. 设置告警

在Render中配置告警通知：
- 服务状态变化
- 构建失败
- 健康检查失败

### 3. 监控指标

Render提供的默认指标：
- CPU使用率
- 内存使用率
- 请求响应时间
- 错误率

### 4. 自动部署

Render默认开启自动部署：
- 每次push到`main`分支自动重新部署
- 可在Settings → Auto-Deploy关闭

## 成本估算

| 计划 | 价格 | 配置 | 适用场景 |
|------|------|------|---------|
| **Free** | $0/月 | 512MB RAM, 共享CPU, 15分钟不活动休眠 | 测试、演示 |
| **Starter** | $7/月 | 512MB RAM, 专用资源, 无休眠 | 个人项目、小团队 |
| **Standard** | $25/月 | 2GB RAM, 更快CPU | 生产环境 |
| **Pro** | $85/月 | 4GB RAM, 高性能 | 高流量应用 |

**推荐配置**:
- 开发/测试: Free
- 小规模生产: Starter
- 正式生产: Standard

## 环境变量管理

### 开发环境

本地使用`.env.local`:
```bash
GEMINI_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
NODE_ENV=development
```

### 生产环境

Render Dashboard配置，不要硬编码在代码中。

### 多环境管理

如需区分staging和production：

1. **创建两个服务**:
   - `nutrition-assessment-staging`
   - `nutrition-assessment-production`

2. **分别配置环境变量**:
   - Staging使用测试API密钥
   - Production使用生产API密钥

## 安全建议

1. **API密钥管理**:
   - 定期轮换API密钥
   - 使用不同密钥区分环境
   - 监控API使用量

2. **访问控制**:
   - 考虑添加身份验证（如NextAuth.js）
   - 限制API调用频率

3. **数据隐私**:
   - 确保患者数据不被记录到日志
   - 遵守HIPAA/GDPR等法规

4. **HTTPS**:
   - Render默认提供免费SSL证书
   - 强制HTTPS（自动配置）

## 备份和恢复

### 数据备份

当前应用无状态，无需备份数据库。

### 代码备份

确保代码推送到GitHub：
```bash
git push origin main
```

### 恢复步骤

如需重新部署：
1. 在Render Dashboard删除旧服务
2. 按照部署步骤重新创建
3. 配置相同的环境变量

## 升级和维护

### 依赖更新

定期更新依赖：

**前端**:
```bash
npm outdated
npm update
npm audit fix
```

**后端**:
```bash
pip list --outdated
pip install --upgrade <package_name>
pip freeze > backend/requirements.txt
```

### Next.js升级

```bash
npm install next@latest react@latest react-dom@latest
npm run build  # 测试构建
```

### Python版本升级

修改`render.yaml`:
```yaml
envVars:
  - key: PYTHON_VERSION
    value: "3.12"  # 新版本
```

## 故障恢复

### 服务不可用

1. **检查服务状态**: Dashboard → Overview
2. **查看最近日志**: Dashboard → Logs
3. **手动重启**: Dashboard → Manual Deploy → "Clear build cache & deploy"

### 回滚到上一版本

```bash
git revert HEAD
git push origin main
```

Render会自动部署回滚后的版本。

## 技术支持

### Render支持

- 文档: https://render.com/docs
- 社区: https://community.render.com
- Email: support@render.com

### 项目支持

- GitHub Issues: [你的仓库]/issues
- 项目文档: `CLAUDE.md`, `AGENTS.md`

## 部署清单

部署前检查：

- [ ] 代码已提交到GitHub
- [ ] `.env.example`已创建（不含真实密钥）
- [ ] `.gitignore`包含`.env`和`.env.local`
- [ ] `render.yaml`配置正确
- [ ] `backend/requirements.txt`包含精确版本
- [ ] 已获取Gemini API密钥
- [ ] 本地测试通过（`npm run build && npm start`）
- [ ] Python脚本可独立运行

部署后验证：

- [ ] 服务启动成功（绿色状态）
- [ ] 健康检查通过
- [ ] 首页可访问
- [ ] JSON输入功能正常
- [ ] 图像识别功能正常
- [ ] 报告生成功能正常
- [ ] 两种模型系列都可用
- [ ] 日志无严重错误

---

**版本**: 1.0
**更新日期**: 2025-09-30
**适用于**: Render.com部署平台
