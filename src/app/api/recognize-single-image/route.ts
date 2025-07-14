import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { writeFile, unlink } from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request: Request) {
  let tempFile: string | null = null;
  
  try {
    console.log('=== Received image recognition request ===');
    console.log('Request headers:', request.headers);
    
    // 尝试解析请求体
    let formData: FormData;
    try {
      formData = await request.formData();
      console.log('FormData parsed successfully');
    } catch (formError) {
      console.error('Failed to parse FormData:', formError);
      return NextResponse.json({ 
        error: '无法解析请求数据',
        details: formError instanceof Error ? formError.message : 'Unknown error'
      }, { status: 400 });
    }
    
    // 打印所有表单字段以调试
    console.log('FormData entries:');
    const entries = Array.from(formData.entries());
    console.log(`Total entries: ${entries.length}`);
    for (const [key, value] of entries) {
      console.log(`  ${key}:`, value instanceof File ? `File(${value.name}, size: ${value.size})` : value);
    }
    
    const image = formData.get('image') as File;
    
    if (!image) {
      console.error('No image file found in request');
      return NextResponse.json({ 
        error: '没有上传图像文件',
        debug: 'FormData中未找到名为"image"的文件',
        entries: entries.map(([k, v]) => ({ key: k, type: v instanceof File ? 'File' : typeof v }))
      }, { status: 400 });
    }
    
    if (!(image instanceof File)) {
      console.error('image is not a File instance');
      return NextResponse.json({ 
        error: '上传的不是有效的文件',
        debug: `image字段类型: ${typeof image}`
      }, { status: 400 });
    }
    
    console.log(`Processing image: ${image.name}, size: ${image.size}`);
    
    // 临时保存上传的图像文件
    const tempDir = path.join(process.cwd(), 'temp');
    
    // 确保临时目录存在
    const fs = require('fs');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    // 处理图像
    const bytes = await image.arrayBuffer();
    const buffer = Buffer.from(bytes);
    
    // 生成唯一的文件名
    const fileName = `${uuidv4()}_${image.name}`;
    tempFile = path.join(tempDir, fileName);
    
    await writeFile(tempFile, buffer);
    console.log(`Saved temp file: ${tempFile}`);
    
    // 准备图像数据用于Python处理
    const imageData = {
      file_paths: [tempFile]
    };
    
    const backendPath = path.join(process.cwd(), 'backend');
    const pythonProcess = spawn('python3', ['image_recognition_service.py'], { cwd: backendPath });
    
    let resultData = '';
    let errorData = '';
    
    pythonProcess.stdout.on('data', (data) => {
      resultData += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      console.error('Python stderr:', data.toString());
    });
    
    // 发送图像路径到Python脚本
    pythonProcess.stdin.write(JSON.stringify(imageData));
    pythonProcess.stdin.end();
    
    const processPromise = new Promise<NextResponse>((resolve) => {
      pythonProcess.on('close', async (code) => {
        // 清理临时文件
        if (tempFile) {
          try {
            await unlink(tempFile);
            console.log(`Deleted temp file: ${tempFile}`);
          } catch (e) {
            console.error(`Failed to delete temp file ${tempFile}:`, e);
          }
        }
        
        if (code !== 0) {
          console.error(`Python script exited with code ${code}`);
          console.error('Python error output:', errorData);
          resolve(NextResponse.json({ 
            error: '图像识别失败', 
            details: errorData,
            code: code
          }, { status: 500 }));
        } else {
          console.log('Python output:', resultData);
          try {
            const result = JSON.parse(resultData);
            
            // 提取单个图像的结果
            if (result.documents && result.documents.length > 0) {
              const doc = result.documents[0];
              console.log('Recognition successful:', doc.document_type);
              resolve(NextResponse.json({
                success: true,
                document_type: doc.document_type,
                extracted_data: doc.data,
                integrated_data: result.integrated_data || {}
              }));
            } else if (result.error) {
              console.error('Recognition error:', result.error);
              resolve(NextResponse.json({ 
                error: result.error,
                details: result.details || ''
              }, { status: 400 }));
            } else {
              console.error('No valid data recognized');
              resolve(NextResponse.json({ 
                error: '没有识别到有效数据',
                result: result
              }, { status: 400 }));
            }
          } catch (e) {
            console.error('Error parsing python script output:', e);
            console.error('Raw output:', resultData);
            resolve(NextResponse.json({ 
              error: '解析识别结果失败', 
              details: resultData,
              parseError: e instanceof Error ? e.message : String(e)
            }, { status: 500 }));
          }
        }
      });
    });
    
    return await processPromise;
    
  } catch (error) {
    // 清理临时文件
    if (tempFile) {
      try {
        await unlink(tempFile);
      } catch (e) {
        console.error(`Failed to delete temp file ${tempFile}:`, e);
      }
    }
    
    console.error('API Route Error:', error);
    return NextResponse.json({ 
      error: '服务器内部错误',
      message: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}