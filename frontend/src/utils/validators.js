import { parseMmDdYy, toMmDdYy, todayMmDdYy } from './date'

// 与服务端同一套规则（utils 提示语与服务端同源，避免前后端文案漂移）
export function validateUsername(username) {
  if (!username) return { code: 1001, message: '用户名不能为空' }
  if (/^\d+$/.test(username)) return { code: 1002, message: '用户名不能由纯数字组成，请重新输入' }
  if (/^\d/.test(username)) return { code: 1003, message: '用户名不能由数字开头，请重新输入' }
  if (username.length < 4) return { code: 1004, message: '用户名长度必须至少为4个字符' }
  if (username.length > 8) return { code: 1005, message: '用户名不能超过8位，请重新输入' }
  if (!/^[0-9A-Za-z]{4,8}$/.test(username)) return { code: 1012, message: '用户名只能由字母和数字组成，请重新输入' }
  return null
}

export function validateUsernameLogin(username) {
  if (!username) return { code: 1101, message: '请输入用户名' }
  if (/^\d+$/.test(username)) return { code: 1103, message: '用户名不能由纯数字组成，请重新输入' }
  if (/^\d/.test(username)) return { code: 1104, message: '用户名不能由数字开头，请重新输入' }
  return null
}

export function validatePasswordStrength(password) {
  if (!password || password.length < 8 || password.length > 20) {
    return { code: 1007, message: '密码为8～20位，且需同时包含字母与数字' }
  }
  if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
    return { code: 1007, message: '密码为8～20位，且需同时包含字母与数字' }
  }
  return null
}

export function validateFlightDate(s) {
  const d = parseMmDdYy(s)
  if (!d) return { code: 3008, message: '航班日期格式不正确，请按mm/dd/yy输入' }
  if (toMmDdYy(d) <= todayMmDdYy()) {
    return { code: 3001, message: `此日期后的航班日期有效${todayMmDdYy()}` }
  }
  return null
}

export function validateAnswerLength(answer) {
  if (!answer || !answer.trim()) return { code: 1009, message: '请选择安全问题并填写答案' }
  const len = answer.trim().length
  if (len < 2 || len > 30) return { code: 1013, message: '安全问题答案长度须为2～30位' }
  return null
}
