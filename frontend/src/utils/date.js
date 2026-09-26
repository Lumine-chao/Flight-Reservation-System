export function parseMmDdYy(s) {
  const m = /^(\d{2})\/(\d{2})\/(\d{2})$/.exec(s || '')
  if (!m) return null
  const year = Number(m[3]) < 70 ? 2000 + Number(m[3]) : 1900 + Number(m[3])
  const d = new Date(year, Number(m[1]) - 1, Number(m[2]))
  if (d.getFullYear() !== year || d.getMonth() !== Number(m[1]) - 1 || d.getDate() !== Number(m[2])) return null
  return d
}

export function toMmDdYy(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(date.getMonth() + 1)}/${pad(date.getDate())}/${String(date.getFullYear()).slice(-2)}`
}

export function todayMmDdYy() {
  return toMmDdYy(new Date())
}
