-- 国考刷题 业务表结构
SET NAMES utf8mb4;

DROP TABLE IF EXISTS exam_record;
DROP TABLE IF EXISTS exam_question;
DROP TABLE IF EXISTS exam_material;
DROP TABLE IF EXISTS exam_paper;

CREATE TABLE exam_paper (
  id            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  paper_code    VARCHAR(32)  NOT NULL COMMENT '卷代码（如 2020-dsj）',
  title         VARCHAR(200) NOT NULL COMMENT '试卷标题',
  year          INT          DEFAULT NULL COMMENT '年份',
  version       VARCHAR(32)  DEFAULT NULL COMMENT '版本（副省级/地市级/A卷等）',
  subject       VARCHAR(32)  DEFAULT '行测' COMMENT '科目',
  question_count INT         DEFAULT 0 COMMENT '题目数量',
  create_time   DATETIME     DEFAULT CURRENT_TIMESTAMP,
  update_time   DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_paper_code (paper_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='国考真题试卷';

CREATE TABLE exam_material (
  id         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  paper_id   BIGINT       NOT NULL COMMENT '试卷ID',
  section    VARCHAR(32)  DEFAULT NULL COMMENT '所属题型',
  title      VARCHAR(200) DEFAULT NULL COMMENT '材料标题（如（一）、请根据下图回答81～85题）',
  content    MEDIUMTEXT   COMMENT '材料内容 HTML',
  sort_order INT          DEFAULT 0 COMMENT '排序',
  PRIMARY KEY (id),
  KEY idx_m_paper (paper_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='阅读材料（资料分析等共享材料）';

CREATE TABLE exam_question (
  id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  paper_id    BIGINT       NOT NULL COMMENT '试卷ID',
  material_id BIGINT       DEFAULT NULL COMMENT '材料ID',
  section     VARCHAR(32)  DEFAULT NULL COMMENT '题型',
  qno         INT          DEFAULT 0 COMMENT '卷内原题号',
  qorder      INT          DEFAULT 0 COMMENT '全卷顺序号（展示用）',
  stem        MEDIUMTEXT   COMMENT '题干 HTML',
  options     TEXT         COMMENT '选项 JSON',
  answer      VARCHAR(8)   DEFAULT '' COMMENT '正确答案',
  analysis    MEDIUMTEXT   COMMENT '解析',
  has_image   TINYINT      DEFAULT 0 COMMENT '是否含图片',
  create_time DATETIME     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_q_paper (paper_id, qorder),
  KEY idx_q_material (material_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='真题题目';

CREATE TABLE exam_record (
  id            BIGINT   NOT NULL AUTO_INCREMENT COMMENT '主键',
  user_id       BIGINT   NOT NULL COMMENT '用户ID',
  question_id   BIGINT   NOT NULL COMMENT '题目ID',
  user_answer   VARCHAR(8) DEFAULT NULL COMMENT '用户答案',
  is_correct    TINYINT  DEFAULT 0 COMMENT '是否正确 0否 1是',
  answered_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '答题时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_user_q (user_id, question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='答题记录';

-- 菜单：刷题中心 & 题库管理
SET @parent1 = (SELECT menu_id FROM sys_menu WHERE menu_name = '刷题中心' LIMIT 1);
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('刷题中心', 0, 6, 'practice', NULL, 1, 0, 'M', '0', '0', '', 'education', 'admin', sysdate(), '刷题中心目录');
SET @parent1 = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('试卷练习', @parent1, 1, 'papers', 'practice/papers', 1, 0, 'C', '0', '0', 'exam:paper:list', 'documentation', 'admin', sysdate(), '按历年真题试卷刷题');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('随机练习', @parent1, 2, 'random', 'practice/random', 1, 0, 'C', '0', '0', 'exam:random', 'shuffle', 'admin', sysdate(), '按题型随机刷题');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('错题本', @parent1, 3, 'wrong', 'practice/wrong', 1, 0, 'C', '0', '0', 'exam:record:wrong', 'delete', 'admin', sysdate(), '错题回顾');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('刷题页面', @parent1, 4, 'session', 'practice/session', 1, 0, 'C', '1', '0', 'exam:paper:list', 'form', 'admin', sysdate(), '刷题主页面（隐藏菜单）');

SET @parent2 = (SELECT menu_id FROM sys_menu WHERE menu_name = '题库管理' LIMIT 1);
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('题库管理', 0, 7, 'exam', NULL, 1, 0, 'M', '0', '0', '', 'list', 'admin', sysdate(), '题库管理目录');
SET @parent2 = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('试卷管理', @parent2, 1, 'paper', 'exam/paper', 1, 0, 'C', '0', '0', 'exam:paper:list', 'table', 'admin', sysdate(), '试卷管理');
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
VALUES ('题目管理', @parent2, 2, 'question', 'exam/question', 1, 0, 'C', '0', '0', 'exam:question:list', 'edit', 'admin', sysdate(), '题目管理');

-- 授权给管理员角色
INSERT INTO sys_role_menu (role_id, menu_id)
SELECT 1, menu_id FROM sys_menu WHERE menu_name IN ('刷题中心','试卷练习','随机练习','错题本','刷题页面','题库管理','试卷管理','题目管理')
AND menu_id NOT IN (SELECT menu_id FROM sys_role_menu WHERE role_id = 1);

-- ===== 备考中心等业务菜单补全（幂等，可重复执行）=====
-- 备考中心菜单补全（幂等：已存在则跳过）
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2011, '每日一练', 2000, 5, 'daily', 'prep/daily', 1, 0, 'C', '0', '0', '', 'calendar', 'admin', NOW(), '每天10题混刷打卡'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2011);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2010, '备考中心', 0, 8, 'prep', NULL, 1, 0, 'M', '0', '0', '', 'notebook', 'admin', NOW(), '备考中心目录'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2010);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2012, '学习计划', 0, 9, 'plan', 'prep/plan', 1, 0, 'C', '0', '0', '', 'calendar', 'admin', NOW(), '90天学习计划'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2012);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2018, '学习报告', 0, 10, 'report', 'prep/report', 1, 0, 'C', '0', '0', '', 'trend-charts', 'admin', NOW(), '学习数据报告'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2018);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2013, '成语积累', 2010, 3, 'chengyu', 'prep/chengyu', 1, 0, 'C', '0', '0', '', 'reading', 'admin', NOW(), '高频成语'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2013);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2014, '申论规范词', 2010, 4, 'guifan', 'prep/guifan', 1, 0, 'C', '0', '0', '', 'notebook', 'admin', NOW(), '规范词库'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2014);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2015, '时政速递', 2010, 5, 'shizheng', 'prep/shizheng', 1, 0, 'C', '0', '0', '', 'clock', 'admin', NOW(), '时政新闻与测验'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2015);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2016, '速记卡片', 2010, 6, 'cards', 'prep/cards', 1, 0, 'C', '0', '0', '', 'tickets', 'admin', NOW(), '闪卡速记'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2016);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2017, '申论素材', 2010, 7, 'sucai', 'prep/sucai', 1, 0, 'C', '0', '0', '', 'collection', 'admin', NOW(), '范文与模板'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2017);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2022, '词语辨析', 2010, 8, 'cybx', 'prep/cybx', 1, 0, 'C', '0', '0', '', 'star', 'admin', NOW(), '词语辨析练习'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2022);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2023, '高频词语', 2010, 9, 'highword', 'prep/highword', 1, 0, 'C', '0', '0', '', 'collection', 'admin', NOW(), '高频词语学习'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2023);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2024, '生词锦囊', 2010, 10, 'myword', 'prep/myword', 1, 0, 'C', '0', '0', '', 'bookmark', 'admin', NOW(), '生词收藏'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2024);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2026, '计时工具', 2010, 12, 'timer', 'prep/timer', 1, 0, 'C', '0', '0', '', 'clock', 'admin', NOW(), '考试计时'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2026);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2027, '行测助手', 2010, 13, 'aide', 'prep/aide', 1, 0, 'C', '0', '0', '', 'c-scale-to-original', 'admin', NOW(), '口算与速算'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2027);
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark)
SELECT 2009, '资料', 0, 11, 'docs', 'docs/index', 1, 0, 'C', '0', '0', '', 'document', 'admin', NOW(), '资料教程'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 2009);

-- 授权：管理员(1) + 普通角色(2)
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT 1, m.menu_id FROM sys_menu m WHERE m.menu_id BETWEEN 2009 AND 2027;
INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT 2, m.menu_id FROM sys_menu m WHERE m.menu_id IN (2000,2001,2002,2003,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2020,2022,2023,2024,2026,2027);
