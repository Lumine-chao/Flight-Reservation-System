# -*- coding: utf-8 -*-
"""生成全国省份-城市种子数据（backend/sql/cities_data.py）。

数据源：全国 34 个省级行政区的地级市清单（含少量重点县级市）。
编码规则：城市拼音全拼小写；重名城市（如吉林市/吉林、三亚/雅安）追加省份标识消歧。
运行：python generate_cities.py
"""

# (省份, [(城市, 拼音), ...]) —— 拼音为全拼小写
PROVINCE_CITIES = [
    ("北京市", [
        ("北京", "beijing"),
    ]),
    ("天津市", [
        ("天津", "tianjin"),
    ]),
    ("上海市", [
        ("上海", "shanghai"),
    ]),
    ("重庆市", [
        ("重庆", "chongqing"),
    ]),
    ("河北省", [
        ("石家庄", "shijiazhuang"), ("唐山", "tangshan"), ("秦皇岛", "qinhuangdao"),
        ("邯郸", "handan"), ("邢台", "xingtai"), ("保定", "baoding"),
        ("张家口", "zhangjiakou"), ("承德", "chengde"), ("沧州", "cangzhou"),
        ("廊坊", "langfang"), ("衡水", "hengshui"),
    ]),
    ("山西省", [
        ("太原", "taiyuan"), ("大同", "datong"), ("阳泉", "yangquan"),
        ("长治", "changzhi"), ("晋城", "jincheng"), ("朔州", "shuozhou"),
        ("晋中", "jinzhong"), ("运城", "yuncheng"), ("忻州", "xinzhou"),
        ("临汾", "linfen"), ("吕梁", "lvliang"),
    ]),
    ("内蒙古自治区", [
        ("呼和浩特", "huhehaote"), ("包头", "baotou"), ("乌海", "wuhai"),
        ("赤峰", "chifeng"), ("通辽", "tongliao"), ("鄂尔多斯", "eerduosi"),
        ("呼伦贝尔", "hulunbeier"), ("巴彦淖尔", "bayannaoer"), ("乌兰察布", "wulanchabu"),
        ("兴安盟", "xinganmeng"), ("锡林郭勒盟", "xilinguolemeng"), ("阿拉善盟", "alashanmeng"),
    ]),
    ("辽宁省", [
        ("沈阳", "shenyang"), ("大连", "dalian"), ("鞍山", "anshan"),
        ("抚顺", "fushun"), ("本溪", "benxi"), ("丹东", "dandong"),
        ("锦州", "jinzhou"), ("营口", "yingkou"), ("阜新", "fuxin"),
        ("辽阳", "liaoyang"), ("盘锦", "panjin"), ("铁岭", "tieling"),
        ("朝阳", "chaoyang"), ("葫芦岛", "huludao"),
    ]),
    ("吉林省", [
        ("长春", "changchun"), ("吉林", "jilin"), ("四平", "siping"),
        ("辽源", "liaoyuan"), ("通化", "tonghua"), ("白山", "baishan"),
        ("松原", "songyuan"), ("白城", "baicheng"), ("延边", "yanbian"),
    ]),
    ("黑龙江省", [
        ("哈尔滨", "haerbin"), ("齐齐哈尔", "qiqihaer"), ("鸡西", "jixi"),
        ("鹤岗", "hegang"), ("双鸭山", "shuangyashan"), ("大庆", "daqing"),
        ("伊春", "yichun"), ("佳木斯", "jiamusi"), ("七台河", "qitaihe"),
        ("牡丹江", "mudanjiang"), ("黑河", "heihe"), ("绥化", "suihua"),
        ("大兴安岭", "daxinganling"),
    ]),
    ("江苏省", [
        ("南京", "nanjing"), ("无锡", "wuxi"), ("徐州", "xuzhou"),
        ("常州", "changzhou"), ("苏州", "suzhou"), ("南通", "nantong"),
        ("连云港", "lianyungang"), ("淮安", "huaian"), ("盐城", "yancheng"),
        ("扬州", "yangzhou"), ("镇江", "zhenjiang"), ("泰州", "taizhou"),
        ("宿迁", "suqian"),
    ]),
    ("浙江省", [
        ("杭州", "hangzhou"), ("宁波", "ningbo"), ("温州", "wenzhou"),
        ("嘉兴", "jiaxing"), ("湖州", "huzhou"), ("绍兴", "shaoxing"),
        ("金华", "jinhua"), ("衢州", "quzhou"), ("舟山", "zhoushan"),
        ("台州", "taizhou"), ("丽水", "lishui"),
    ]),
    ("安徽省", [
        ("合肥", "hefei"), ("芜湖", "wuhu"), ("蚌埠", "bengbu"),
        ("淮南", "huainan"), ("马鞍山", "maanshan"), ("淮北", "huaibei"),
        ("铜陵", "tongling"), ("安庆", "anqing"), ("黄山", "huangshan"),
        ("滁州", "chuzhou"), ("阜阳", "fuyang"), ("宿州", "suzhou"),
        ("六安", "luan"), ("亳州", "bozhou"), ("池州", "chizhou"),
        ("宣城", "xuancheng"),
    ]),
    ("福建省", [
        ("福州", "fuzhou"), ("厦门", "xiamen"), ("莆田", "putian"),
        ("三明", "sanming"), ("泉州", "quanzhou"), ("漳州", "zhangzhou"),
        ("南平", "nanping"), ("龙岩", "longyan"), ("宁德", "ningde"),
    ]),
    ("江西省", [
        ("南昌", "nanchang"), ("景德镇", "jingdezhen"), ("萍乡", "pingxiang"),
        ("九江", "jiujiang"), ("新余", "xinyu"), ("鹰潭", "yingtan"),
        ("赣州", "ganzhou"), ("吉安", "jian"), ("宜春", "yichun"),
        ("抚州", "fuzhou"), ("上饶", "shangrao"),
    ]),
    ("山东省", [
        ("济南", "jinan"), ("青岛", "qingdao"), ("淄博", "zibo"),
        ("枣庄", "zaozhuang"), ("东营", "dongying"), ("烟台", "yantai"),
        ("潍坊", "weifang"), ("济宁", "jining"), ("泰安", "taian"),
        ("威海", "weihai"), ("日照", "rizhao"), ("临沂", "linyi"),
        ("德州", "dezhou"), ("聊城", "liaocheng"), ("滨州", "binzhou"),
        ("菏泽", "heze"),
    ]),
    ("河南省", [
        ("郑州", "zhengzhou"), ("开封", "kaifeng"), ("洛阳", "luoyang"),
        ("平顶山", "pingdingshan"), ("安阳", "anyang"), ("鹤壁", "hebi"),
        ("新乡", "xinxiang"), ("焦作", "jiaozuo"), ("濮阳", "puyang"),
        ("许昌", "xuchang"), ("漯河", "luohe"), ("三门峡", "sanmenxia"),
        ("南阳", "nanyang"), ("商丘", "shangqiu"), ("信阳", "xinyang"),
        ("周口", "zhoukou"), ("驻马店", "zhumadian"), ("济源", "jiyuan"),
    ]),
    ("湖北省", [
        ("武汉", "wuhan"), ("黄石", "huangshi"), ("十堰", "shiyan"),
        ("宜昌", "yichang"), ("襄阳", "xiangyang"), ("鄂州", "ezhou"),
        ("荆门", "jingmen"), ("孝感", "xiaogan"), ("荆州", "jingzhou"),
        ("黄冈", "huanggang"), ("咸宁", "xianning"), ("随州", "suizhou"),
        ("恩施", "enshi"), ("仙桃", "xiantao"), ("潜江", "qianjiang"),
        ("天门", "tianmen"),
    ]),
    ("湖南省", [
        ("长沙", "changsha"), ("株洲", "zhuzhou"), ("湘潭", "xiangtan"),
        ("衡阳", "hengyang"), ("邵阳", "shaoyang"), ("岳阳", "yueyang"),
        ("常德", "changde"), ("张家界", "zhangjiajie"), ("益阳", "yiyang"),
        ("郴州", "chenzhou"), ("永州", "yongzhou"), ("怀化", "huaihua"),
        ("娄底", "loudi"), ("湘西", "xiangxi"),
    ]),
    ("广东省", [
        ("广州", "guangzhou"), ("韶关", "shaoguan"), ("深圳", "shenzhen"),
        ("珠海", "zhuhai"), ("汕头", "shantou"), ("佛山", "foshan"),
        ("江门", "jiangmen"), ("湛江", "zhanjiang"), ("茂名", "maoming"),
        ("肇庆", "zhaoqing"), ("惠州", "huizhou"), ("梅州", "meizhou"),
        ("汕尾", "shanwei"), ("河源", "heyuan"), ("阳江", "yangjiang"),
        ("清远", "qingyuan"), ("东莞", "dongguan"), ("中山", "zhongshan"),
        ("潮州", "chaozhou"), ("揭阳", "jieyang"), ("云浮", "yunfu"),
    ]),
    ("广西壮族自治区", [
        ("南宁", "nanning"), ("柳州", "liuzhou"), ("桂林", "guilin"),
        ("梧州", "wuzhou"), ("北海", "beihai"), ("防城港", "fangchenggang"),
        ("钦州", "qinzhou"), ("贵港", "guigang"), ("玉林", "yulin"),
        ("百色", "baise"), ("贺州", "hezhou"), ("河池", "hechi"),
        ("来宾", "laibin"), ("崇左", "chongzuo"),
    ]),
    ("海南省", [
        ("海口", "haikou"), ("三亚", "sanya"), ("三沙", "sansha"),
        ("儋州", "danzhou"),
    ]),
    ("四川省", [
        ("成都", "chengdu"), ("自贡", "zigong"), ("攀枝花", "panzhihua"),
        ("泸州", "luzhou"), ("德阳", "deyang"), ("绵阳", "mianyang"),
        ("广元", "guangyuan"), ("遂宁", "suining"), ("内江", "neijiang"),
        ("乐山", "leshan"), ("南充", "nanchong"), ("眉山", "meishan"),
        ("宜宾", "yibin"), ("广安", "guangan"), ("达州", "dazhou"),
        ("雅安", "yaan"), ("巴中", "bazhong"), ("资阳", "ziyang"),
        ("阿坝", "aba"), ("甘孜", "ganzi"), ("凉山", "liangshan"),
    ]),
    ("贵州省", [
        ("贵阳", "guiyang"), ("六盘水", "liupanshui"), ("遵义", "zunyi"),
        ("安顺", "anshun"), ("毕节", "bijie"), ("铜仁", "tongren"),
        ("黔西南", "qianxinan"), ("黔东南", "qiandongnan"), ("黔南", "qiannan"),
    ]),
    ("云南省", [
        ("昆明", "kunming"), ("曲靖", "qujing"), ("玉溪", "yuxi"),
        ("保山", "baoshan"), ("昭通", "zhaotong"), ("丽江", "lijiang"),
        ("普洱", "puer"), ("临沧", "lincang"), ("楚雄", "chuxiong"),
        ("红河", "honghe"), ("文山", "wenshan"), ("西双版纳", "xishuangbanna"),
        ("大理", "dali"), ("德宏", "dehong"), ("怒江", "nujiang"),
        ("迪庆", "diqing"),
    ]),
    ("西藏自治区", [
        ("拉萨", "lasa"), ("日喀则", "rikaze"), ("昌都", "changdu"),
        ("林芝", "linzhi"), ("山南", "shannan"), ("那曲", "naqu"),
        ("阿里", "ali"),
    ]),
    ("陕西省", [
        ("西安", "xian"), ("铜川", "tongchuan"), ("宝鸡", "baoji"),
        ("咸阳", "xianyang"), ("渭南", "weinan"), ("延安", "yanan"),
        ("汉中", "hanzhong"), ("榆林", "yulin"), ("安康", "ankang"),
        ("商洛", "shangluo"),
    ]),
    ("甘肃省", [
        ("兰州", "lanzhou"), ("嘉峪关", "jiayuguan"), ("金昌", "jinchang"),
        ("白银", "baiyin"), ("天水", "tianshui"), ("武威", "wuwei"),
        ("张掖", "zhangye"), ("平凉", "pingliang"), ("酒泉", "jiuquan"),
        ("庆阳", "qingyang"), ("定西", "dingxi"), ("陇南", "longnan"),
        ("临夏", "linxia"), ("甘南", "gannan"), ("敦煌", "dunhuang"),
    ]),
    ("青海省", [
        ("西宁", "xining"), ("海东", "haidong"), ("海北", "haibei"),
        ("黄南", "huangnan"), ("海南州", "hainanzhou"), ("果洛", "guoluo"),
        ("玉树", "yushu"), ("海西", "haixi"),
    ]),
    ("宁夏回族自治区", [
        ("银川", "yinchuan"), ("石嘴山", "shizuishan"), ("吴忠", "wuzhong"),
        ("固原", "guyuan"), ("中卫", "zhongwei"),
    ]),
    ("新疆维吾尔自治区", [
        ("乌鲁木齐", "urumqi"), ("克拉玛依", "kelamayi"), ("吐鲁番", "tulufan"),
        ("哈密", "hami"), ("昌吉", "changji"), ("博尔塔拉", "boertala"),
        ("巴音郭楞", "bayinguoleng"), ("阿克苏", "akesu"), ("克孜勒苏", "kezilesu"),
        ("喀什", "kashi"), ("和田", "hetian"), ("伊犁", "yili"),
        ("塔城", "tacheng"), ("阿勒泰", "aletai"), ("石河子", "shihezi"),
    ]),
    ("香港特别行政区", [
        ("香港", "xianggang"),
    ]),
    ("澳门特别行政区", [
        ("澳门", "aomen"),
    ]),
    ("台湾省", [
        ("台北", "taibei"), ("高雄", "gaoxiong"), ("台中", "taizhong"),
        ("台南", "tainan"), ("新竹", "xinzhu"), ("嘉义", "jiayi"),
    ]),
]


