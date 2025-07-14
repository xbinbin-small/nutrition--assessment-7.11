#!/usr/bin/env python3
"""
创建测试图像用于验证识别功能
"""

import base64
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_image(text_content, filename):
    """创建一个包含文本的测试图像"""
    # 创建白色背景图像
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        font = ImageFont.load_default()
    
    # 绘制文本
    y_position = 50
    for line in text_content.split('\n'):
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 40
    
    # 保存图像
    img.save(filename)
    print(f"已创建测试图像: {filename}")

# 创建测试图像1 - 生化检查报告
test1_content = """生化检查报告

检查日期: 2024-01-15

检查项目:
白蛋白: 34.3 g/L ↓
C-反应蛋白: 292.8 mg/L ↑
肌酐: 129.2 umol/L
尿素氮: 7.8 mmol/L
谷丙转氨酶: 45 U/L
谷草转氨酶: 38 U/L

结论: 白蛋白降低，炎症指标升高
"""

# 创建测试图像2 - 营养评估
test2_content = """营养风险筛查评估表

患者姓名: 测试患者
评估日期: 2024-01-15

NRS2002评分: 4分

营养状况评分:
- 体重下降 >5% (3个月内): 2分
- 进食量减少 >50%: 1分

疾病严重程度: 1分

总分: 4分
结论: 存在营养风险，需要营养干预
"""

# 创建测试图像3 - 人体测量
test3_content = """人体测量记录

测量日期: 2024-01-15

身高: 165 cm
体重: 55 kg
BMI: 20.2 kg/m²

上臂围: 24 cm
小腿围: 32 cm

体重变化:
- 1个月前: 58 kg
- 3个月前: 60 kg
- 体重下降: 8.3%
"""

# 创建测试图像
create_test_image(test1_content, "test_biochem.png")
create_test_image(test2_content, "test_nutrition.png")
create_test_image(test3_content, "test_anthropometry.png")

print("\n测试图像创建完成！")
print("请在浏览器中上传这些图像进行测试。")