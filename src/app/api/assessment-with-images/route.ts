import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { writeFile, unlink } from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request: Request) {
  const tempFiles: string[] = [];
  
  try {
    const formData = await request.formData();
    
    // 获取患者数据
    const patientDataString = formData.get('patientData') as string;
    if (!patientDataString) {
      return NextResponse.json({ error: '缺少患者数据' }, { status: 400 });
    }
    
    let patientData;
    try {
      patientData = JSON.parse(patientDataString);
    } catch (e) {
      return NextResponse.json({ error: '患者数据JSON格式无效' }, { status: 400 });
    }
    
    // 处理图像文件
    const imagePaths: string[] = [];
    const tempDir = path.join(process.cwd(), 'temp');
    
    // 确保临时目录存在
    const fs = require('fs');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    // 处理每个上传的图像
    for (const [key, value] of formData) {
      if (key.startsWith('image_') && value instanceof File) {
        const bytes = await value.arrayBuffer();
        const buffer = Buffer.from(bytes);
        
        // 生成唯一的文件名
        const fileName = `${uuidv4()}_${value.name}`;
        const filePath = path.join(tempDir, fileName);
        
        await writeFile(filePath, buffer);
        tempFiles.push(filePath);
        imagePaths.push(filePath);
      }
    }
    
    // 准备发送给Python的数据
    const dataToSend = {
      patientData: patientData,
      imageData: imagePaths.length > 0 ? { file_paths: imagePaths } : null
    };
    
    const backendPath = path.join(process.cwd(), 'backend');
    const pythonProcess = spawn('python3', ['main.py'], { cwd: backendPath });
    
    let reportData = '';
    let errorData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      reportData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
    });
    
    // 发送数据到Python脚本
    pythonProcess.stdin.write(JSON.stringify(dataToSend));
    pythonProcess.stdin.end();
    
    const processPromise = new Promise<NextResponse>((resolve) => {
      pythonProcess.on('close', async (code) => {
        // 清理临时文件
        for (const file of tempFiles) {
          try {
            await unlink(file);
          } catch (e) {
            console.error(`Failed to delete temp file ${file}:`, e);
          }
        }
        
        if (code !== 0) {
          console.error(`Python script exited with code ${code}`);
          console.error(errorData);
          resolve(NextResponse.json({ error: '评估过程中发生错误', details: errorData }, { status: 500 }));
        } else {
          try {
            const result = JSON.parse(reportData);
            resolve(NextResponse.json(result));
          } catch (e) {
            console.error('Error parsing python script output:', e);
            resolve(NextResponse.json({ error: '解析评估报告失败', details: reportData }, { status: 500 }));
          }
        }
      });
    });
    
    return await processPromise;
    
  } catch (error) {
    // 清理临时文件
    for (const file of tempFiles) {
      try {
        await unlink(file);
      } catch (e) {
        console.error(`Failed to delete temp file ${file}:`, e);
      }
    }
    
    console.error('API Route Error:', error);
    return NextResponse.json({ error: '服务器内部错误' }, { status: 500 });
  }
}