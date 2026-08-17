# -*- coding: utf-8 -*-
"""用透明 logo 生成新 favicon.ico（带圆角浅色底，多尺寸）"""
from PIL import Image, ImageDraw

LOGO = r'C:\Users\admin\DSH\ruoyi\src\assets\logo\logo.png'
OUT = r'C:\Users\admin\DSH\ruoyi\public\favicon.ico'

logo = Image.open(LOGO).convert('RGBA')

def make(size):
    # 圆角浅色底
    bg = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    r = size * 0.22
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=(255, 255, 255, 255))
    # logo 留边 14% 居中
    pad = int(size * 0.14)
    l = logo.resize((size - pad * 2, size - pad * 2), Image.LANCZOS)
    bg.alpha_composite(l, (pad, pad))
    return bg

sizes = [16, 24, 32, 48, 64, 128]
imgs = [make(s) for s in sizes]
imgs[0].save(OUT, format='ICO', sizes=[(s, s) for s in sizes])
print('已生成 favicon.ico:', OUT)
# 也输出一个 png 备用
make(64).save(r'C:\Users\admin\DSH\ruoyi\public\favicon.png')
print('已生成 favicon.png')
