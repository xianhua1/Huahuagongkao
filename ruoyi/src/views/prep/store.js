// 备考中心本地进度存储（按用户隔离）
export function keyOf(uid, name) {
  return 'dsh.prep.' + uid + '.' + name
}

export function load(uid, name, fallback) {
  try {
    const v = localStorage.getItem(keyOf(uid, name))
    return v ? JSON.parse(v) : fallback
  } catch (e) {
    return fallback
  }
}

export function save(uid, name, val) {
  try {
    localStorage.setItem(keyOf(uid, name), JSON.stringify(val))
  } catch (e) {
    /* ignore */
  }
}

export function today() {
  const d = new Date()
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

// 打卡：记录某天完成了一次学习
export function addCheckin(uid) {
  const list = load(uid, 'checkins', [])
  const t = today()
  if (!list.includes(t)) {
    list.push(t)
    save(uid, 'checkins', list)
  }
  return list.length
}

export function checkinCount(uid) {
  return load(uid, 'checkins', []).length
}
