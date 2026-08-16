# -*- coding: utf-8 -*-
"""菜单调整：
1. 删除「若依官网」菜单（所有人）
2. 普通角色（role_id=2）不展示 系统管理/系统监控/系统工具
3. 普通角色补上 刷题中心/题库管理 菜单
"""
import subprocess

MYSQL = r'C:\Users\admin\DSH\tools\mysql57\bin\mysql.exe'


def mysql(sql, raw=False):
    args = [MYSQL, '-u', 'root', '-p123456', '--default-character-set=utf8mb4', 'ruoyi', '-N', '-e', sql]
    if raw:
        args.append('--raw')
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print('SQL ERR:', r.stderr[:200])
    return r.stdout.strip()


def mysql_noout(sql):
    subprocess.run([MYSQL, '-u', 'root', '-p123456', '--default-character-set=utf8mb4', 'ruoyi', '-e', sql],
                   capture_output=True, text=True)


# 1) 全部菜单树
rows = []
for line in mysql("SELECT menu_id, parent_id FROM sys_menu;").splitlines():
    if not line.strip():
        continue
    mid, pid = line.split('\t')
    rows.append((int(mid), int(pid)))

children = {}
for mid, pid in rows:
    children.setdefault(pid, []).append(mid)


def subtree(root):
    out = [root]
    stack = [root]
    while stack:
        cur = stack.pop()
        for c in children.get(cur, []):
            out.append(c)
            stack.append(c)
    return out


# 2) 删除「若依官网」(menu_id=4)
if 4 in children.get(0, []):
    mysql_noout("DELETE FROM sys_role_menu WHERE menu_id=4; DELETE FROM sys_menu WHERE menu_id=4;")
    print('已删除 若依官网')

# 3) 普通角色去掉 系统管理(1)/系统监控(2)/系统工具(3)
remove_ids = []
for root in (1, 2, 3):
    remove_ids += subtree(root)
if remove_ids:
    idlist = ','.join(str(x) for x in remove_ids)
    mysql_noout("DELETE FROM sys_role_menu WHERE role_id=2 AND menu_id IN (" + idlist + ");")
    print('普通角色已移除系统菜单', len(remove_ids), '个')

# 4) 普通角色补 刷题中心/题库管理
names = "('刷题中心','试卷练习','随机练习','错题本','刷题页面','题库管理','试卷管理','题目管理')"
have = set(mysql("SELECT menu_id FROM sys_role_menu WHERE role_id=2;").split())
ids = [int(x) for x in mysql("SELECT menu_id FROM sys_menu WHERE menu_name IN " + names + ";").split() if x.strip()]
added = 0
for mid in ids:
    if str(mid) not in have:
        mysql_noout("INSERT INTO sys_role_menu (role_id, menu_id) VALUES (2, " + str(mid) + ");")
        added += 1
print('普通角色补充刷题菜单', added, '个')

# 5) 校验
print('--- 普通角色菜单 ---')
print(mysql("SELECT m.menu_name, m.path FROM sys_role_menu rm JOIN sys_menu m ON m.menu_id=rm.menu_id "
            "WHERE rm.role_id=2 AND m.parent_id=0 ORDER BY m.order_num;"))