# ============ 民用运输机场所在地白名单 ============
# 依据中国民用航空局截至2024年底的263个境内运输机场（去重到地级行政区）。
# 只有当城市具备民用运输机场时才纳入航班预订系统的可选城市。
AIRPORT_ONLY = set("""
beijing tianjin shanghai chongqing
shijiazhuang xingtai handan zhangjiakou tangshan qinhuangdao chengde
taiyuan shuozhou yuncheng datong changzhi lvliang xinzhou linfen
huhehaote hulunbeier eerduosi baotou chifeng tongliao
xinganmeng xilinguolemeng wulanchabu bayannaoer alashanmeng wuhai
dalian shenyang jinzhou yingkou anshan dandong chaoyang
changchun yanbian baishan tonghua baicheng songyuan
haerbin mudanjiang jiamusi daqing qiqihaer jixi heihe daxinganling yichun
changzhou huaian lianyungang nanjing nantong wuxi xuzhou yancheng yangzhou taizhou
hangzhou ningbo quzhou "taizhou-浙" wenzhou jinhua zhoushan
anqing chizhou fuyang hefei huangshan wuhu xuancheng
fuzhou longyan quanzhou sanming xiamen nanping
ganzhou jian jingdezhen jiujiang nanchang shangrao "yichun-江"
dongying heze jinan jining linyi qingdao rizhao weihai weifang yantai
anyang zhengzhou luoyang nanyang xinyang
wuhan yichang xiangyang shiyan enshi jingzhou ezhou
xiangxi changsha zhangjiajie hengyang changde huaihua yongzhou shaoyang yueyang chenzhou
guangzhou shenzhen zhuhai jieyang zhanjiang huizhou foshan meizhou shaoguan
nanning guilin beihai liuzhou baise wuzhou hechi yulin
haikou sanya sansha
chengdu mianyang yibin nanchong liangshan aba dazhou luzhou panzhihua guangyuan ganzi bazhong
guiyang zunyi tongren bijie qianxinan qiandongnan anshun liupanshui qiannan
kunming lijiang xishuangbanna dehong dali baoshan puer diqing lincang zhaotong wenshan
lasa linzhi changdu ali rikaze shannan
xian xianyang "yulin-陕" hanzhong yanan ankang
lanzhou jiuquan jiayuguan qingyang tianshui jinchang zhangye gannan longnan dunhuang
xining yushu haixi guoluo haibei
yinchuan zhongwei guyuan
urumqi kelamayi tulufan hami changji boertala bayinguoleng akesu kashi hetian yili tacheng aletai shihezi
xianggang aomen
taibei gaoxiong taizhong tainan jiayi
""".replace('"', "").split())


