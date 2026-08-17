-- 申论题库表结构
SET NAMES utf8mb4;

DROP TABLE IF EXISTS shenlun_answer;
DROP TABLE IF EXISTS shenlun_question;
DROP TABLE IF EXISTS shenlun_material;
DROP TABLE IF EXISTS shenlun_paper;

CREATE TABLE shenlun_paper (
  id BIGINT NOT NULL AUTO_INCREMENT,
  paper_code VARCHAR(32) NOT NULL,
  title VARCHAR(200) NOT NULL,
  year INT DEFAULT NULL,
  version VARCHAR(32) DEFAULT NULL,
  question_count INT DEFAULT 0,
  create_time DATETIME DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_code (paper_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='申论试卷';

CREATE TABLE shenlun_material (
  id BIGINT NOT NULL AUTO_INCREMENT,
  paper_id BIGINT NOT NULL,
  m_no INT DEFAULT NULL,
  title VARCHAR(100) DEFAULT NULL,
  content MEDIUMTEXT,
  PRIMARY KEY (id),
  KEY idx_paper (paper_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='申论材料';

CREATE TABLE shenlun_question (
  id BIGINT NOT NULL AUTO_INCREMENT,
  paper_id BIGINT NOT NULL,
  qno INT DEFAULT NULL,
  title TEXT,
  score INT DEFAULT NULL,
  word_limit INT DEFAULT NULL,
  ref_answer MEDIUMTEXT,
  PRIMARY KEY (id),
  KEY idx_paper (paper_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='申论题目';

CREATE TABLE shenlun_answer (
  id BIGINT NOT NULL AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  paper_id BIGINT NOT NULL,
  content TEXT COMMENT 'JSON: {qno: 作答内容}',
  grade_json TEXT COMMENT 'JSON: [{qno, score, analysis, suggestions}]',
  status INT DEFAULT 0 COMMENT '0未评分 1已评分',
  create_time DATETIME DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='申论作答与评分';

-- 菜单：申论刷题（刷题中心下）+ 申论题库管理（题库管理下）
INSERT INTO sys_menu (menu_id, menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, remark) VALUES
(2020, '申论刷题', 2000, 6, 'shenlun', 'shenlun/index', 1, 0, 'C', '0', '0', '', 'edit', 'admin', NOW(), '申论真题作答与AI评分'),
(2021, '申论管理', 2005, 3, 'shenlun', 'exam/shenlun', 1, 0, 'C', '0', '0', '', 'table', 'admin', NOW(), '申论题库管理');
INSERT IGNORE INTO sys_role_menu (role_id, menu_id) VALUES (1,2020),(2,2020),(1,2021);
