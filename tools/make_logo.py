# -*- coding: utf-8 -*-
"""生成站点 Logo：渐变圆角方块 + 白色“刷”字"""
from PIL import Image, ImageDraw, ImageFont

SIZE = 256
img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 圆角矩形 + 垂直渐变（深蓝 -> 亮蓝）
radius = 56
mask = Image.new('L', (SIZE, SIZE), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=radius, fill=255)

top = (46, 91, 255)      # #2E5BFF
bottom = (91, 164, 255)  # #5BA4FF
for y in range(SIZE):
    t = y / (SIZE - 1)
    color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
    d.line([(0, y), (SIZE, y)], fill=color)

img.putalpha(mask)

# 白色“刷”字
try:
    font = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 150)
except Exception:
    font = ImageFont.load_default()
txt = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)
bbox = td.textbbox((0, 0), '刷', font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
td.text(((SIZE - tw) / 2 - bbox[0], (SIZE - th) / 2 - bbox[1] - 4), '刷',
        font=font, fill=(255, 255, 255, 255))
img = Image.alpha_composite(img, txt)

out = r'C:\Users\admin\DSH\ruoyi\src\assets\logo\logo.png'
img.save(out)
print('saved', out)
