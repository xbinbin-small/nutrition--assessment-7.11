'use client';

import React, { useState } from 'react';

interface LabItem {
  name: string;
  value: string;
  unit: string;
  interpretation: string;
}

interface StructuredFormData {
  patientInfo: {
    name: string;
    gender: string;
    age: string;
    height: string;
    weight: string;
  };
  chiefComplaint: string;
  presentIllness: string;
  pastHistory: string;
  physicalExam: {
    temperature: string;
    bloodPressure: string;
    pulse: string;
    respiration: string;
    general: string;
    abdomen: string;
  };
  bloodRoutine: LabItem[];
  biochemistry: LabItem[];
  nrs2002Score: string;
  diagnosis: string[];
  treatmentPlan: string;
}

interface StructuredTextFormProps {
  onSubmit: (formattedText: string) => void;
  isProcessing: boolean;
}

const StructuredTextForm: React.FC<StructuredTextFormProps> = ({ onSubmit, isProcessing }) => {
  const [formData, setFormData] = useState<StructuredFormData>({
    patientInfo: {
      name: '',
      gender: '男',
      age: '',
      height: '',
      weight: ''
    },
    chiefComplaint: '',
    presentIllness: '',
    pastHistory: '',
    physicalExam: {
      temperature: '',
      bloodPressure: '',
      pulse: '',
      respiration: '',
      general: '',
      abdomen: ''
    },
    bloodRoutine: [
      { name: '白细胞计数', value: '', unit: '×10^9/L', interpretation: '正常' },
      { name: '红细胞计数', value: '', unit: '×10^12/L', interpretation: '正常' },
      { name: '血红蛋白', value: '', unit: 'g/L', interpretation: '正常' },
      { name: '血小板计数', value: '', unit: '×10^9/L', interpretation: '正常' }
    ],
    biochemistry: [
      { name: '血清白蛋白', value: '', unit: 'g/L', interpretation: '正常' },
      { name: '总蛋白', value: '', unit: 'g/L', interpretation: '正常' },
      { name: '血糖', value: '', unit: 'mmol/L', interpretation: '正常' },
      { name: '总胆固醇', value: '', unit: 'mmol/L', interpretation: '正常' },
      { name: '甘油三酯', value: '', unit: 'mmol/L', interpretation: '正常' },
      { name: '钠', value: '', unit: 'mmol/L', interpretation: '正常' },
      { name: '钾', value: '', unit: 'mmol/L', interpretation: '正常' },
      { name: '氯', value: '', unit: 'mmol/L', interpretation: '正常' }
    ],
    nrs2002Score: '',
    diagnosis: [''],
    treatmentPlan: ''
  });

  const formatToText = (): string => {
    const { patientInfo, chiefComplaint, presentIllness, pastHistory, physicalExam, bloodRoutine, biochemistry, nrs2002Score, diagnosis, treatmentPlan } = formData;

    // 计算BMI
    const height = parseFloat(patientInfo.height);
    const weight = parseFloat(patientInfo.weight);
    const bmi = height && weight ? (weight / Math.pow(height / 100, 2)).toFixed(1) : '';

    let text = `患者基本信息：
姓名：${patientInfo.name}
性别：${patientInfo.gender}
年龄：${patientInfo.age}岁
身高：${patientInfo.height}cm
体重：${patientInfo.weight}kg
BMI：${bmi}

主诉：
${chiefComplaint}

现病史：
${presentIllness}

既往史：
${pastHistory}

体格检查：
体温：${physicalExam.temperature}℃
血压：${physicalExam.bloodPressure}mmHg
脉搏：${physicalExam.pulse}次/分
呼吸：${physicalExam.respiration}次/分
${physicalExam.general}
${physicalExam.abdomen}

实验室检查：

血常规：
${bloodRoutine.map(item => `${item.name}：${item.value}${item.unit} ${item.interpretation !== '正常' ? item.interpretation : ''}`).join('\n')}

生化检查：
${biochemistry.map(item => `${item.name}：${item.value}${item.unit} ${item.interpretation !== '正常' ? item.interpretation : ''}`).join('\n')}

营养评估：
NRS2002评分：${nrs2002Score}分

初步诊断：
${diagnosis.filter(d => d.trim()).map((d, i) => `${i + 1}. ${d}`).join('\n')}

治疗计划：
${treatmentPlan}
`;

    return text;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formattedText = formatToText();
    onSubmit(formattedText);
  };

  const updatePatientInfo = (field: keyof typeof formData.patientInfo, value: string) => {
    setFormData(prev => ({
      ...prev,
      patientInfo: { ...prev.patientInfo, [field]: value }
    }));
  };

  const updatePhysicalExam = (field: keyof typeof formData.physicalExam, value: string) => {
    setFormData(prev => ({
      ...prev,
      physicalExam: { ...prev.physicalExam, [field]: value }
    }));
  };

  const updateLabItem = (category: 'bloodRoutine' | 'biochemistry', index: number, field: keyof LabItem, value: string) => {
    setFormData(prev => ({
      ...prev,
      [category]: prev[category].map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const updateDiagnosis = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      diagnosis: prev.diagnosis.map((d, i) => i === index ? value : d)
    }));
  };

  const addDiagnosis = () => {
    setFormData(prev => ({
      ...prev,
      diagnosis: [...prev.diagnosis, '']
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 患者基本信息 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">患者基本信息</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
            <input
              type="text"
              required
              value={formData.patientInfo.name}
              onChange={(e) => updatePatientInfo('name', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="请输入患者姓名"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">性别 *</label>
            <select
              required
              value={formData.patientInfo.gender}
              onChange={(e) => updatePatientInfo('gender', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">年龄 *</label>
            <input
              type="number"
              required
              value={formData.patientInfo.age}
              onChange={(e) => updatePatientInfo('age', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="岁"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">身高 (cm) *</label>
            <input
              type="number"
              required
              value={formData.patientInfo.height}
              onChange={(e) => updatePatientInfo('height', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="cm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">体重 (kg) *</label>
            <input
              type="number"
              required
              step="0.1"
              value={formData.patientInfo.weight}
              onChange={(e) => updatePatientInfo('weight', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="kg"
            />
          </div>
        </div>
      </div>

      {/* 病史信息 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">病史信息</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">主诉 *</label>
            <textarea
              required
              value={formData.chiefComplaint}
              onChange={(e) => setFormData(prev => ({ ...prev, chiefComplaint: e.target.value }))}
              className="w-full px-3 py-2 border rounded-md"
              rows={2}
              placeholder="患者因...入院"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">现病史 *</label>
            <textarea
              required
              value={formData.presentIllness}
              onChange={(e) => setFormData(prev => ({ ...prev, presentIllness: e.target.value }))}
              className="w-full px-3 py-2 border rounded-md"
              rows={4}
              placeholder="患者...前无明显诱因出现..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">既往史</label>
            <textarea
              value={formData.pastHistory}
              onChange={(e) => setFormData(prev => ({ ...prev, pastHistory: e.target.value }))}
              className="w-full px-3 py-2 border rounded-md"
              rows={3}
              placeholder="高血压病史、糖尿病病史等"
            />
          </div>
        </div>
      </div>

      {/* 体格检查 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">体格检查</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">体温 (℃)</label>
            <input
              type="number"
              step="0.1"
              value={formData.physicalExam.temperature}
              onChange={(e) => updatePhysicalExam('temperature', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="36.5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">血压 (mmHg)</label>
            <input
              type="text"
              value={formData.physicalExam.bloodPressure}
              onChange={(e) => updatePhysicalExam('bloodPressure', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="120/80"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">脉搏 (次/分)</label>
            <input
              type="number"
              value={formData.physicalExam.pulse}
              onChange={(e) => updatePhysicalExam('pulse', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="72"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">呼吸 (次/分)</label>
            <input
              type="number"
              value={formData.physicalExam.respiration}
              onChange={(e) => updatePhysicalExam('respiration', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="18"
            />
          </div>
        </div>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">一般情况</label>
            <input
              type="text"
              value={formData.physicalExam.general}
              onChange={(e) => updatePhysicalExam('general', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="神志清楚，精神差，营养状况等"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">腹部检查</label>
            <input
              type="text"
              value={formData.physicalExam.abdomen}
              onChange={(e) => updatePhysicalExam('abdomen', e.target.value)}
              className="w-full px-3 py-2 border rounded-md"
              placeholder="腹部平软，无压痛等"
            />
          </div>
        </div>
      </div>

      {/* 血常规 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">血常规</h3>
        <div className="space-y-3">
          {formData.bloodRoutine.map((item, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">{item.name}</label>
              </div>
              <div>
                <input
                  type="text"
                  value={item.value}
                  onChange={(e) => updateLabItem('bloodRoutine', index, 'value', e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="数值"
                />
              </div>
              <div>
                <input
                  type="text"
                  value={item.unit}
                  disabled
                  className="w-full px-3 py-2 border rounded-md bg-gray-50"
                />
              </div>
              <div>
                <select
                  value={item.interpretation}
                  onChange={(e) => updateLabItem('bloodRoutine', index, 'interpretation', e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="正常">正常</option>
                  <option value="↑">↑ 偏高</option>
                  <option value="↓">↓ 偏低</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 生化检查 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">生化检查</h3>
        <div className="space-y-3">
          {formData.biochemistry.map((item, index) => (
            <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">{item.name}</label>
              </div>
              <div>
                <input
                  type="text"
                  value={item.value}
                  onChange={(e) => updateLabItem('biochemistry', index, 'value', e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="数值"
                />
              </div>
              <div>
                <input
                  type="text"
                  value={item.unit}
                  disabled
                  className="w-full px-3 py-2 border rounded-md bg-gray-50"
                />
              </div>
              <div>
                <select
                  value={item.interpretation}
                  onChange={(e) => updateLabItem('biochemistry', index, 'interpretation', e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="正常">正常</option>
                  <option value="↑">↑ 偏高</option>
                  <option value="↓">↓ 偏低</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 营养评估 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">营养评估</h3>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">NRS2002评分</label>
          <input
            type="number"
            value={formData.nrs2002Score}
            onChange={(e) => setFormData(prev => ({ ...prev, nrs2002Score: e.target.value }))}
            className="w-full md:w-48 px-3 py-2 border rounded-md"
            placeholder="0-7分"
            min="0"
            max="7"
          />
          <p className="text-xs text-gray-500 mt-1">≥3分提示有营养风险</p>
        </div>
      </div>

      {/* 初步诊断 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">初步诊断</h3>
        <div className="space-y-2">
          {formData.diagnosis.map((diag, index) => (
            <div key={index} className="flex gap-2">
              <span className="text-gray-600 pt-2">{index + 1}.</span>
              <input
                type="text"
                value={diag}
                onChange={(e) => updateDiagnosis(index, e.target.value)}
                className="flex-1 px-3 py-2 border rounded-md"
                placeholder="诊断名称"
              />
            </div>
          ))}
          <button
            type="button"
            onClick={addDiagnosis}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            + 添加诊断
          </button>
        </div>
      </div>

      {/* 治疗计划 */}
      <div className="bg-white p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">治疗计划</h3>
        <textarea
          value={formData.treatmentPlan}
          onChange={(e) => setFormData(prev => ({ ...prev, treatmentPlan: e.target.value }))}
          className="w-full px-3 py-2 border rounded-md"
          rows={6}
          placeholder="1. 完善检查&#10;2. 营养支持治疗&#10;3. 对症治疗&#10;..."
        />
      </div>

      {/* 提交按钮 */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isProcessing}
          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
        >
          {isProcessing ? '处理中...' : '提交并生成评估'}
        </button>
      </div>
    </form>
  );
};

export default StructuredTextForm;
