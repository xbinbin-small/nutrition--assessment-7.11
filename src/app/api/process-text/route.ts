import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";

export async function POST(request: NextRequest) {
  console.log("=== 接收文本处理请求 ===");

  try {
    const body = await request.json();
    const { text } = body;

    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: "缺少有效的文本内容" },
        { status: 400 }
      );
    }

    console.log("收到文本内容，长度:", text.length);

    // 获取后端目录路径
    const backendPath = path.join(process.cwd(), "backend");
    console.log("后端路径:", backendPath);

    // 创建Python子进程
    const pythonProcess = spawn("python3", ["text_processing_service.py"], {
      cwd: backendPath,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let pythonOutput = "";
    let pythonError = "";

    // 监听Python输出
    pythonProcess.stdout.on("data", (data) => {
      pythonOutput += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      pythonError += data.toString();
      console.log("Python stderr:", data.toString());
    });

    // 发送文本数据到Python进程
    const inputData = JSON.stringify({ text });
    pythonProcess.stdin.write(inputData);
    pythonProcess.stdin.end();

    // 等待Python进程完成
    const result = await new Promise((resolve, reject) => {
      pythonProcess.on("close", (code) => {
        console.log(`Python进程退出，代码: ${code}`);
        console.log("Python输出:", pythonOutput);

        if (code !== 0) {
          reject(new Error(`Python进程异常退出: ${pythonError}`));
          return;
        }

        try {
          const processedData = JSON.parse(pythonOutput);
          resolve(processedData);
        } catch (error) {
          console.error("解析Python输出失败:", pythonOutput);
          reject(new Error(`解析输出失败: ${error}`));
        }
      });

      pythonProcess.on("error", (error) => {
        reject(new Error(`启动Python进程失败: ${error.message}`));
      });
    });

    console.log("文本处理成功");
    return NextResponse.json(result);

  } catch (error) {
    console.error("文本处理出错:", error);
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "文本处理失败"
      },
      { status: 500 }
    );
  }
}