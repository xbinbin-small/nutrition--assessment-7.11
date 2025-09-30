import React from 'react';

interface ReportDisplayProps {
  result: any;
}

const ReportDisplay: React.FC<ReportDisplayProps> = ({ result }) => {
  if (!result) {
    return <p className="text-gray-500">评估结果将显示在这里...</p>;
  }

  if (result.error) {
    return (
      <div className="text-red-500">
        <p className="font-bold">评估出错:</p>
        <pre className="whitespace-pre-wrap text-sm mt-2">
          {JSON.stringify(result, null, 2)}
        </pre>
      </div>
    );
  }

  const { report, validation_results } = result;

  // The report is now expected to have bolded titles.
  // We'll split by newlines and render accordingly.
  const reportLines = (report || '').split('\n').filter((line: string) => line.trim() !== '');

  return (
    <div className="space-y-4">
      {reportLines.map((line: string, index: number) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return (
            <h3 key={index} className="text-xl font-bold text-gray-800 pt-2">
              {line.replace(/\*\*/g, '')}
            </h3>
          );
        }
        return (
          <p key={index} className="text-gray-700 whitespace-pre-wrap">
            {line}
          </p>
        );
      })}

      {validation_results && (validation_results.missing_fields.length > 0 || validation_results.warnings.length > 0) && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-300 rounded-md">
          <h4 className="font-bold text-yellow-800">数据验证警告</h4>
          {validation_results.missing_fields.length > 0 && (
            <p className="text-sm text-yellow-700 mt-2">
              <strong>缺失字段:</strong> {validation_results.missing_fields.join(', ')}
            </p>
          )}
          {validation_results.warnings.length > 0 && (
             <p className="text-sm text-yellow-700 mt-2">
              <strong>警告:</strong> {validation_results.warnings.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ReportDisplay;