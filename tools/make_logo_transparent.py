# -*- coding: utf-8 -*-
"""huahualogo.png 白底 → 透明背景，输出 256px 透明 PNG"""
from PIL import Image

SRC = r'C:\Users\admin\Pictures\huahualogo.png'
OUT = r'C:\Users\admin\DSH\ruoyi\src\assets\logo\logo.png'

img = Image.open(SRC).convert('RGB')
img = img.resize((256, 256), Image.LANCZOS)

# 亮度抠图：亮(白) → 透明；暗(内容) → 不透明；中间渐变抗锯齿
lum = img.convert('L')
px = lum.load()
alpha = Image.new('L', img.size, 0)
apx = alpha.load()
TH_HI = 235   # 亮度高于此 → 全透明
TH_LO = 190   # 亮度低于此 → 全不透明
for y in range(img.size[1]):
    for x in range(img.size[0]):
        v = px[x, y]
        if v >= TH_HI:
            a = 0
        elif v <= TH_LO:
            a = 255
        else:
            a = int((TH_HI - v) / (TH_HI - TH_LO) * 255)
        apx[x, y] = a

rgba = img.convert('RGBA')
rgba.putalpha(alpha)

# 去白边：对半透明边缘做轻微收缩（可选，保持简单）
rgba.save(OUT)
print('已输出:', OUT)
a = rgba.getchannel('A')
print('alpha 范围:', a.getextrema(), '透明像素占比: %.1f%%' % (sum(1 for v in a.getdata() if v < 30) / (256*256) * 100))
