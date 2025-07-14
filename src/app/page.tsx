"use client";

import { useState } from "react";
import ReportDisplay from "@/components/ReportDisplay";

interface ImageRecognitionResult {
  id: string;
  fileName: string;
  status: "pending" | "processing" | "success" | "error";
  result?: any;
  error?: string;
}

export default function Home() {
  const [patientData, setPatientData] = useState("");
  const [assessmentResult, setAssessmentResult] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState("");
  const [uploadedImages, setUploadedImages] = useState<File[]>([]);
  const [imageRecognitionResults, setImageRecognitionResults] = useState<ImageRecognitionResult[]>([]);
  const [inputMode, setInputMode] = useState<"json" | "image">("json");
  const [isIntegrating, setIsIntegrating] = useState(false);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      const fileArray = Array.from(files);
      setUploadedImages(fileArray);
      
      // 初始化每个图片的识别状态
      const initialResults = fileArray.map((file, index) => ({
        id: `${Date.now()}_${index}`,
        fileName: file.name,
        status: "pending" as const,
      }));
      setImageRecognitionResults(initialResults);
    }
  };

  // 识别单张图片
  const recognizeSingleImage = async (file: File, resultId: string) => {
    // 更新状态为处理中
    setImageRecognitionResults(prev => 
      prev.map(r => r.id === resultId ? { ...r, status: "processing" } : r)
    );

    try {
      const formData = new FormData();
      formData.append("image", file);

      console.log(`Uploading image: ${file.name}, size: ${file.size}`);

      const res = await fetch("/api/recognize-single-image", {
        method: "POST",
        body: formData,
      });

      const responseText = await res.text();
      let result;
      
      try {
        result = JSON.parse(responseText);
      } catch (parseError) {
        console.error("Failed to parse response:", responseText);
        throw new Error(`服务器响应无效: ${responseText.substring(0, 200)}`);
      }

      if (!res.ok) {
        console.error("API returned error:", result);
        throw new Error(result.error || `图像识别失败 (${res.status})`);
      }
      
      // 更新状态为成功
      setImageRecognitionResults(prev => 
        prev.map(r => r.id === resultId ? { 
          ...r, 
          status: "success", 
          result: result 
        } : r)
      );
    } catch (error) {
      // 更新状态为错误
      setImageRecognitionResults(prev => 
        prev.map(r => r.id === resultId ? { 
          ...r, 
          status: "error", 
          error: error instanceof Error ? error.message : "识别失败" 
        } : r)
      );
    }
  };

  // 开始批量识别
  const handleBatchRecognition = async () => {
    // 依次识别每张图片
    for (let i = 0; i < uploadedImages.length; i++) {
      const file = uploadedImages[i];
      const result = imageRecognitionResults[i];
      
      // 只处理待处理或失败的图片
      if (result.status === "pending" || result.status === "error") {
        await recognizeSingleImage(file, result.id);
      }
    }
  };

  // 重试单张图片
  const retrySingleImage = async (resultId: string) => {
    const index = imageRecognitionResults.findIndex(r => r.id === resultId);
    if (index !== -1 && uploadedImages[index]) {
      await recognizeSingleImage(uploadedImages[index], resultId);
    }
  };

  // 整合所有识别结果
  const handleIntegrateResults = () => {
    setIsIntegrating(true);
    
    // 收集所有成功的识别结果
    const successfulResults = imageRecognitionResults
      .filter(r => r.status === "success" && r.result)
      .map(r => r.result);
    
    // 整合数据
    const integratedData = {
      patient_info: {},
      diagnoses: [],
      lab_results: {
        biochemistry: [],
        complete_blood_count: [],
        stool_routine: []
      },
      symptoms_and_history: {},
      treatment_plan: {},
      consultation_record: {},
      // 添加原始识别数据字段
      raw_recognized_data: []
    };
    
    // 处理每个识别结果
    successfulResults.forEach((result, index) => {
      // 获取实际的识别数据
      const extractedData = result.extracted_data || result;
      const documentType = result.document_type || "未知类型";
      
      // 保存原始识别数据
      integratedData.raw_recognized_data.push({
        document_type: documentType,
        data: extractedData
      });
      
      // 根据文档类型处理数据
      if (documentType.includes("生化") || documentType.includes("检查")) {
        // 处理生化检查数据
        if (extractedData && typeof extractedData === 'object') {
          Object.entries(extractedData).forEach(([key, value]) => {
            // 跳过非检查项目的字段
            if (key === "检查日期" || key === "结论" || key === "文书类型") return;
            
            // 提取数值和单位
            if (typeof value === 'string' && value.match(/[\d.]+/)) {
              const match = value.match(/([\d.]+)\s*([a-zA-Z/]+)?/);
              if (match) {
                integratedData.lab_results.biochemistry.push({
                  name: key,
                  value: match[1],
                  unit: match[2] || "",
                  interpretation: value.includes("↑") ? "↑" : value.includes("↓") ? "↓" : ""
                });
              }
            }
          });
        }
      } else if (documentType.includes("营养") || documentType.includes("NRS")) {
        // 处理营养评估数据
        if (extractedData) {
          // 提取NRS2002评分
          if (extractedData.NRS2002评分 || extractedData["NRS2002评分"]) {
            const score = extractedData.NRS2002评分 || extractedData["NRS2002评分"];
            const scoreNum = typeof score === 'string' ? parseInt(score.match(/\d+/)?.[0] || "0") : score;
            integratedData.consultation_record.NRS2002_score = scoreNum;
          }
          
          // 提取营养评估结论
          if (extractedData.结论 || extractedData.conclusion) {
            integratedData.consultation_record.nutritional_assessment = extractedData.结论 || extractedData.conclusion;
          }
        }
      } else if (documentType.includes("人体测量") || documentType.includes("体重")) {
        // 处理人体测量数据
        if (extractedData) {
          // 提取身高
          if (extractedData.身高) {
            const height = extractedData.身高;
            const heightNum = typeof height === 'string' ? parseFloat(height.match(/[\d.]+/)?.[0] || "0") : height;
            integratedData.patient_info.height_cm = heightNum;
          }
          
          // 提取体重
          if (extractedData.体重) {
            const weight = extractedData.体重;
            const weightNum = typeof weight === 'string' ? parseFloat(weight.match(/[\d.]+/)?.[0] || "0") : weight;
            integratedData.patient_info.weight_kg = weightNum;
          }
          
          // 提取BMI
          if (extractedData.BMI || extractedData.bmi) {
            const bmi = extractedData.BMI || extractedData.bmi;
            const bmiNum = typeof bmi === 'string' ? parseFloat(bmi.match(/[\d.]+/)?.[0] || "0") : bmi;
            integratedData.patient_info.bmi = bmiNum;
          }
          
          // 提取体重变化
          if (extractedData.体重下降 || extractedData.体重变化) {
            const weightLoss = extractedData.体重下降 || extractedData.体重变化;
            integratedData.patient_info.weight_loss_percentage = weightLoss;
          }
        }
      } else if (documentType.includes("血常规")) {
        // 处理血常规数据
        if (extractedData && typeof extractedData === 'object') {
          Object.entries(extractedData).forEach(([key, value]) => {
            if (key === "检查日期" || key === "结论") return;
            
            if (typeof value === 'string' && value.match(/[\d.]+/)) {
              const match = value.match(/([\d.]+)\s*([a-zA-Z/^]+)?/);
              if (match) {
                integratedData.lab_results.complete_blood_count.push({
                  name: key,
                  value: match[1],
                  unit: match[2] || "",
                  interpretation: value.includes("↑") ? "↑" : value.includes("↓") ? "↓" : ""
                });
              }
            }
          });
        }
      }
      
      // 处理通用的integrated_data（如果存在）
      if (result.integrated_data) {
        // 合并患者信息
        if (result.integrated_data.patient_info) {
          Object.assign(integratedData.patient_info, result.integrated_data.patient_info);
        }
        
        // 合并诊断信息
        if (result.integrated_data.diagnoses) {
          integratedData.diagnoses.push(...result.integrated_data.diagnoses);
        }
        
        // 合并实验室结果
        if (result.integrated_data.lab_results) {
          if (result.integrated_data.lab_results.biochemistry) {
            integratedData.lab_results.biochemistry.push(...result.integrated_data.lab_results.biochemistry);
          }
          if (result.integrated_data.lab_results.complete_blood_count) {
            integratedData.lab_results.complete_blood_count.push(...result.integrated_data.lab_results.complete_blood_count);
          }
        }
        
        // 合并NRS2002评分
        if (result.integrated_data.NRS2002_score) {
          integratedData.consultation_record.NRS2002_score = result.integrated_data.NRS2002_score;
        }
      }
    });
    
    // 设置到患者数据输入框
    setPatientData(JSON.stringify(integratedData, null, 2));
    setIsIntegrating(false);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setAssessmentResult("");
    try {
      let parsedData;
      try {
        parsedData = JSON.parse(patientData);
      } catch (error) {
        if (error instanceof Error) {
          setAssessmentResult(`JSON格式无效: ${error.message}`);
        } else {
          setAssessmentResult("JSON格式无效");
        }
        setIsLoading(false);
        return;
      }

      const res = await fetch("/api/assessment", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsedData),
      });

      if (!res.ok) {
        throw new Error("评估请求失败");
      }

      const result = await res.json();
      setAssessmentResult(result);
    } catch (error) {
      if (error instanceof Error) {
        setAssessmentResult(`发生错误: ${error.message}`);
      } else {
        setAssessmentResult("发生未知错误");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (assessmentResult) {
      let textToCopy = "";
      
      // 如果assessmentResult是对象，提取报告文本
      if (typeof assessmentResult === 'object' && assessmentResult.report) {
        textToCopy = assessmentResult.report;
      } 
      // 如果有错误，显示错误信息
      else if (typeof assessmentResult === 'object' && assessmentResult.error) {
        textToCopy = `评估出错: ${assessmentResult.error}`;
      }
      // 如果是字符串，直接使用
      else if (typeof assessmentResult === 'string') {
        textToCopy = assessmentResult;
      }
      // 其他情况，转换为JSON格式
      else {
        textToCopy = JSON.stringify(assessmentResult, null, 2);
      }
      
      navigator.clipboard.writeText(textToCopy).then(() => {
        setCopySuccess("已成功复制到剪贴板!");
        setTimeout(() => setCopySuccess(""), 2000);
      }, () => {
        setCopySuccess("复制失败。");
        setTimeout(() => setCopySuccess(""), 2000);
      });
    }
  };

  // 计算识别进度
  const recognitionProgress = imageRecognitionResults.length > 0 
    ? {
        total: imageRecognitionResults.length,
        completed: imageRecognitionResults.filter(r => r.status === "success" || r.status === "error").length,
        successful: imageRecognitionResults.filter(r => r.status === "success").length,
        failed: imageRecognitionResults.filter(r => r.status === "error").length
      }
    : null;

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50">
      <div className="w-full max-w-6xl">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          智能营养评估
        </h1>

        {/* 输入模式选择 */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex rounded-md shadow-sm" role="group">
            <button
              type="button"
              onClick={() => setInputMode("json")}
              className={`px-4 py-2 text-sm font-medium rounded-l-lg ${
                inputMode === "json"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              } border border-gray-200`}
            >
              JSON输入
            </button>
            <button
              type="button"
              onClick={() => setInputMode("image")}
              className={`px-4 py-2 text-sm font-medium rounded-r-lg ${
                inputMode === "image"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50"
              } border border-gray-200`}
            >
              图像识别
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="flex flex-col">
            {inputMode === "image" && (
              <div className="mb-4">
                <label className="mb-2 font-semibold text-gray-700 block">
                  上传医疗文书图片
                </label>
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="mb-2 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
                />
                
                {uploadedImages.length > 0 && (
                  <div className="mt-4">
                    <div className="flex justify-between items-center mb-2">
                      <div className="text-sm text-gray-600">
                        已选择 {uploadedImages.length} 个文件
                        {recognitionProgress && (
                          <span className="ml-2">
                            (识别进度: {recognitionProgress.completed}/{recognitionProgress.total})
                          </span>
                        )}
                      </div>
                      <button
                        onClick={handleBatchRecognition}
                        className="px-3 py-1 bg-green-600 text-white text-sm font-semibold rounded-md hover:bg-green-700"
                      >
                        开始识别
                      </button>
                    </div>
                    
                    {/* 识别进度和结果 */}
                    <div className="space-y-2 max-h-60 overflow-y-auto border border-gray-200 rounded-md p-2">
                      {imageRecognitionResults.map((result, index) => (
                        <div key={result.id} className="border border-gray-200 rounded p-2">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">{result.fileName}</span>
                            <div className="flex items-center gap-2">
                              {result.status === "pending" && (
                                <span className="text-gray-500 text-xs">待处理</span>
                              )}
                              {result.status === "processing" && (
                                <span className="text-blue-500 text-xs">识别中...</span>
                              )}
                              {result.status === "success" && (
                                <span className="text-green-500 text-xs">✓ 成功</span>
                              )}
                              {result.status === "error" && (
                                <>
                                  <span className="text-red-500 text-xs">✗ 失败</span>
                                  <button
                                    onClick={() => retrySingleImage(result.id)}
                                    className="px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
                                  >
                                    重试
                                  </button>
                                </>
                              )}
                            </div>
                          </div>
                          
                          {/* 显示识别结果预览 */}
                          {result.status === "success" && result.result && (
                            <div className="mt-2 text-xs text-gray-600">
                              <details>
                                <summary className="cursor-pointer">查看识别结果</summary>
                                <pre className="mt-1 p-2 bg-gray-100 rounded overflow-x-auto">
                                  {JSON.stringify(result.result.extracted_data || result.result, null, 2)}
                                </pre>
                              </details>
                            </div>
                          )}
                          
                          {result.status === "error" && result.error && (
                            <div className="mt-1 text-xs text-red-600">
                              错误: {result.error}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                    
                    {/* 整合按钮 */}
                    {recognitionProgress && recognitionProgress.successful > 0 && (
                      <button
                        onClick={handleIntegrateResults}
                        disabled={isIntegrating}
                        className="mt-4 w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 disabled:bg-gray-400"
                      >
                        {isIntegrating ? "整合中..." : `整合数据 (${recognitionProgress.successful} 个成功结果)`}
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}

            <label htmlFor="patientData" className="mb-2 font-semibold text-gray-700">
              患者信息 (JSON格式)
              {inputMode === "image" && patientData && (
                <span className="text-sm text-green-600 ml-2">
                  (数据已整合，请检查并编辑)
                </span>
              )}
            </label>
            <textarea
              id="patientData"
              rows={20}
              className="p-4 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition font-mono text-sm"
              placeholder="在此处粘贴患者的JSON数据..."
              value={patientData}
              onChange={(e) => setPatientData(e.target.value)}
            />
            <button
              onClick={handleSubmit}
              disabled={isLoading || !patientData}
              className="mt-4 px-6 py-3 bg-blue-600 text-white font-semibold rounded-md shadow-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? "评估中..." : "开始评估"}
            </button>
          </div>

          <div className="flex flex-col">
            <label htmlFor="assessmentResult" className="mb-2 font-semibold text-gray-700">
              评估报告
            </label>
            <div
              id="assessmentResult"
              className="p-4 border border-gray-300 rounded-md bg-white shadow-sm h-full min-h-[300px]"
            >
              <ReportDisplay result={assessmentResult} />
            </div>
            {assessmentResult && (
              <div className="mt-4 flex justify-between items-center">
                <button
                  onClick={copyToClipboard}
                  className="px-4 py-2 bg-gray-600 text-white font-semibold rounded-md shadow-md hover:bg-gray-700 transition-colors"
                >
                  复制报告
                </button>
                {copySuccess && <span className="text-green-500">{copySuccess}</span>}
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}