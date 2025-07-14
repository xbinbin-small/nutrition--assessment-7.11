// 测试图片上传页面
export default function TestUpload() {
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    console.log('Selected file:', file.name, file.size, file.type);
    
    const formData = new FormData();
    formData.append('image', file);
    
    // 打印FormData内容
    for (const [key, value] of formData.entries()) {
      console.log('FormData entry:', key, value);
    }
    
    try {
      const response = await fetch('/api/recognize-single-image', {
        method: 'POST',
        body: formData,
      });
      
      const text = await response.text();
      console.log('Response status:', response.status);
      console.log('Response text:', text);
      
      if (response.ok) {
        const result = JSON.parse(text);
        console.log('Success:', result);
      } else {
        console.error('Error response:', text);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>图片上传测试</h1>
      <input 
        type="file" 
        accept="image/*" 
        onChange={handleUpload}
      />
      <p>请打开浏览器控制台查看详细日志</p>
    </div>
  );
}