def build():
    cities = {}
    duplicates = {}
    total = 0
    skipped = []
    for province, items in PROVINCE_CITIES:
        for name, py in items:
            code = py
            if code in cities and cities[code]["name"] != name:
                # 重名城市：追加省份简称消歧
                code = f"{py}-{province[0]}"
                if code in cities:
                    raise SystemExit(f"编码冲突: {code} ({name} / {cities[code]['name']})")
            if code not in AIRPORT_ONLY:
                skipped.append(f"{province}/{name}({code})")
                continue
            cities[code] = {"province": province, "name": name}
            duplicates.setdefault(code, 0)
            duplicates[code] += 1
            total += 1
    dup = {k: v for k, v in duplicates.items() if v > 1}
    if dup:
        raise SystemExit(f"存在重复编码: {dup}")
    print(f"跳过无民用运输机场的城市 {len(skipped)} 个：{skipped}")
    return cities, total


def main():
    cities, total = build()
    lines = ['# -*- coding: utf-8 -*-', '"""自动生成的全国省份-城市数据（勿手改，来源 backend/sql/generate_cities.py）。',
             '键为城市编码（拼音全拼，重名加省份首字消歧），值为 (省份, 城市名)。"""', '', 'PROVINCE_CITIES = {']
    for code in sorted(cities):
        province, name = cities[code]["province"], cities[code]["name"]
        lines.append(f'    "{code}": ("{province}", "{name}"),')
    lines.append('}')
    lines.append('')
    lines.append(f'CITY_TOTAL = {total}')
    lines.append('')
    out = r"e:\项目1\1\flight-reservation\backend\sql\cities_data.py"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    provinces = sorted({v["province"] for v in cities.values()})
    print(f"城市总数: {total}, 省份/地区数: {len(provinces)}")
    print(f"已写入: {out}")
    for p in provinces:
        n = sum(1 for v in cities.values() if v["province"] == p)
        print(f"  {p}: {n}")


if __name__ == "__main__":
    main()
