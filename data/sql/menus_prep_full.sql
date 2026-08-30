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