import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    console.log("Received body:", JSON.stringify(body, null, 2));
    const patientData = body;

    if (!patientData) {
      return NextResponse.json({ error: 'Patient data is required' }, { status: 400 });
    }

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

    // Write patient data to the Python script's stdin
    const dataString = JSON.stringify(patientData);
    console.log("Writing to python stdin:", dataString);
    pythonProcess.stdin.write(dataString);
    pythonProcess.stdin.end();

    const processPromise = new Promise<NextResponse>((resolve) => {
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}`);
          console.error(errorData);
          resolve(NextResponse.json({ error: 'Error during assessment', details: errorData }, { status: 500 }));
        } else {
          try {
            const result = JSON.parse(reportData);
            resolve(NextResponse.json(result));
          } catch (e) {
            console.error('Error parsing python script output:', e);
            resolve(NextResponse.json({ error: 'Failed to parse assessment report', details: reportData }, { status: 500 }));
          }
        }
      });
    });

    return await processPromise;

  } catch (error) {
    console.error('API Route Error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}