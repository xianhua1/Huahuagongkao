# -*- coding: utf-8 -*-
"""生成资料文档教学配图 → ruoyi/public/docs/"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r'C:\Users\admin\DSH\ruoyi\public\docs'
os.makedirs(OUT, exist_ok=True)
FONT = r'C:\Windows\Fonts\msyh.ttc'
FONT_B = r'C:\Windows\Fonts\msyhbd.ttc'

def f(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)

BLUE = (64, 158, 255)
DARK = (48, 65, 86)
GRAY = (120, 130, 140)
RED = (245, 108, 108)
GREEN = (103, 194, 58)
ORANGE = (230, 162, 60)
BG = (255, 255, 255)
LIGHT = (235, 244, 255)

def canvas(w, h):
    img = Image.new('RGB', (w, h), BG)
    return img, ImageDraw.Draw(img)

def text_c(d, xy, s, font, fill=DARK):
    x, y = xy
    w = d.textlength(s, font=font)
    d.text((x - w / 2, y), s, font=font, fill=fill)

def round_box(d, box, r=14, fill=LIGHT, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def arrow(d, p1, p2, color=BLUE, width=5):
    d.line([p1, p2], fill=color, width=width)
    import math
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    L = 16
    for da in (2.6, -2.6):
        x = p2[0] - L * math.cos(ang + da)
        y = p2[1] - L * math.sin(ang + da)
        d.line([p2, (x, y)], fill=color, width=width)

def title(d, img, text, sub=''):
    d.text((30, 22), text, font=f(30, True), fill=BLUE)
    if sub:
        d.text((30, 62), sub, font=f(17), fill=GRAY)

# ---------- 1 行程：相遇与追及 ----------
img, d = canvas(960, 620)
title(d, img, '行程问题两大模型：相遇 & 追及', '同一条直线上，两人一前一后或相向而行，用“速度之和 / 速度之差”来算时间')
# 相遇
y = 130
d.text((40, y), '① 相遇：两人相向而行（面对面）', font=f(22, True), fill=DARK)
arrow(d, (120, y + 75), (420, y + 75))
arrow(d, (840, y + 75), (540, y + 75))
text_c(d, (270, y + 90), '甲', f(20, True), BLUE)
text_c(d, (690, y + 90), '乙', f(20, True), BLUE)
d.line([(60, y + 75), (900, y + 75)], fill=GRAY, width=3)
text_c(d, (480, y + 55), '相遇', f(22, True), RED)
text_c(d, (480, y + 118), '相遇时间 = 总路程 ÷（甲速 + 乙速）', f(20, True), DARK)
# 追及
y2 = 300
d.text((40, y2), '② 追及：两人同向而行（一快一慢，快的追慢的）', font=f(22, True), fill=DARK)
arrow(d, (120, y2 + 78), (330, y2 + 78))
arrow(d, (700, y2 + 78), (880, y2 + 78))
text_c(d, (220, y2 + 92), '甲(快)', f(20, True), BLUE)
text_c(d, (790, y2 + 92), '乙(慢)', f(20, True), ORANGE)
d.line([(60, y2 + 78), (900, y2 + 78)], fill=GRAY, width=3)
d.line([(330, y2 + 58), (330, y2 + 100)], fill=RED, width=3)
text_c(d, (330, y2 + 112), '路程差', f(18, True), RED)
text_c(d, (480, y2 + 55), '追上', f(22, True), GREEN)
text_c(d, (480, y2 + 118), '追及时间 = 路程差 ÷（快速 − 慢速）', f(20, True), DARK)
d.text((40, 520), '记住：相遇看“和”，追及看“差”——速度相加或相减，时间自然就出来了。', font=f(18), fill=GRAY)
img.save(os.path.join(OUT, 'sl-xingcheng.png'))

# ---------- 2 容斥（文氏图） ----------
img, d = canvas(960, 560)
title(d, img, '容斥问题：先画图，再列式', '50 名学生：物理做对 40 人，化学做对 31 人，两科都做错 4 人 —— 两科都做对几人？')
d.ellipse([(230, 150), (560, 440)], fill=(214, 233, 255), outline=BLUE, width=3)
d.ellipse([(430, 150), (760, 440)], fill=(255, 236, 214), outline=ORANGE, width=3)
d.text((280, 270), '物理', font=f(26, True), fill=BLUE)
d.text((660, 270), '化学', font=f(26, True), fill=ORANGE)
text_c(d, (350, 210), '15', f(26, True), DARK)
text_c(d, (495, 210), '25', f(30, True), RED)
text_c(d, (640, 210), '6', f(26, True), DARK)
text_c(d, (495, 320), '两科都对', f(18, True), RED)
d.text((120, 460), '只对物理 15  +  都对 25  +  只对化学 6  +  都错 4  =  50 人', font=f(20, True), fill=DARK)
d.text((120, 505), '公式：都做对 = 物理对 + 化学对 + 都错 − 总人数 = 40 + 31 + 4 − 50 = 25', font=f(20, True), fill=BLUE)
img.save(os.path.join(OUT, 'sl-rongchi.png'))

# ---------- 3 工程问题公式三角 ----------
img, d = canvas(960, 560)
title(d, img, '工程问题：总量 = 效率 × 时间', '把“工作量”看成一块蛋糕，效率是“每天吃多少”，时间是“吃几天”')
# 三角形
d.line([(480, 120), (260, 360)], fill=BLUE, width=5)
d.line([(480, 120), (700, 360)], fill=BLUE, width=5)
d.line([(260, 360), (700, 360)], fill=BLUE, width=5)
text_c(d, (480, 145), '工作总量', f(30, True), RED)
text_c(d, (355, 330), '效率', f(26, True), DARK)
text_c(d, (605, 330), '时间', f(26, True), DARK)
text_c(d, (480, 265), '×', f(30, True), BLUE)
d.text((120, 400), '求总量 → 效率 × 时间；求效率 → 总量 ÷ 时间；求时间 → 总量 ÷ 效率', font=f(20, True), fill=DARK)
d.text((120, 445), '技巧：总量不好求时，直接“赋值”总量为 1 或最小公倍数（赋值法，最常用）', font=f(20, True), fill=BLUE)
d.text((120, 490), '例：甲 6 天干完，乙 12 天干完，两人合干 → 赋值总量 12，甲效率 2、乙效率 1，合干 12÷3=4 天', font=f(18), fill=GRAY)
img.save(os.path.join(OUT, 'sl-gongcheng.png'))

# ---------- 4 利润链条 ----------
img, d = canvas(960, 560)
title(d, img, '经济利润：钱是怎么“赚”出来的', '一条链看懂：进价 → 标价 → 售价 → 利润')
round_box(d, (70, 130, 250, 230), fill=LIGHT)
text_c(d, (160, 160), '进价', f(26, True), DARK)
text_c(d, (160, 200), '（成本）', f(18), GRAY)
arrow(d, (250, 180), (330, 180))
round_box(d, (330, 130, 510, 230), fill=LIGHT)
text_c(d, (420, 160), '标价', f(26, True), DARK)
text_c(d, (420, 200), '（原价）', f(18), GRAY)
arrow(d, (510, 180), (590, 180))
round_box(d, (590, 130, 770, 230), fill=LIGHT)
text_c(d, (680, 160), '售价', f(26, True), DARK)
text_c(d, (680, 200), '（打完折后）', f(18), GRAY)
arrow(d, (770, 180), (850, 180))
round_box(d, (850, 130, 930, 230), fill=(255, 236, 214))
text_c(d, (890, 180), '利润', f(24, True), ORANGE)
d.text((70, 270), '售价 = 标价 × 折扣（打八折就是 × 0.8）', font=f(20, True), fill=DARK)
d.text((70, 315), '利润 = 售价 − 进价；利润率 = 利润 ÷ 进价 × 100%', font=f(20, True), fill=DARK)
d.text((70, 360), '总利润 = 单件利润 × 数量（打折多卖几件，利润可能不变——经典考题）', font=f(20, True), fill=BLUE)
d.text((70, 405), '解题套路：把“利润相等 / 利润率相等”列成方程，设进价为未知数 X，一步到位', font=f(20, True), fill=RED)
img.save(os.path.join(OUT, 'sl-lirun.png'))

# ---------- 5 分步乘法 ----------
img, d = canvas(960, 480)
title(d, img, '排列组合入门：分步相乘、分类相加', '自助餐选餐：肉类 3 选 1，蔬菜 4 选 2，点心 4 选 1，一共多少种搭配？')
round_box(d, (80, 150, 280, 280), fill=LIGHT)
text_c(d, (180, 185), '选肉类', f(24, True), DARK)
text_c(d, (180, 230), '3 种中选 1', f(18), GRAY)
text_c(d, (180, 265), '= 3 种', f(22, True), BLUE)
arrow(d, (280, 215), (370, 215))
round_box(d, (370, 150, 600, 280), fill=LIGHT)
text_c(d, (485, 185), '选蔬菜', f(24, True), DARK)
text_c(d, (485, 230), '4 种中选 2', f(18), GRAY)
text_c(d, (485, 265), '= 6 种', f(22, True), BLUE)
arrow(d, (600, 215), (690, 215))
round_box(d, (690, 150, 890, 280), fill=LIGHT)
text_c(d, (790, 185), '选点心', f(24, True), DARK)
text_c(d, (790, 230), '4 种中选 1', f(18), GRAY)
text_c(d, (790, 265), '= 4 种', f(22, True), BLUE)
d.text((80, 330), '分步完成（缺一步都不行）→ 用乘法：3 × 6 × 4 = 72 种', font=f(24, True), fill=RED)
d.text((80, 380), '分类完成（几种情况任选其一）→ 用加法：情况1 + 情况2 + …', font=f(20, True), fill=DARK)
img.save(os.path.join(OUT, 'sl-pailie.png'))

# ---------- 6 图形推理：位置移动 ----------
img, d = canvas(960, 420)
title(d, img, '图形推理：位置移动规律', '三幅图中黑块每次顺时针平移一格，问号处应选哪幅？')
def grid(d, x0, y0, filled, size=150):
    for i in range(4):
        d.line([(x0, y0 + i * size / 3), (x0 + size, y0 + i * size / 3)], fill=GRAY, width=2)
        d.line([(x0 + i * size / 3, y0), (x0 + i * size / 3, y0 + size)], fill=GRAY, width=2)
    for (r, c) in filled:
        d.rectangle([(x0 + c * size / 3 + 4, y0 + r * size / 3 + 4),
                     (x0 + (c + 1) * size / 3 - 4, y0 + (r + 1) * size / 3 - 4)], fill=BLUE)
    return x0 + size, y0
y = 140
x = 110
x, _ = grid(d, x, y, [(0, 0)])
arrow(d, (x + 30, y + 75), (x + 110, y + 75))
x += 140
x, _ = grid(d, x, y, [(0, 1)])
arrow(d, (x + 30, y + 75), (x + 110, y + 75))
x += 140
x, _ = grid(d, x, y, [(0, 2)])
arrow(d, (x + 30, y + 75), (x + 110, y + 75))
x += 140
grid(d, x, y, [(1, 2)])
d.text((110, 340), '位置类口诀：先看“移动方向 + 步数”（顺时针/逆时针、每次几格），选项一眼排除', font=f(20, True), fill=BLUE)
d.text((110, 380), '真题里黑块常“按行/列/环形”移动，画箭头比空想快得多', font=f(18), fill=GRAY)
img.save(os.path.join(OUT, 'tx-weizhi.png'))

# ---------- 7 图形推理：对称 ----------
img, d = canvas(960, 420)
title(d, img, '图形推理：对称轴', '轴对称 = 沿一条直线对折能完全重合，这条线就是对称轴')
def tri(d, cx, cy, r):
    d.polygon([(cx, cy - r), (cx - r * 0.9, cy + r * 0.6), (cx + r * 0.9, cy + r * 0.6)], fill=LIGHT, outline=BLUE, width=3)
def axis(d, p1, p2):
    d.line([p1, p2], fill=RED, width=3)
tri(d, 220, 240, 95)
axis(d, (220, 110), (220, 370))
text_c(d, (220, 395), '等边三角形', f(18, True), DARK)
text_c(d, (220, 422), '3 条对称轴', f(16), RED)
d.rectangle([(400, 150), (580, 330)], fill=LIGHT, outline=BLUE, width=3)
axis(d, (490, 130), (490, 350))
axis(d, (380, 240), (600, 240))
text_c(d, (490, 395), '长方形', f(18, True), DARK)
text_c(d, (490, 422), '2 条对称轴', f(16), RED)
d.ellipse([(680, 150), (880, 330)], fill=LIGHT, outline=BLUE, width=3)
for ang in (0, 45, 90, 135):
    import math
    a = math.radians(ang)
    axis(d, (780 - 90 * math.cos(a), 240 - 90 * math.sin(a)), (780 + 90 * math.cos(a), 240 + 90 * math.sin(a)))
text_c(d, (780, 395), '圆', f(18, True), DARK)
text_c(d, (780, 422), '无数条对称轴', f(16), RED)
d.text((60, 40), '进阶：对称轴的数量、方向（横/竖/斜 45°）本身也是考点，比如“对称轴每次顺时针转 45°”', font=f(16), fill=GRAY)
img.save(os.path.join(OUT, 'tx-duichen.png'))

# ---------- 8 图形推理：笔画数 ----------
img, d = canvas(960, 480)
title(d, img, '图形推理：一笔画（奇点法）', '奇点 = 从这个点出发的线条数是“奇数”的交叉点/端点')
def shape(d, x0, y0, kind):
    w = 150
    if kind == 'ri':
        d.rectangle([(x0, y0), (x0 + w, y0 + w * 0.62)], outline=BLUE, width=3)
        d.line([(x0 + w / 2, y0), (x0 + w / 2, y0 + w * 0.62)], fill=BLUE, width=3)
        pts = [(x0 + w / 2, y0), (x0 + w / 2, y0 + w * 0.62)]
    else:
        d.rectangle([(x0, y0), (x0 + w, y0 + w * 0.62)], outline=BLUE, width=3)
        d.line([(x0 + w / 2, y0), (x0 + w / 2, y0 + w * 0.62)], fill=BLUE, width=3)
        d.line([(x0, y0 + w * 0.31), (x0 + w, y0 + w * 0.31)], fill=BLUE, width=3)
        pts = [(x0 + w / 2, y0), (x0 + w / 2, y0 + w * 0.62), (x0, y0 + w * 0.31), (x0 + w, y0 + w * 0.31)]
    for p in pts:
        d.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=RED)
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(255, 255, 255))
shape(d, 180, 150, 'ri')
text_c(d, (255, 290), '“日”字形', f(20, True), DARK)
text_c(d, (255, 322), '2 个奇点 → 一笔画成', f(18, True), GREEN)
shape(d, 560, 150, 'tian')
text_c(d, (635, 290), '“田”字形', f(20, True), DARK)
text_c(d, (635, 322), '4 个奇点 → 两笔画成', f(18, True), RED)
d.text((120, 360), '公式：笔画数 = 奇点数 ÷ 2（奇点数为 0 或 2 时可一笔画成）', font=f(22, True), fill=BLUE)
d.text((120, 410), '看到“日、田、五角星、连环圈”这些特征图形，优先想笔画数', font=f(18), fill=GRAY)
img.save(os.path.join(OUT, 'tx-bihua.png'))

# ---------- 9 资料分析：核心公式卡 ----------
img, d = canvas(960, 560)
title(d, img, '资料分析核心公式：一张图全记住', '现期（今年）←→ 基期（去年）之间，就靠“增长率”这座桥')
cards = [
    ('现期量', '现期 = 基期 × (1 + 增长率)', '今年 = 去年 × (1 + r)', BLUE),
    ('基期量', '基期 = 现期 ÷ (1 + 增长率)', '去年 = 今年 ÷ (1 + r)', GREEN),
    ('增长量', '增长量 = 现期 − 基期 = 基期 × r', '增长量 = 现期 × r ÷ (1 + r)', ORANGE),
    ('增长率', 'r = 增长量 ÷ 基期 × 100%', 'r = (现期 − 基期) ÷ 基期', RED),
]
for i, (t, f1, f2, c) in enumerate(cards):
    x0 = 60 + (i % 2) * 440
    y0 = 140 + (i // 2) * 180
    round_box(d, (x0, y0, x0 + 400, y0 + 150), fill=(255, 255, 255), outline=c, width=3)
    round_box(d, (x0 + 20, y0 + 18, x0 + 130, y0 + 62), fill=c)
    text_c(d, (x0 + 75, y0 + 30), t, f(20, True), (255, 255, 255))
    d.text((x0 + 22, y0 + 78), f1, font=f(19, True), fill=DARK)
    d.text((x0 + 22, y0 + 112), f2, font=f(17), fill=GRAY)
d.text((60, 510), '口诀：求去年（基期）一定“除”；求今年（现期）一定“乘”；增长率永远“÷基期”', font=f(20, True), fill=BLUE)
img.save(os.path.join(OUT, 'zl-gongshi.png'))

# ---------- 10 比重变化 ----------
img, d = canvas(960, 460)
title(d, img, '比重（占比）怎么变？只看“增速”', '比重 = 部分 ÷ 整体。分子分母都在涨，涨得快的占比就变大')
for i, (label, sub, color, up) in enumerate([('部分增速 > 整体增速', '比重 → 上升', GREEN, True), ('部分增速 < 整体增速', '比重 → 下降', RED, False), ('部分增速 = 整体增速', '比重 → 不变', GRAY, None)]):
    x0 = 70 + i * 300
    round_box(d, (x0, 140, x0 + 260, 260), fill=(255, 255, 255), outline=color, width=3)
    d.text((x0 + 20, 165), label, font=f(20, True), fill=DARK)
    if up is True:
        d.polygon([(x0 + 130, 200), (x0 + 108, 240), (x0 + 152, 240)], fill=color)
        d.text((x0 + 20, 250), sub, font=f(22, True), fill=color)
    elif up is False:
        d.polygon([(x0 + 130, 245), (x0 + 108, 205), (x0 + 152, 205)], fill=color)
        d.text((x0 + 20, 250), sub, font=f(22, True), fill=color)
    else:
        d.line([(x0 + 105, 220), (x0 + 155, 220)], fill=color, width=6)
        d.text((x0 + 20, 250), sub, font=f(22, True), fill=color)
d.text((70, 320), '例：某省 GDP 增长 10%，其中农业产值增长 15% → 农业占比上升', font=f(20, True), fill=DARK)
d.text((70, 365), '秒杀：两期比重差 ≈ 部分增速 − 整体增速（结果远小于增速差，真题可直接选“上升/下降 + 小数值”）', font=f(19, True), fill=BLUE)
img.save(os.path.join(OUT, 'zl-bizhong.png'))

# ---------- 11 百化分速记表 ----------
img, d = canvas(960, 620)
title(d, img, '百分数与分数互换（百化分）', '资料分析提速神器：看到 12.5% 直接想 1/8，除法变乘法')
vals = [(1, 2, '50%'), (1, 3, '33.3%'), (1, 4, '25%'), (1, 5, '20%'), (1, 6, '16.7%'), (1, 7, '14.3%'),
        (1, 8, '12.5%'), (1, 9, '11.1%'), (1, 10, '10%'), (1, 11, '9.1%'), (1, 12, '8.3%'), (1, 13, '7.7%'),
        (1, 14, '7.1%'), (1, 15, '6.7%'), (1, 16, '6.25%'), (1, 17, '5.9%'), (1, 18, '5.6%'), (1, 20, '5%')]
col_w = 210
x0, y0 = 60, 150
for i, (n, m, p) in enumerate(vals):
    r, c = divmod(i, 3)
    x = x0 + c * (col_w + 30)
    y = y0 + r * 62
    round_box(d, (x, y, x + col_w, y + 50), fill=(255, 255, 255), outline=BLUE, width=2)
    d.text((x + 16, y + 12), '%d/%d' % (n, m), font=f(20, True), fill=DARK)
    text_c(d, (x + 140, y + 13), p, f(20, True), RED)
    d.text((x + 130, y + 16), '≈', font=f(18), fill=GRAY)
d.text((60, 545), '用法：增长率 r 是这些分数时，增长量 = 现期 ÷ (分数分母 + 1)，一步口算', font=f(20, True), fill=BLUE)
d.text((60, 590), '重点记：1/2、1/3、1/4、1/5、1/6、1/8、1/10、1/12、1/20（其余考场现推）', font=f(18), fill=GRAY)
img.save(os.path.join(OUT, 'zl-baihuafen.png'))

# ---------- 12 朝代时间轴 ----------
img, d = canvas(960, 400)
title(d, img, '历史朝代时间轴（常识高频）', '“夏商与西周，东周分两段；春秋和战国，一统秦两汉…》')
y = 200
d.line([(60, y), (900, y)], fill=BLUE, width=4)
d.ellipse([(54, y - 8), (70, y + 8)], fill=BLUE)
d.ellipse([(894, y - 8), (910, y + 8)], fill=BLUE)
periods = [('夏', 75), ('商', 125), ('西周', 175), ('春秋战国', 240), ('秦', 315), ('汉', 365), ('三国两晋南北朝', 450), ('隋', 550), ('唐', 600), ('五代十国', 670), ('宋', 720), ('元', 790), ('明', 835), ('清', 880)]
for i, (name, x) in enumerate(periods):
    up = i % 2 == 0
    yy = y - 30 if up else y + 35
    d.line([(x, y), (x, yy)], fill=GRAY, width=2)
    text_c(d, (x, yy - 24 if up else yy + 4), name, f(17, True), DARK)
d.text((60, 300), '记法：按“统一—分裂—再统一”的节奏背，比死记顺序快得多', font=f(19, True), fill=BLUE)
d.text((60, 345), '高频考点：朝代更替顺序、每个朝代标志性事件（秦统一六国、汉丝绸之路、唐贞观之治、明清科举）', font=f(17), fill=GRAY)
img.save(os.path.join(OUT, 'cs-shidai.png'))

# ---------- 13 法律体系树 ----------
img, d = canvas(960, 520)
title(d, img, '法律常识框架：一图理清“部门法”', '常识考法律，不考条文细节，考“分类 + 基础概念”')
round_box(d, (360, 130, 600, 190), fill=BLUE)
text_c(d, (480, 150), '中国特色社会主义法律体系', f(22, True), (255, 255, 255))
text_c(d, (480, 178), '以宪法为统帅', f(15), (230, 240, 255))
branches = ['宪法\n（根本大法）', '刑法\n（犯罪与刑罚）', '民法\n（平等主体之间）', '行政法\n（官与民）', '经济法', '社会法\n（劳动保障）', '诉讼法\n（打官司程序）']
xs = [120, 245, 370, 495, 620, 745, 870]
for i, b in enumerate(branches):
    x = xs[i]
    d.line([(480, 195), (x, 235)], fill=GRAY, width=2)
    round_box(d, (x - 85, 235, x + 85, 305), fill=LIGHT, outline=BLUE, width=2)
    lines = b.split('\n')
    text_c(d, (x, 250), lines[0], f(17, True), DARK)
    if len(lines) > 1:
        text_c(d, (x, 278), lines[1], f(13), GRAY)
d.text((60, 360), '高频区分：', font=f(20, True), fill=RED)
d.text((165, 360), '罚款（行政）≠ 罚金（刑事）；拘役（刑事）≠ 拘留（行政）', font=f(20, True), fill=DARK)
d.text((60, 410), '“法”与“法规”层级：宪法 > 法律（全国人大） > 行政法规（国务院） > 地方性法规', font=f(19, True), fill=BLUE)
d.text((60, 455), '宪法考点：国家机构（人大、政府、法院、检察院的职权分工）、公民基本权利、宪法修正', font=f(17), fill=GRAY)
img.save(os.path.join(OUT, 'cs-falv.png'))

# ---------- 14 实验设计 ----------
img, d = canvas(960, 500)
title(d, img, '事业单位职测 · 实验设计：唯一变量', '实验设计题三步走：找自变量（你改什么）→ 找因变量（你看什么）→ 找对照组（什么都不改的那组）')
round_box(d, (110, 160, 330, 280), fill=LIGHT, outline=BLUE, width=3)
text_c(d, (220, 195), '实验组', f(24, True), BLUE)
text_c(d, (220, 235), '施加“自变量”', f(17), DARK)
text_c(d, (220, 262), '（如：施肥 A）', f(15), GRAY)
round_box(d, (630, 160, 850, 280), fill=(255, 236, 214), outline=ORANGE, width=3)
text_c(d, (740, 195), '对照组', f(24, True), ORANGE)
text_c(d, (740, 235), '不施加自变量', f(17), DARK)
text_c(d, (740, 262), '（如：不施肥）', f(15), GRAY)
arrow(d, (330, 220), (430, 220))
d.text((360, 205), '其余条件', font=f(17, True), fill=DARK)
d.text((360, 228), '完全相同', font=f(17, True), fill=RED)
arrow(d, (630, 220), (530, 220))
text_c(d, (480, 300), '比较两组的“因变量”（如：植株高度）', f(17, True), DARK)
d.text((110, 330), '为什么必须设对照组？没有对比，就说不清变化是“自变量”造成的，还是本来就会发生的', font=f(19, True), fill=BLUE)
d.text((110, 375), '控制变量：除了自变量，温度、光照、水分等必须相同，否则实验结果“说不清是谁的功劳”', font=f(19, True), fill=BLUE)
d.text((110, 420), '做题顺序：题干先标出自变量/因变量 → 选项逐条对照“唯一变量原则” → 排除多变量或无关项', font=f(18), fill=GRAY)
img.save(os.path.join(OUT, 'sy-design.png'))

# ---------- 15 翻译推理 ----------
img, d = canvas(960, 520)
title(d, img, '逻辑判断 · 翻译推理：箭头游戏', '把中文翻译成箭头，再按规则推——这是逻辑判断里最“送分”的题型')
round_box(d, (70, 140, 350, 230), fill=LIGHT, outline=BLUE, width=3)
d.text((95, 160), '如果 A，那么 B', font=f(22, True), fill=DARK)
text_c(d, (210, 205), 'A → B', f(26, True), BLUE)
d.text((95, 240), '肯前必肯后：有 A 一定有 B', font=f(16), fill=GRAY)
arrow(d, (350, 185), (440, 185))
round_box(d, (440, 140, 720, 230), fill=(255, 236, 214), outline=ORANGE, width=3)
d.text((465, 160), '逆否等价（最常用）', font=f(22, True), fill=DARK)
text_c(d, (580, 205), '非B → 非A', f(26, True), ORANGE)
d.text((465, 240), '没有 B 就一定没有 A', font=f(16), fill=GRAY)
d.text((70, 290), '两大坑（真题专挖）：', font=f(20, True), fill=RED)
d.text((300, 290), '肯后（有 B）推不出 A；否前（无 A）推不出无 B', font=f(20, True), fill=DARK)
d.text((70, 335), '口诀：肯前肯后、否后否前；肯后否前，一律不选', font=f(22, True), fill=BLUE)
d.text((70, 385), '“只有 A，才 B” → B → A（只有…才：后推前）', font=f(20, True), fill=DARK)
d.text((70, 430), '“除非 A，否则 B” → 非B → A（否一推一）', font=f(20, True), fill=DARK)
img.save(os.path.join(OUT, 'pd-luoji.png'))

# ---------- 16 言语文段结构 ----------
img, d = canvas(960, 620)
title(d, img, '言语 · 中心理解：先看结构，再找重点', '文段结构决定重点位置——转折之后、因果结论、对策句，往往是答案')
rows = [
    ('总分结构', '观点在开头，后面全是解释/举例 → 重点在第一句', BLUE, 0),
    ('分总结构', '前面铺陈，最后一句总结 → 重点在结尾', GREEN, 1),
    ('总分总', '首尾呼应，中间论证 → 重点在首尾', ORANGE, 2),
    ('并列结构', '各部分地位平等 → 没有重点，答案必须“全面概括”', RED, 3),
]
for i, (name, desc, c, idx) in enumerate(rows):
    x0 = 60 + (i % 2) * 450
    y0 = 140 + (i // 2) * 120
    round_box(d, (x0, y0, x0 + 410, y0 + 100), fill=(255, 255, 255), outline=c, width=3)
    round_box(d, (x0 + 16, y0 + 16, x0 + 116, y0 + 56), fill=c)
    text_c(d, (x0 + 66, y0 + 28), name, f(18, True), (255, 255, 255))
    d.text((x0 + 132, y0 + 22), desc[:14], font=f(16, True), fill=DARK)
    d.text((x0 + 132, y0 + 52), desc[14:], font=f(15), fill=GRAY)
d.text((60, 410), '关联词定位法：', font=f(20, True), fill=BLUE)
d.text((230, 410), '但是/然而/却（转折后）→ 因此/所以（结论）→ 更/甚至（递进）→ 同时/此外（并列）', font=f(19, True), fill=DARK)
d.text((60, 460), '主体排除法：选项主语与文段主语不一致 → 直接排除（又快又准）', font=f(20, True), fill=DARK)
d.text((60, 510), '选项“绝对化”（一定、必然、所有）大多错误；“片面”项（只提一个例子）是常见陷阱', font=f(20, True), fill=RED)
img.save(os.path.join(OUT, 'yanyu-structure.png'))

print('done', len(os.listdir(OUT)))
