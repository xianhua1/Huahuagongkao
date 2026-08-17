# 国考刷题网站（若依 RuoYi-Vue3 + 2000-2022 行测真题）

基于 **RuoYi-Vue3 (v3.8.8)** 前后端分离框架搭建的国考行测刷题网站，
题库来源于 `D:\BaiduNetdiskDownload\国考2000-2022真题word` 中的 Word 真题
（含图片、图片公式、图表材料），答案与解析从配套 PDF 解析提取。

## 访问

| 项目 | 地址 |
| ---- | ---- |
| 刷题网站 | http://127.0.0.1:8090 |
| 后端 API | http://127.0.0.1:8080 |
| 登录账号 | admin / admin123（验证码已关闭；可注册新账号） |

## 一键启动

双击 `C:\Users\admin\DSH\start-all.bat`（自动按需启动 MySQL / Redis / 后端 / 前端）。

## 功能

- **试卷练习**：2000-2022 年共 36 套行测真题（A/B 卷、副省级、地市级、省级、市地级、行政执法类），
  按年筛选，显示每卷进度与正确率，可断点续练。
- **资料分析联动**：题目带共享材料时，左侧固定显示材料面板（文字、表格、图表图片），
  右侧逐题作答，材料始终可见；判断推理组合排列、篇章阅读的共享材料同样支持。
- **随机练习**：按题型（常识判断/言语理解与表达/数量关系/判断推理/资料分析）随机抽题。
- **逐题判分**：选择选项即提交，即时显示对错、正确答案与解析；答题卡可跳题。
- **错题本**：错题汇总，含我的答案/正确答案/解析/材料，可移出或清空。
- **题库管理**：试卷管理、题目管理（可为缺失答案/解析的题目补全答案与解析）。

## 数据规模

- 试卷 127 套（国考行测 36 套 + 事业单位联考职测 91 套，A/B/C/D/E 类 2015-2024）
- 题目 20363 道，阅读材料 1899 份，已有答案与解析 18145 道（约 89%）
- 图片（题干图、图表、图片公式）按卷存放于 `data/images/<卷代码>/`（行测）与
  `data/images_sydw/<卷代码>/`（职测），通过 `/exam-img/**` 静态访问
- 刷题首页可按科目筛选：国考行测 / 事业单位职测

## 环境

- JDK 8（Azul Zulu 8.0.442，位于 `tools/zulu8`）
- Maven 3.9.9（`tools/apache-maven-3.9.9`）
- MySQL 5.7.44（`tools/mysql57`，root/123456，库名 `ruoyi`）
- Redis 5.0.14（`tools/redis`）
- Node.js 24 + npm

## 目录

```
C:\Users\admin\DSH\
├── ruoyi\               RuoYi-Vue3 前端（src/views/practice 刷题页、src/views/exam 管理页）
├── ruoyi-backend\       RuoYi 后端（ruoyi-system 新增 exam 题库模块、ExamController）
├── data\
│   ├── xingce_docx\     转换后的真题 docx（.doc 经 Word COM 转换）
│   ├── parsed\          每卷解析后的 JSON（题目/材料/答案）
│   ├── images\<卷代码>\ 提取的题干图片
│   ├── sql\             exam_schema.sql（表结构+菜单）、exam_data.sql（题库数据）
│   └── ocr_texts\       扫描版答案 PDF 的 OCR 文本缓存
└── tools\               JDK / Maven / MySQL / Redis
```

## 数据重建（可选）

```bash
python tools/parse_all.py all     # 重新解析国考行测（Word -> JSON + 图片）
python tools/parse_sydw.py all    # 重新解析事业单位职测（PDF -> JSON + 图片）
python tools/gen_sql.py           # 生成 data/sql/exam_data.sql
mysql -u root -p123456 ruoyi < data/sql/exam_data.sql
```

## 已知限制

- 个别旧卷（2002-2009）因 PDF 文本层损坏或扫描件，部分题目缺答案（可在题目管理中补全）；
- 2002B 卷答案 PDF 为纯扫描件，仅 OCR 出部分答案；
- 材料以原文呈现：部分年份的资料分析材料本身是整图（截图），直接以图片展示；
- 题库为行测；申论试卷未入库（如需可基于同一解析管线扩展）。
