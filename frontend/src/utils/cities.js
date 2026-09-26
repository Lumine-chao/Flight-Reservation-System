// 将城市列表按省份分组，保持省份首次出现的顺序
export function groupCitiesByProvince(cities) {
  const groups = []
  const index = new Map()
  for (const c of cities || []) {
    const province = c.province || '其他'
    let g = index.get(province)
    if (!g) {
      g = { province, cities: [] }
      index.set(province, g)
      groups.push(g)
    }
    g.cities.push(c)
  }
  return groups
}

// 生成 el-cascader 两级选项：省份 → 城市（叶子 value 为城市 code）
export function cityCascaderOptions(cities) {
  return groupCitiesByProvince(cities).map((g) => ({
    code: g.province,
    name: g.province,
    children: g.cities.map((c) => ({ code: c.cityCode, name: c.cityName })),
  }))
}

export const CASCADER_PROPS = { value: 'code', label: 'name', children: 'children', emitPath: false }

