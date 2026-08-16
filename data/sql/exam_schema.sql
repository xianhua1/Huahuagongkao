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
