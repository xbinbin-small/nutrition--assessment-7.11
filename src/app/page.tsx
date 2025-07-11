"use client";

import { useState } from "react";
import ReportDisplay from "@/components/ReportDisplay";

export default function Home() {
  const [patientData, setPatientData] = useState("");
  const [assessmentResult, setAssessmentResult] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState("");

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
      navigator.clipboard.writeText(assessmentResult).then(() => {
        setCopySuccess("已成功复制到剪贴板!");
        setTimeout(() => setCopySuccess(""), 2000);
      }, () => {
        setCopySuccess("复制失败。");
        setTimeout(() => setCopySuccess(""), 2000);
      });
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="w-full max-w-4xl">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          智能营养评估
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="flex flex-col">
            <label htmlFor="patientData" className="mb-2 font-semibold text-gray-700">
              患者信息 (JSON格式)
            </label>
            <textarea
              id="patientData"
              rows={20}
              className="p-4 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
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