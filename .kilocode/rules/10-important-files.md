# 重要文件位置（请勿修改）

为了项目的安全性和稳定性，请指示 KOLO CODE **不要读取或修改** 以下文件或目录：

- **环境变量文件**: `.env`，`.env.local`，`.env.development.local`，`.env.production.local` 等包含 API 密钥或其他敏感环境变量的文件。
- **Gemini 相关配置**: 任何 Gemini 的配置文件或模型存储目录（如果 Cline 需要直接操作这些文件）。通常情况下，KOLO CODE 只需要通过 API 与 Gemini 交互，不需要直接修改其配置。
- **构建输出目录**: 通常是 `/.next/`，`/build/`，`/dist/` 等。
- **包管理器的锁文件**: `package-lock.json` (npm) 或 `yarn.lock` (yarn)。

请确保 KOLO CODE 在执行任何操作时都遵守这些限制，以防止意外修改或暴露敏感信息。
