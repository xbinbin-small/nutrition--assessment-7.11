import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * 健康检查端点
 * 用于Render等平台的健康监控
 */
export async function GET() {
  try {
    // 检查Python环境
    const { stdout: pythonVersion } = await execAsync('python3 --version');

    // 检查关键环境变量
    const hasGeminiKey = !!process.env.GEMINI_API_KEY;

    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      environment: {
        nodeVersion: process.version,
        pythonVersion: pythonVersion.trim(),
        platform: process.platform,
      },
      configuration: {
        geminiConfigured: hasGeminiKey,
        deepseekConfigured: !!process.env.DEEPSEEK_API_KEY,
      }
    };

    return NextResponse.json(health, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}
