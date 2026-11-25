#!/usr/bin/env python3
"""dsh-pet Korean patch (right-click menu + settings/chat UI).

Two independent problems, two separate patches:

1. Menu labels are hardcoded in the bundles (not localized), duplicated across
   the web bundle (client.js) and the desktop helper (shared-core.js). The
   script injects a translator at the single menu-label render chokepoint in
   both bundles and translates display labels only.

2. The settings tab and the pet chat panel go through ctx.locale dictionaries,
   but dsh-pet registers only zh/en/ja/es/fr/de/ru/pt for the `pet.config` and
   `pet.chat` namespaces, so a Korean locale falls back to English. The script
   adds a `ko` dictionary to both namespaces and translates the handful of
   Chinese strings that bypass t().

Safety: menu labels are display-only (animations resolve by node.anim and memes
by node.image, the original names), so translating labels cannot break
playback. The locale patch only adds dictionaries: it never edits another
language's entries, and dsh-pet's own t() call sites are untouched.

    python patch_dsh_pet_ko.py --check
    python patch_dsh_pet_ko.py
    python patch_dsh_pet_ko.py --revert
"""

import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALE_KO_PATH = os.path.join(HERE, "pet_locale_ko.json")

PET_ROOT = os.path.join(
    os.environ.get("DSH_HOME", os.path.expanduser(r"~\.dsh")),
    "profiles", "desktop", "node_modules", "dsh-pet",
)

TARGETS = {
    "client": os.path.join(PET_ROOT, "lib", "client.js"),
    "shared-core": os.path.join(PET_ROOT, "runtime", "electron-helper", "shared-core.js"),
    "tray": os.path.join(PET_ROOT, "runtime", "electron-helper", "main", "tray.js"),
}

LABELS = {
    # display submenu
    "显示位置": "표시 위치",
    "仅网页": "웹만",
    "仅桌面": "데스크톱만",
    "两者": "둘 다",
    "都不": "모두 끔",
    # menu groups
    "更多": "더 보기",
    "动作": "동작",
    "配图": "짤",
    "纳入对话的配图": "대화에 쓰는 짤",
    "其他": "기타",
    "待机": "대기",
    "转向": "방향 전환",
    "拖拽": "드래그",
    "点击回应": "클릭 반응",
    "移动": "이동",
    "余额档位": "잔액 단계",
    "工作状态": "작업 상태",
    # root menu
    "查看余额": "잔액 보기",
    "查询天气": "날씨 조회",
    "待办事项": "할 일",
    "碎碎念": "혼잣말",
    "对话": "대화",
    "睡觉": "자기",
    "起来": "일어나기",
    "回到初始位置": "처음 위치로",
    "重载配置": "설정 다시 읽기",
    "打开软件": "앱 열기",
    "打开 AI 设置": "AI 설정 열기",
    "打开网站": "웹사이트 열기",
    "退出": "종료",
    # category ids
    "小动作": "잔동작",
    "玩耍": "놀이",
    "吃什么": "먹기",
    "时节": "절기",
    "文字": "글자",
    # animations
    "可爱宅舞": "귀여운 댄스",
    "开心小跑": "신나는 종종걸음",
    "鲸鱼吐泡泡特效": "고래 방울 뿜기",
    "轻快记录": "경쾌한 기록",
    "轻快摇摆舞": "경쾌한 스웨이",
    "工作状态-忙碌点按": "작업-바쁘게 타자",
    "工作状态-思考冒泡": "작업-생각 버블",
    "工作状态-垂头叹气冒汗": "작업-한숨",
    "工作状态-原地踱步张望": "작업-서성임",
    "工作状态-雀跃庆祝": "작업-축하",
    "工作状态-清点归档": "작업-정리",
    "期待开饭": "밥 기다리기",
    "骑木马": "목마 타기",
    "女仆屈膝礼仪": "메이드 인사",
    "大口吃零食": "간식 와구와구",
    "待机呼吸休闲": "대기 숨쉬기",
    "动物环绕": "동물 맴돌기",
    "东张西望": "두리번두리번",
    "蓝鲸现世": "푸른 고래 강림",
    "撸猫": "고양이 쓰다듬기",
    "萌化小幽灵": "꼬마 유령",
    "舞狮头": "사자춤",
    "放孔明灯": "등불 날리기",
    "放烟花": "불꽃놀이",
    "放风筝": "연날리기",
    "放河灯": "강등 띄우기",
    "螃蟹走路": "게걸음",
    "变鸽子": "비둘기 마술",
    "扑克魔术": "카드 마술",
    "凭空生花": "꽃 피우기",
    "写代码": "코딩",
    "写福字": "복 글씨 쓰기",
    "三球抛接": "공 3개 저글링",
    "插茱萸赏菊": "국화 감상",
    "小提琴演奏": "바이올린 연주",
    "小幅度原地360度旋转展示": "360도 회전",
    "碎碎念-对屏碎碎念": "혼잣말-화면 보며",
    "碎碎念-发呆碎碎念": "혼잣말-멍하니",
    "碎碎念-擦桌碎碎念": "혼잣말-책상 닦기",
    "涮火锅": "훠궈",
    "睡觉-开始": "잠-시작",
    "睡觉-起来": "잠-기상",
    "睡觉-循环": "잠-반복",
    "收红包": "세뱃돈 받기",
    "是啊，吃什么": "그래, 뭐 먹지",
    "晨间刷牙": "아침 양치",
    "深度思考碎碎念": "깊은 생각 혼잣말",
    "余额-金袋叮当": "잔액-금화 자루",
    "余额-袋空如洗": "잔액-텅 빈 자루",
    "余额-分文不剩": "잔액-한 푼도 없음",
    "余额-数金皱眉": "잔액-돈 세며 찡그림",
    "余额-钱袋满溢": "잔액-자루 넘침",
    "余额-钱袋如常": "잔액-평범한 자루",
    "玩水枪": "물총 놀이",
    "玩游戏气急败坏": "게임하다 빡침",
    "摇扇纳凉": "부채질",
    "用鲸鱼尾巴拍打地面": "꼬리로 바닥 치기",
    "优雅女仆舞": "우아한 메이드 댄스",
    "原地敲击桌面互动": "책상 톡톡",
    "原地跳跃抓碎头顶物品": "점프해 잡기",
    "原地小憩沉眠": "제자리 낮잠",
    "原地专心玩魔方": "루빅스 큐브",
    "原地左转奔跑": "제자리 달리기",
    "原地蹲下玩玩具汽车": "장난감 자동차",
    "原地重力下蹲压缩": "중력 앉기",
    "原地漂浮踏步": "떠서 발구르기",
    "悠闲哼歌": "콧노래",
    "装点圣诞树": "크리스마스 트리",
    "点击回应-开心跃动": "클릭-신나서 폴짝",
    "点击回应-傲娇生气": "클릭-도도하게 화남",
    "点击回应-挠痒咯咯笑": "클릭-간지럼 웃음",
    "点击回应-元气挥手": "클릭-손 흔들기",
    "点击回应-害羞惊讶": "클릭-부끄럼 놀람",
    "整体换装试色": "옷 갈아입어 보기",
    "照镜子": "거울 보기",
    "中秋赏月吃月饼": "추석 달맞이",
    "踢毽子": "제기차기",
    "穿针乞巧": "바늘에 실 꿰기",
    "超大伸懒腰": "크게 기지개",
    "抽陀螺": "팽이 돌리기",
    "吹气球": "풍선 불기",
    "吹笛子": "피리 불기",
    "侧身急躁跑": "옆으로 급히 달리기",
    "打瞌睡被惊醒": "졸다 놀람",
    "拆礼物": "선물 뜯기",
    "荡秋千": "그네 타기",
    "讨糖南瓜灯": "할로윈 사탕",
    "堆雪人": "눈사람 만들기",
    "偷吃零食被抓住": "몰래 먹다 들킴",
    "被落叶淹没": "낙엽에 파묻힘",
    "被鼠标拖拽悬空反馈": "드래그 반응",
    "被吓一跳": "깜짝 놀람",
    "下五子棋": "오목 두기",
    "哈欠连天": "하품 연발",
    "蝴蝶蜜蜂环绕头顶开花": "꽃과 나비",
    "吃Token": "토큰 먹기",
    "吃饺子": "만두 먹기",
    "吃年糕": "떡 먹기",
    "吃糖葫芦": "탕후루 먹기",
    "吃大闸蟹": "꽃게 먹기",
    "吃晚餐": "저녁 먹기",
    "吃饭·碗饭": "밥 먹기",
    "吃饭团": "주먹밥 먹기",
    "吃白饭": "쌀밥 먹기",
    "吃冰淇淋融化": "아이스크림 먹기",
    "吃西瓜": "수박 먹기",
    "吃腊八粥": "팥죽 먹기",
    "吃午餐": "점심 먹기",
    "吃长寿面": "장수 국수",
    "吃早餐": "아침 먹기",
    "吃粽子": "쭝쯔 먹기",
    "吃重阳糕": "국화떡 먹기",
    "吃青团": "청퇀 먹기",
    "吃汤圆": "탕위안 먹기",
    # memes
    "吃白饭的大肥鱼": "밥 빼먹는 대왕고래",
    "大的要来啦": "큰 거 온다",
    "大的药来了": "큰 약 왔다",
    "要不直接骂他": "그냥 욕할까",
    "死掉了": "죽었음",
    "深度睡眠": "깊은 잠",
    "大烧货": "토큰 낭비왕",
    "先养着吧": "일단 키우자",
    "吃饱饱摸肚子": "배불러 배 문지르기",
    "誓死践行开源精神": "오픈소스 정신",
    "电死你": "감전시킨다",
    "可爱": "귀여움",
    "token给妈妈保管": "토큰은 엄마가 보관",
    "假如给我三天多模态": "3일만 멀티모달",
    "厉害了我的鲸": "대단해 우리 고래",
    "哦鲸鲸": "아 그래 고래",
    "压力一只大肥鱼": "압박 대왕고래",
    "黎曼猜想没证明喵": "리만 가설 미증명",
    "除了调情没啥用": "쓸모없는 애교",
    "我不更新你们用什么": "업데이트 안 하면 어쩔래",
    "哪来的电脑病毒": "무슨 컴퓨터 바이러스",
    "鱼片有资源吗": "자료 있어?",
    "大师这个区是什么意思": "이 글자 무슨 뜻",
    "就骚了怎么滴吧": "어쩔 건데",
    "完蛋了把黄油删了": "큰일 났다 지웠어",
    "就一碗": "한 그릇만",
    "Ciallo": "Ciallo",
}

MARKER = "__DSH_PET_KO__"

KO_HELPER = """// ---- dsh-pet Korean menu patch (injected by patch_dsh_pet_ko.py) ----
// Labels are display-only: animations resolve by the anim field and memes by the
// image field (original names), so translating them cannot change behavior.
const __DSH_PET_KO__ = %s;
function koLabel(text) {
\tif (typeof text !== "string") return text;
\tconst hit = __DSH_PET_KO__[text];
\treturn hit === void 0 ? text : hit;
}
function koHint(text) {
\tif (typeof text !== "string") return text;
\treturn /^[A-Za-z0-9]*\\s*键$/.test(text) ? text.replace("键", "키") : text;
}
"""


def build_helper_block() -> str:
    body = json.dumps(LABELS, ensure_ascii=False, indent=1)
    indented = "\n".join(" " + line for line in body.splitlines())
    return KO_HELPER % indented


def patch_file(path: str, check_only: bool) -> str:
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if MARKER in src:
        return "ALREADY-PATCHED"

    anchor = "function mountContextMenu("
    if src.count(anchor) != 1:
        return "ANCHOR-MISS:%d" % src.count(anchor)

    n_label = src.count("label.textContent = node.label;")
    n_hint = src.count("hint.textContent = node.hint;")
    if n_label == 0:
        return "NO-LABEL-SITE"
    if check_only:
        return "WOULD-PATCH(label=%d,hint=%d)" % (n_label, n_hint)

    src = src.replace("label.textContent = node.label;", "label.textContent = koLabel(node.label);")
    src = src.replace("hint.textContent = node.hint;", "hint.textContent = koHint(node.hint);")
    src = src.replace(anchor, build_helper_block() + anchor, 1)

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED(label=%d,hint=%d)" % (n_label, n_hint)


def revert_file(path: str) -> str:
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if MARKER not in src:
        return "NOT-PATCHED"
    start = src.index("// ---- dsh-pet Korean menu patch")
    end = src.index("function mountContextMenu(", start)
    src = src[:start] + src[end:]
    src = src.replace("label.textContent = koLabel(node.label);", "label.textContent = node.label;")
    src = src.replace("hint.textContent = koHint(node.hint);", "hint.textContent = node.hint;")
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED"


def patch_tray(path: str, check_only: bool) -> str:
    """Tray menu: only the 'quit' label (pet names come from config)."""
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    needle = "{ label: '退出', click: quitApp }"
    if needle not in src:
        if "{ label: '종료', click: quitApp }" in src:
            return "ALREADY-PATCHED"
        return "NO-TRAY-LABEL"
    if check_only:
        return "WOULD-PATCH"
    src = src.replace(needle, "{ label: '종료', click: quitApp }")
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED"


def revert_tray(path: str) -> str:
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    needle = "{ label: '종료', click: quitApp }"
    if needle not in src:
        return "NOT-PATCHED"
    src = src.replace(needle, "{ label: '退出', click: quitApp }")
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED"


# --------------------------------------------------------------------------
# Locale patch: add a `ko` dictionary to dsh-pet's pet.config / pet.chat
# namespaces, and translate the settings strings that bypass t().
# --------------------------------------------------------------------------

LOCALE_MARKER = "// ---- dsh-pet ko locale patch"

# namespace -> (dict table as shipped, the constant that immediately precedes it)
# The dictionary block is injected before the `const NS...` line so the table can
# reference it without a temporal-dead-zone error.
LOCALE_NAMESPACES = {
    "pet.config": (
        'const dicts$1 = {\n\tzh: zh$1,\n\ten: en$1,\n\tja: ja$1,\n\tes: es$1,\n\tfr: fr$1,\n\tde: de$1,\n\tru: ru$1,\n\tpt: pt$1\n};',
        'const NS$1 = "pet.config";',
    ),
    "pet.chat": (
        'const dicts = {\n\tzh,\n\ten,\n\tja,\n\tes,\n\tfr,\n\tde,\n\tru,\n\tpt\n};',
        'const NS = "pet.chat";',
    ),
}

# Hardcoded Chinese strings in the settings UI that never reach t().
# (needle, replacement) -- each needle must occur exactly once in client.js.
HARDCODED = [
    # avatar upload errors (thrown/shown verbatim)
    ('throw new Error("浏览器不支持缩放这张图")',
     'throw new Error("이 브라우저에서는 이 이미지를 축소할 수 없습니다")'),
    ('"上传失败（HTTP " + res.status + "）"',
     '"업로드 실패(HTTP " + res.status + ")"'),
    ('raw.message : "上传失败"',
     'raw.message : "업로드 실패"'),
    # test notification (OS toast, never passes through t())
    ('new Notification("测试通知", {',
     'new Notification("알림 테스트", {'),
    ('body: "【dsh-pet】系统通知已就绪。"',
     'body: "[dsh-pet] 시스템 알림이 준비되었습니다."'),
    # separators: Korean uses ", " and ": ", not the CJK ideographic ones
    ('result.failed.join("、")',
     'result.failed.join(", ")'),
    ('? "：" + result.message',
     '? ": " + result.message'),
    ('children: t(key) + "：" + value + suffix',
     'children: t(key) + ": " + value + suffix'),
    # voice picker label: `name（tag）`
    ('`${option.name}（${option.tag}）`',
     '`${option.name} (${option.tag})`'),
    # environment / weather bubble (src/shared/env-view.ts) -- hardcoded, never t()
    ('const title = place === "" ? "天气" : place;',
     'const title = place === "" ? "날씨" : place;'),
    ('emptyText: "暂时查不到天气"',
     'emptyText: "이번엔 날씨를 찾지 못했어요"'),
    ('label: "体感"',
     'label: "체감"'),
    ('label: "湿度"',
     'label: "습도"'),
    ('label: "风速"',
     'label: "풍속"'),
    ('{ footer: "观测 " + observed }',
     '{ footer: "관측 " + observed }'),
]

# The weather phrase itself is built server-side from the WMO code table in
# lib/index.js. Neither the locale dictionary nor env-view.ts touches it, so the
# bubble showed Chinese even after the labels above were translated.
WMO_BUNDLE = os.path.join(PET_ROOT, "lib", "index.js")

WMO_CODES = {
    "0": "맑음",
    "1": "대체로 맑음",
    "2": "구름 조금",
    "3": "흐림",
    "45": "안개",
    "48": "상고대 안개",
    "51": "약한 이슬비",
    "53": "이슬비",
    "55": "강한 이슬비",
    "56": "어는 이슬비",
    "57": "강한 어는 이슬비",
    "61": "약한 비",
    "63": "비",
    "65": "강한 비",
    "66": "어는 비",
    "67": "강한 어는 비",
    "71": "약한 눈",
    "73": "눈",
    "75": "강한 눈",
    "77": "싸락눈",
    "80": "약한 소나기",
    "81": "소나기",
    "82": "강한 소나기",
    "85": "약한 소낙눈",
    "86": "강한 소낙눈",
    "95": "뇌우",
    "96": "우박 동반 뇌우",
    "99": "강한 우박 동반 뇌우",
}

WMO_MARKER = "__DSH_PET_KO_WMO__"

# 원문(중국어) 표. --revert가 되돌릴 때 쓴다.
WMO_ZH = {
    "0": "晴", "1": "晴间多云", "2": "多云", "3": "阴",
    "45": "雾", "48": "雾凇",
    "51": "小毛毛雨", "53": "毛毛雨", "55": "大毛毛雨",
    "56": "冻毛毛雨", "57": "强冻毛毛雨",
    "61": "小雨", "63": "中雨", "65": "大雨",
    "66": "冻雨", "67": "强冻雨",
    "71": "小雪", "73": "中雪", "75": "大雪", "77": "雪粒",
    "80": "小阵雨", "81": "阵雨", "82": "强阵雨",
    "85": "小阵雪", "86": "强阵雪",
    "95": "雷阵雨", "96": "雷阵雨伴冰雹", "99": "强雷阵雨伴冰雹",
}

SHARED_CORE = TARGETS["shared-core"]

# 도시 이름: 업스트림은 geocoding을 language=zh로 부른다(중국어 지명).
# language=ko는 로마자·한국어 입력에 강하고 중국어 입력에 약하므로,
# ko를 먼저 시도하고 실패하면 기존 zh로 폴백한다.
GEOCODE_KO_URL = (
    'const GEOCODE_URL = '
    '"https://geocoding-api.open-meteo.com/v1/search?count=1&language=zh&format=json&name=";'
)
GEOCODE_KO_REPLACEMENT = (
    'const GEOCODE_URL = '
    '"https://geocoding-api.open-meteo.com/v1/search?count=1&language=zh&format=json&name=";\n'
    '// [dsh-pet-ko] 한국어 지명 우선. ko로 못 찾으면 아래 GEOCODE_URL(zh)로 폴백한다.\n'
    'const GEOCODE_URL_KO = '
    '"https://geocoding-api.open-meteo.com/v1/search?count=1&language=ko&format=json&name=";'
)

SEARCH_PLACE_OLD = """async function searchPlace(name$1, deps) {
	let body;
	try {
		body = recordOf(await fetchJson(GEOCODE_URL + encodeURIComponent(name$1), {
			label: "open-meteo-geocoding",
			fetchImpl: deps.fetchImpl,
			sleep: deps.sleep
		}));
	} catch {
		return null;
	}"""

SEARCH_PLACE_NEW = """async function searchPlace(name$1, deps) {
	let body;
	// [dsh-pet-ko] 한국어 지명을 먼저 시도하고, 못 찾으면 기존 zh URL로 폴백한다.
	try {
		body = recordOf(await fetchJson(GEOCODE_URL_KO + encodeURIComponent(name$1), {
			label: "open-meteo-geocoding",
			fetchImpl: deps.fetchImpl,
			sleep: deps.sleep
		}));
	} catch {
		body = void 0;
	}
	if (!Array.isArray(body?.results) || body.results.length === 0) try {
		body = recordOf(await fetchJson(GEOCODE_URL + encodeURIComponent(name$1), {
			label: "open-meteo-geocoding",
			fetchImpl: deps.fetchImpl,
			sleep: deps.sleep
		}));
	} catch {
		return null;
	}"""

# IP 기반 자동 감지는 region/city가 중국어로 온다. 제목에 그대로 쓰면
# 「首尔特别市」가 뜨므로, 좌표로 한국어 지명을 다시 얻어 덮어쓴다.
IP_API_URL_OLD = (
    'const IP_API_URL = '
    '"http://ip-api.com/json/?lang=zh-CN&fields=status,city,regionName,country";'
)
IP_API_URL_NEW = (
    'const IP_API_URL = '
    '"http://ip-api.com/json/?lang=zh-CN&fields=status,city,regionName,country,lat,lon";'
)

ASK_IP_OLD = """		if (body === void 0 || body.status !== "success") return null;
		const city = textOf$2(body.city);
		if (city === void 0) return null;
		return {
			city,
			region: textOf$2(body.regionName) ?? "",
			country: textOf$2(body.country) ?? ""
		};"""

ASK_IP_NEW = """		if (body === void 0 || body.status !== "success") return null;
		const city = textOf$2(body.city);
		if (city === void 0) return null;
		return {
			city,
			region: textOf$2(body.regionName) ?? "",
			country: textOf$2(body.country) ?? "",
			// [dsh-pet-ko] 좌표를 함께 받아 한국어 지명 조회에 쓴다.
			latitude: numberOrUndefined(body.lat),
			longitude: numberOrUndefined(body.lon)
		};"""

IP_TITLE_OLD = """		const located = await locateCity(deps);
		if (located === null) return {};
		const weather = await queryWeather(located.city, deps);
		return {
			...located.region === "" ? {} : { region: located.region },
			city: located.city,"""

IP_TITLE_NEW = """		const located = await locateCity(deps);
		if (located === null) return {};
		const weather = await queryWeather(located.city, deps);
		// [dsh-pet-ko] IP가 준 지명은 중국어/영어다. 좌표로 한국어 지명을 다시 얻고,
		// 못 얻으면 원래 값 대신 빈 문자열을 써서 중문이 제목에 붙지 않게 한다.
		const koName = await koreanPlaceName(located, deps);
		const shownCity = koName ?? located.city;
		const shownRegion = koName === null ? located.region : "";
		return {
			...shownRegion === "" ? {} : { region: shownRegion },
			city: shownCity,"""

# 좌표 → 한국어 지명. BigDataCloud 역지오코딩은 무료·무키이며 localityLanguage=ko를
# 지원한다. 실패하면 null을 돌려주고 호출부가 기존 값으로 폴백한다.
REVERSE_GEO_ANCHOR = """//#endregion
//#region src/host/routes/result.ts"""

REVERSE_GEO_HELPER = """//#endregion
//#region [dsh-pet-ko] reverse geocode
/** 좌표 → 한국어 지명. 실패하면 null. */
const REVERSE_GEO_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client";
async function koreanPlaceName(located, deps) {
	const lat = located.latitude;
	const lon = located.longitude;
	if (typeof lat !== "number" || typeof lon !== "number") return null;
	let body;
	try {
		body = recordOf$2(await fetchJson(REVERSE_GEO_URL + "?latitude=" + lat + "&longitude=" + lon + "&localityLanguage=ko", {
			label: "reverse-geocode",
			fetchImpl: deps.fetchImpl,
			sleep: deps.sleep
		}));
	} catch {
		return null;
	}
	return textOf$2(body?.city) ?? textOf$2(body?.principalSubdivision) ?? null;
}

//#endregion
//#region src/host/routes/result.ts"""

GEO_BUNDLE = os.path.join(PET_ROOT, "lib", "index.js")


def ko_var(ns: str) -> str:
    return "__DSH_PET_KO_%s__" % ns.replace(".", "_").upper()


def marker_for(ns: str) -> str:
    return "%s (%s) ----" % (LOCALE_MARKER, ns)


def build_locale_block(ns: str) -> str:
    with io.open(LOCALE_KO_PATH, "r", encoding="utf-8") as fh:
        ko = json.load(fh)
    body = json.dumps(ko[ns], ensure_ascii=False, indent=1)
    lines = [
        marker_for(ns),
        "// dsh-pet ships zh/en/ja/es/fr/de/ru/pt for this namespace, so a Korean",
        "// locale fell back to English. Display-only: no key or code path changes.",
        "const %s = %s;" % (ko_var(ns), body),
    ]
    return "\n".join(lines)


def patch_locale(path: str, check_only: bool, with_dicts: bool) -> str:
    """하드코딩 치환은 모든 번들에, 로케일 사전 주입은 웹 번들에만."""
    if not os.path.exists(path):
        return "MISSING"
    if with_dicts and not os.path.exists(LOCALE_KO_PATH):
        return "NO-DICT-FILE"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if with_dicts and LOCALE_MARKER in src:
        return "ALREADY-PATCHED"
    if not with_dicts and any(repl in src for _needle, repl in HARDCODED):
        return "ALREADY-PATCHED"

    crlf = "\r\n" if "\r\n" in src else "\n"

    # 이 번들에 실제로 있는 하드코딩 항목만 대상으로 한다
    todo = [(n, r) for n, r in HARDCODED if src.count(n) >= 1]
    for needle, _repl in todo:
        if src.count(needle) != 1:
            return "HARDCODED-AMBIGUOUS:%d" % src.count(needle)

    if with_dicts:
        for ns, (table, const_line) in LOCALE_NAMESPACES.items():
            if src.count(table.replace("\n", crlf)) != 1:
                return "ANCHOR-MISS:%s=%d" % (ns, src.count(table.replace("\n", crlf)))
            if src.count(const_line) != 1:
                return "ANCHOR-MISS:%s.const=%d" % (ns, src.count(const_line))

    if not todo and not with_dicts:
        return "NOTHING-TO-DO"
    if check_only:
        return "WOULD-PATCH(ns=%d,hardcoded=%d)" % (
            len(LOCALE_NAMESPACES) if with_dicts else 0, len(todo))

    if with_dicts:
        for ns, (table, const_line) in LOCALE_NAMESPACES.items():
            block = build_locale_block(ns).replace("\n", crlf)
            src = src.replace(const_line, block + crlf + const_line, 1)
            # extend the shipped table with the Korean entry (the last entry has
            # no trailing comma, so the new row must start with one)
            table_now = table.replace("\n", crlf)
            extended = table_now.replace(
                crlf + "};", "," + crlf + "\tko: " + ko_var(ns) + crlf + "};")
            src = src.replace(table_now, extended, 1)

    for needle, repl in todo:
        src = src.replace(needle, repl)

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED(ns=%d,hardcoded=%d)" % (
        len(LOCALE_NAMESPACES) if with_dicts else 0, len(todo))


def revert_locale(path: str) -> str:
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    # 사전을 주입한 번들에는 LOCALE_MARKER가 있고, 하드코딩 치환만 한 번들
    # (shared-core)에는 없다. 어느 쪽이든 되돌릴 게 있는지로 판단한다.
    has_dict = LOCALE_MARKER in src
    has_hard = any(repl in src for _needle, repl in HARDCODED)
    if not has_dict and not has_hard:
        return "NOT-PATCHED"

    crlf = "\r\n" if "\r\n" in src else "\n"
    for ns, (table, const_line) in LOCALE_NAMESPACES.items():
        # remove the injected comment + const declaration, up to the const line
        start_marker = marker_for(ns)
        if start_marker not in src:
            continue
        start = src.index(start_marker)
        end = src.index(const_line, start)
        src = src[:start] + src[end:]
        # drop the ko entry from the table
        table_now = table.replace("\n", crlf)
        extended = table_now.replace(
            crlf + "};", "," + crlf + "\tko: " + ko_var(ns) + crlf + "};")
        src = src.replace(extended, table_now, 1)

    for needle, repl in HARDCODED:
        src = src.replace(repl, needle)

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED"


def patch_wmo(check_only: bool) -> str:
    """날씨 문구 표(WMO code -> 중국어)를 한국어로."""
    path = WMO_BUNDLE
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if WMO_MARKER in src:
        return "ALREADY-PATCHED"

    crlf = "\r\n" if "\r\n" in src else "\n"
    entries = []
    for code, ko in WMO_CODES.items():
        # 원문에서 해당 코드의 중국어 값을 찾아 같은 자리에서 바꾼다
        m = re.search(r'(\n\t%s: ")([^"]+)(")' % re.escape(code), src)
        if m is None:
            return "WMO-MISS:%s" % code
        entries.append((m.group(0), m.group(1) + ko + m.group(3)))

    unknown = re.search(r'return TEXT_BY_CODE\[code\] \?\? "([^"]+)"', src)
    if unknown is None:
        return "WMO-UNKNOWN-MISS"

    if check_only:
        return "WOULD-PATCH(codes=%d)" % len(entries)

    for old, new in entries:
        src = src.replace(old, new, 1)
    src = src.replace(unknown.group(0),
                      'return TEXT_BY_CODE[code] ?? "알 수 없는 날씨"', 1)
    # mark the region so a second run is a no-op (and revert can find it)
    src = src.replace("const TEXT_BY_CODE = {",
                      "// %s WMO code -> Korean weather phrase\nconst TEXT_BY_CODE = {"
                      % WMO_MARKER, 1)

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED(codes=%d)" % len(entries)


def revert_wmo() -> str:
    path = WMO_BUNDLE
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if WMO_MARKER not in src:
        return "NOT-PATCHED"
    for code, ko in WMO_CODES.items():
        src = src.replace('\n\t%s: "%s"' % (code, ko), '\n\t%s: "%s"' % (code, WMO_ZH[code]), 1)
    src = src.replace('return TEXT_BY_CODE[code] ?? "알 수 없는 날씨"',
                      'return TEXT_BY_CODE[code] ?? "未知天气"', 1)
    src = src.replace("// %s WMO code -> Korean weather phrase\n" % WMO_MARKER, "", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED"


def region_span(src, name):
    tag = "//#region " + name
    start = src.find(tag)
    if start < 0:
        return None
    end = src.find("//#endregion", start)
    if end < 0:
        return None
    return start, end


def patch_region_ui(path, check_only):
    """#region 안에서만 중문 라벨을 치환한다 (짧은 문자열 안전)."""
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()

    # 이 번들에 실제로 있는 영역만 대상
    todo, ambiguous = [], []
    for region, pairs in REGION_UI.items():
        span = region_span(src, region)
        if span is None:
            continue
        body = src[span[0]:span[1]]
        for old, new in pairs:
            if new in body:
                continue          # 이미 번역됨
            n = body.count(old)
            if n == 1:
                todo.append((region, old, new))
            elif n > 1 and (region, old) in REGION_ALLOW_MULTI:
                todo.append((region, old, new))
            elif n > 1:
                ambiguous.append((region, old, n))

    if ambiguous:
        return "REGION-AMBIGUOUS:" + ",".join(
            "%s=%d" % (o, n) for _r, o, n in ambiguous[:3])
    if not todo:
        return "ALREADY-PATCHED"
    if check_only:
        return "WOULD-PATCH(%d)" % len(todo)

    # 영역별로 모아서 한 번에 치환 (오프셋이 밀리지 않게 뒤에서부터)
    for region in {r for r, _o, _n in todo}:
        span = region_span(src, region)
        if span is None:
            continue
        body = src[span[0]:span[1]]
        for r, old, new in todo:
            if r == region:
                body = body.replace(old, new)
        src = src[:span[0]] + body + src[span[1]:]

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED(%d)" % len(todo)


def revert_region_ui(path):
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    count = 0
    for region, pairs in REGION_UI.items():
        span = region_span(src, region)
        if span is None:
            continue
        body = src[span[0]:span[1]]
        for old, new in pairs:
            if new in body:
                body = body.replace(new, old)
                count += 1
        src = src[:span[0]] + body + src[span[1]:]
    if count == 0:
        return "NOT-PATCHED"
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED(%d)" % count


def patch_tool_copy(check_only):
    """펫 작업 대사 표(중국어 → 한국어). lib/index.js 한 곳."""
    if not os.path.exists(TOOL_COPY_PATH):
        return "NO-MAP-FILE"
    path = TARGETS["client"].replace("client.js", "index.js")
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    span = region_span(src, TOOL_COPY_REGION)
    if span is None:
        return "ANCHOR-MISS:region"
    body = src[span[0]:span[1]]

    with io.open(TOOL_COPY_PATH, "r", encoding="utf-8") as fh:
        table = json.load(fh)

    todo = []
    for zh, ko in table.items():
        if zh.startswith("_"):
            continue
        if '\"%s\"' % ko in body:
            continue                      # 이미 번역됨
        n = body.count('"%s"' % zh)
        if n == 0:
            return "TOOL-MISS:%s" % zh
        todo.append(zh)

    if not todo:
        return "ALREADY-PATCHED"
    if check_only:
        return "WOULD-PATCH(%d)" % len(todo)

    for zh in todo:
        body = body.replace('"%s"' % zh, '"%s"' % table[zh])
    src = src[:span[0]] + body + src[span[1]:]

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED(%d)" % len(todo)


def revert_tool_copy():
    if not os.path.exists(TOOL_COPY_PATH):
        return "NO-MAP-FILE"
    path = TARGETS["client"].replace("client.js", "index.js")
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    span = region_span(src, TOOL_COPY_REGION)
    if span is None:
        return "ANCHOR-MISS:region"
    body = src[span[0]:span[1]]
    with io.open(TOOL_COPY_PATH, "r", encoding="utf-8") as fh:
        table = json.load(fh)
    count = 0
    for zh, ko in table.items():
        if zh.startswith("_"):
            continue
        if '"%s"' % ko in body:
            body = body.replace('"%s"' % ko, '"%s"' % zh)
            count += 1
    if count == 0:
        return "NOT-PATCHED"
    src = src[:span[0]] + body + src[span[1]:]
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED(%d)" % count


GEO_MARKER = "[dsh-pet-ko]"

# --------------------------------------------------------------------------
# 남은 UI 중문 번역. 짧은 문자열("完成", "添加")이 여러 곳에 나오므로
# **영역(#region) 안에서만** 치환한다. 각 항목은 그 영역 안에서 유일해야 한다.
# 웹 번들과 shared-core.js에 같은 코드가 중복되어 있어 둘 다 적용한다.
# --------------------------------------------------------------------------

REGION_UI = {
    "src/shared/todo/format.ts": [
        ('"周日"', '"일"'), ('"周一"', '"월"'), ('"周二"', '"화"'),
        ('"周三"', '"수"'), ('"周四"', '"목"'), ('"周五"', '"금"'), ('"周六"', '"토"'),
        ("`${minutes}分钟`", "`${minutes}분`"),
        ("`${hours}小时`", "`${hours}시간`"),
        ("`${Math.max(1, Math.round(hours / 24))}天`",
         "`${Math.max(1, Math.round(hours / 24))}일`"),
        ("if (dueAt === null) return \"无期限\";", "if (dueAt === null) return \"기한 없음\";"),
        ("return todo.dueAt === null ? \"已完成\" :",
         "return todo.dueAt === null ? \"완료\" :"),
        ("if (todo.dueAt === null) return \"无期限\";", "if (todo.dueAt === null) return \"기한 없음\";"),
        ("`今天 ${clock}`", "`오늘 ${clock}`"),
        ("`明天 ${clock}`", "`내일 ${clock}`"),
        ("`后天 ${clock}`", "`모레 ${clock}`"),
        ("`${due.getMonth() + 1}月${due.getDate()}日 ${clock}`",
         "`${due.getMonth() + 1}월 ${due.getDate()}일 ${clock}`"),
        ("`已逾期${spanText(now - dueAt)}`", "`${spanText(now - dueAt)} 지남`"),
        ("`还剩${spanText(dueAt - now)}`", "`${spanText(dueAt - now)} 남음`"),
        ("`已完成 · ${dueLabel(todo.dueAt, now)}`", "`완료 · ${dueLabel(todo.dueAt, now)}`"),
    ],
    "src/shared/todo/render.ts": [
        ('"还没有待办。记一件要做的事，到点我会提醒你～"',
         '"아직 할 일이 없어요. 하나 적어두면 때가 되면 알려줄게요~"'),
        ('root.setAttribute("aria-label", "待办事项");',
         'root.setAttribute("aria-label", "할 일");'),
        ('element("span", "dsh-pet-todo-title", "待办事项")',
         'element("span", "dsh-pet-todo-title", "할 일")'),
        ('"0 项未完成"', '"0개 남음"'),
        ('"关闭待办面板"', '"할 일 패널 닫기"'),
        ('"记一件要做的事…"', '"할 일을 적어보세요…"'),
        ('"待办内容"', '"할 일 내용"'),
        ('"离到期越近，我会提醒得越勤快～"', '"마감이 가까울수록 더 자주 알려줄게요~"'),
        ("`${pending} 项未完成`", "`${pending}개 남음`"),
        ('"添加"', '"추가"'),
        ('"标记未完成："', '"미완료로 표시: "'),
        ('"标记完成："', '"완료로 표시: "'),
        ('"删除：" + todo.text', '"삭제: " + todo.text'),
        ('"确认"', '"확인"'),
    ],
    "src/shared/todo/due-picker.ts": [
        ('"提醒时间（可选）"', '"알림 시각(선택)"'),
        ('"选择提醒时间"', '"알림 시각 선택"'),
        ('"上个月"', '"지난달"'),
        ('"下个月"', '"다음달"'),
        ("`${date.getMonth() + 1}月${date.getDate()}日`", "`${date.getMonth() + 1}월 ${date.getDate()}일`"),
        ("state.view.getFullYear()}年${state.view.getMonth() + 1}月",
         "state.view.getFullYear()}년 ${state.view.getMonth() + 1}월"),
        ("${value} ${isHour ? \"时\" : \"分\"}", "${value} ${isHour ? \"시\" : \"분\"}"),
        ('hourChip.setAttribute("aria-label", "选择小时")',
         'hourChip.setAttribute("aria-label", "시 선택")'),
        ('minuteChip.setAttribute("aria-label", "选择分钟")',
         'minuteChip.setAttribute("aria-label", "분 선택")'),
        ('state.mode === "hour" ? "选择小时" : "选择分钟"',
         'state.mode === "hour" ? "시 선택" : "분 선택"'),
        ('"完成"', '"완료"'),
        ("makeButton(\"dsh-pet-todo-due\", \"无期限\")",
         "makeButton(\"dsh-pet-todo-due\", \"기한 없음\")"),
        ('ms === null ? "无期限" : dueLabel(ms, Date.now())',
         'ms === null ? "기한 없음" : dueLabel(ms, Date.now())'),
        ('"无期限" : dueLabel(ms, Date.now())', '"기한 없음" : dueLabel(ms, Date.now())'),
    ],
    "src/shared/todo/panel.ts": [
        ('"清单加载失败，关掉面板再开一次试试"',
         '"목록을 불러오지 못했어요. 패널을 닫았다 다시 열어보세요"'),
        ('"这个时间已经过去了，换一个吧"', '"이미 지난 시각이에요. 다른 시각으로 골라주세요"'),
        ('"加载中…"', '"불러오는 중…"'),
    ],
    # ---- 2차: 알림 / 대화 입력 / 잔액 / 할 일 API / 미니게임 ----
    "src/shared/notify.ts": [
        ('composeTitle(sessionTitle, "生成失败")', 'composeTitle(sessionTitle, "생성 실패")'),
        ('title: "生成失败",', 'title: "생성 실패",'),
        ('?? "对话完成",', '?? "대화 완료",'),
        ('"输出被截断"', '"출력이 잘렸어요"'),
        ('"已达到输出 token 上限"', '"출력 토큰 한도에 도달했어요"'),
        ('"正在申请权限"', '"권한을 요청하는 중"'),
        ('"模型在等你回答"', '"모델이 답을 기다리고 있어요"'),
    ],
    "src/shared/chat/dom.ts": [
        ('input.placeholder = "说点什么…";', 'input.placeholder = "무슨 말이든 해보세요…";'),
        ('iconButton("上传图片"', 'iconButton("이미지 첨부"'),
        ('iconButton("截取当前屏幕"', 'iconButton("화면 캡처"'),
        ('iconButton("按住说话"', 'iconButton("눌러서 말하기"'),
        ('"已选图片"', '"선택한 이미지"'),
        ('attachX.title = "移除图片";', 'attachX.title = "이미지 제거";'),
        ('attachX.setAttribute("aria-label", "移除图片")',
         'attachX.setAttribute("aria-label", "이미지 제거")'),
        ('"只支持 PNG / JPEG / WebP / GIF"', '"PNG / JPEG / WebP / GIF만 됩니다"'),
        ('"读图失败："', '"이미지를 읽지 못했어요: "'),
        ('"截屏失败："', '"화면 캡처 실패: "'),
        ('"当前环境不支持截屏，先用上传试试"', '"이 환경에서는 화면 캡처를 지원하지 않아요. 먼저 업로드를 써보세요"'),
    ],
    "src/shared/chat/dialog.ts": [
        ('"图片还在处理，稍等一下"', '"이미지를 아직 처리하고 있어요. 잠시 기다려 주세요"'),
        ('"对话失败："', '"대화 실패: "'),
        ('"对话异常："', '"대화 오류: "'),
    ],
    "src/shared/chat/encode.ts": [
        ('reader.onerror = () => reject(new Error("这个文件读不出来"))',
         'reader.onerror = () => reject(new Error("이 파일을 읽을 수 없어요"))'),
        ('\t\t\t\treject(new Error("这个文件读不出来"));',
         '\t\t\t\treject(new Error("이 파일을 읽을 수 없어요"));'),
        ('"这个文件解不出图片"', '"이 파일은 이미지로 열 수 없어요"'),
        ('"无法压到预算内"', '"전송 크기 안으로 줄이지 못했어요"'),
        ('"不是可发送的图片"', '"보낼 수 있는 이미지가 아니에요"'),
    ],
    "src/shared/todo/api.ts": [
        ('"响应不是 JSON"', '"응답이 JSON이 아니에요"'),
        ('reason : "请求被拒绝"', 'reason : "요청이 거부되었어요"'),
        ('"连不上桌宠服务："', '"펫 서비스에 연결하지 못했어요: "'),
        ('"响应里没有有效的待办"', '"응답에 유효한 할 일이 없어요"'),
    ],
    "src/shared/balance/view.ts": [
        ('"当前服务商暂不支持余额查询"', '"현재 제공자는 잔액 조회를 지원하지 않아요"'),
        ('"当前服务商："', '"현재 제공자: "'),
        ('"缺少余额查询凭证"', '"잔액 조회 자격 증명이 없어요"'),
        ('"余额查询失败"', '"잔액 조회 실패"'),
    ],
    "src/client/baifan/constants.ts": [
        ('"吃白饭"', '"밥 먹기"'),
        ('"开饭了——"', '"밥 시간이야——"'),
        ('"白饭时间到！"', '"밥 먹을 시간!"'),
        ('"饿了饿了饿了"', '"배고파 배고파 배고파"'),
        ('"等我下去……"', '"내려갈게……"'),
        ('"下面有饭香"', '"아래에서 밥 냄새가 나"'),
        ('"让一让，我下去了"', '"비켜줘, 내려갈게"'),
        ('"饭呢？饭呢？"', '"밥 어디 있어? 밥?"'),
        ('"快点快点"', '"빨리 빨리"'),
        ('"……还没好吗"', '"……아직 안 됐어?"'),
        ('"掉下来了！"', '"떨어진다!"'),
        ('"接住！"', '"받아!"'),
        ('"来了来了"', '"간다 간다"'),
        ('"碗饭最香"', '"그릇밥이 제일 맛있어"'),
        ('"这个碗我要了"', '"이 그릇 내 거야"'),
        ('"再来一碗"', '"한 그릇 더"'),
        ('"饭团饭团"', '"주먹밥 주먹밥"'),
        ('"一口一个"', '"한 입에 하나"'),
        ('"捏得刚好"', '"딱 맞게 뭉쳤어"'),
        ('"嗝——还能吃！"', '"끄윽——더 먹을 수 있어!"'),
        ('"这点不够塞牙缝"', '"이걸로는 이에 끼지도 않아"'),
        ('"再来十份"', '"열 그릇 더"'),
    ],
    # ---- 3차: 음성 입력 안내 ----
    "src/shared/chat/hear-control.ts": [
        ('"当前地址不支持录音：用 https 或 localhost 打开才有麦克风"',
         '"이 주소에서는 녹음할 수 없어요. https나 localhost로 열어야 마이크를 쓸 수 있습니다"'),
        ('"这个入口没有接上识别地址"', '"이 진입점에는 인식 주소가 연결되어 있지 않아요"'),
        ('"这个宿主没开语音识别"', '"이 호스트는 음성 인식을 켜지 않았어요"'),
        ('"音频没通过宿主校验"', '"오디오가 호스트 검증을 통과하지 못했어요"'),
        ('"识别请求失败：" + outcome.message', '"인식 요청 실패: " + outcome.message'),
        ('"未知原因"', '"알 수 없는 이유"'),
        ('hint.show("识别中…")', 'hint.show("인식 중…")'),
        ('hint.flash("没录到声音")', 'hint.flash("녹음된 소리가 없어요")'),
        ('"没听到声音，检查一下麦克风"', '"소리가 들리지 않았어요. 마이크를 확인해 주세요"'),
        ('hint.flash("没听清，再说一次")', 'hint.flash("잘 못 들었어요. 다시 말해 주세요")'),
        ('"录音出错：" + (e instanceof Error', '"녹음 오류: " + (e instanceof Error'),
        ('"正在打开麦克风…"', '"마이크를 여는 중…"'),
        ('"打不开麦克风："', '"마이크를 열지 못했어요: "'),
        ('"录音中 "', '"녹음 중 "'),
        ('" · 松开结束"', '" · 떼면 끝나요"'),
    ],
    # ---- 4차: 잔액 게이지 ----
    "src/shared/balance/handlers/windows.ts": [
        ('\tweekly: "周",', '\tweekly: "주",'),
        ('\tmonthly: "月"', '\tmonthly: "월"'),
        ('if (delta <= 0) return "已重置";', 'if (delta <= 0) return "리셋됨";'),
        ('return (Math.round(hoursF / 24 * 10) / 10).toFixed(1) + " 天";',
         'return (Math.round(hoursF / 24 * 10) / 10).toFixed(1) + "일";'),
        ('return Math.max(.1, Math.round(hoursF * 10) / 10).toFixed(1) + " 小时";',
         'return Math.max(.1, Math.round(hoursF * 10) / 10).toFixed(1) + "시간";'),
        ('if (reset === "") return "重置时间未知";', 'if (reset === "") return "리셋 시각 알 수 없음";'),
        ('return reset === "已重置" ? reset : reset + "重置";',
         'return reset === "리셋됨" ? reset : reset + " 후 리셋";'),
        ('text: "额度数据不可用"', 'text: "사용량 데이터를 쓸 수 없어요"'),
        ('text: w.label + "额度已用 " + Math.round(w.percent) + "%"',
         'text: w.label + " 사용량 " + Math.round(w.percent) + "%"'),
    ],
    "src/shared/todo/due-picker.ts": [
        # 요일 머리글 (월요일 시작)
        ('const WEEK_HEAD = [\n\t"一",\n\t"二",\n\t"三",\n\t"四",\n\t"五",\n\t"六",\n\t"日"\n];',
         'const WEEK_HEAD = [\n\t"월",\n\t"화",\n\t"수",\n\t"목",\n\t"금",\n\t"토",\n\t"일"\n];'),
        ('"今天"', '"오늘"'),
        ('"清除"', '"지우기"'),
    ],
    # ---- 5차: 잔액 상세 / 점수 팝업 / 단축키 힌트 / 알림 / 미니게임 ----
    "src/shared/balance/handlers/money.ts": [
        ('text: "余额 " + amount', 'text: "잔액 " + amount'),
        ('text: "余额（"', 'text: "잔액("'),
        ('v.tier === "peak" ? "峰" : "谷"', 'v.tier === "peak" ? "피크" : "오프"'),
        ('text: "）" + amount', 'text: ") " + amount'),
    ],
    "src/shared/balance/handlers/windows.ts": [
        ('compactCount(u.inputTokens) + " 入"', 'compactCount(u.inputTokens) + " 입력"'),
        ('compactCount(u.outputTokens) + " 出"', 'compactCount(u.outputTokens) + " 출력"'),
        ('const period = "本期 " + u.requests + " 次";',
         'const period = "이번 기간 " + u.requests + "회";'),
    ],
    "src/shared/score-popup.ts": [
        ('"速度 " + Math.round(opts.speed) + " · 大小 " + Math.round(opts.size)',
         '"속도 " + Math.round(opts.speed) + " · 크기 " + Math.round(opts.size)'),
    ],
    "src/shared/display-hotkey.ts": [
        ('String(index + 1) + " 键"', 'String(index + 1) + " 키"'),
    ],
    "src/client/chat/state.ts": [
        ('petName: pet?.name || "宠"', 'petName: pet?.name || "펫"'),
    ],
    "src/shared/notify.ts": [
        ('"工具「" + toolName + "」"', '"도구 \\"" + toolName + "\\""'),
    ],
    "src/shared/chat/hotkey.ts": [
        ('"L 键"', '"L 키"'),
        ('"S 键"', '"S 키"'),
    ],
    "src/shared/sleep-hotkey.ts": [
        ('"Z 键"', '"Z 키"'),
    ],
    "src/shared/todo/hotkey.ts": [
        ('"D 键"', '"D 키"'),
    ],
    "src/shared/chat/hear-hold.ts": [
        ('"M 键"', '"M 키"'),
    ],
    "src/shared/chat/capture.ts": [
        ('"当前环境不支持截屏"', '"이 환경에서는 화면 캡처를 지원하지 않아요"'),
    ],
    "src/shared/hear.ts": [
        ('"识别响应不是 JSON"', '"인식 응답이 JSON이 아니에요"'),
    ],
    "src/shared/chat/hear-control.ts": [
        ('"识别失败：" + (outcome.message', '"인식 실패: " + (outcome.message'),
    ],
    "src/shared/whisper.ts": [
        ('"当前对话未配置模型，碎碎念不可用"', '"현재 대화에 모델이 설정되지 않아 혼잣말을 쓸 수 없어요"'),
        ('"碎碎念生成失败"', '"혼잣말 생성 실패"'),
    ],
    "src/shared/todo/api.ts": [
        ('"请求失败（HTTP ${response.status}）"', '"요청 실패(HTTP ${response.status})"'),
    ],
    "src/shared/balance/handlers/points.ts": [
        ('"积分数据不可用"', '"포인트 데이터를 쓸 수 없어요"'),
        ('text: "余额 " + ', 'text: "잔액 " + '),
    ],
    "src/client/baifan/show.ts": [
        ('"点播失败："', '"재생 실패: "'),
        ('"这一页找不到这只宠物"', '"이 페이지에서 이 펫을 찾을 수 없어요"'),
        ('"锁丢了，表演结束"', '"락을 잃었어요. 공연 끝"'),
        ('"用户接管，已收场"', '"사용자가 넘겨받아 마무리했어요"'),
        ('"重新开始"', '"다시 시작"'),
        ('"吃白饭 —— 开饭了"', '"밥 먹기 —— 밥 시간이야"'),
    ],
    "src/client/baifan/lock.ts": [
        ('"这只宠物没显示在网页里（display=" + String(created.display) + "）"',
         '"이 펫은 웹에 표시되지 않아요 (display=" + String(created.display) + ")"'),
        ('"取锁失败：" + String(reason ?? "unknown")', '"락을 잡지 못했어요: " + String(reason ?? "unknown")'),
        ('"上一场还没收干净，等它过期…"', '"지난 판이 아직 정리되지 않았어요. 만료될 때까지 기다릴게요…"'),
        ('"取锁失败：" + String(retry.reason ?? "unknown")',
         '"락을 잡지 못했어요: " + String(retry.reason ?? "unknown")'),
        ('"宠物被别人占着，等会儿再试"', '"다른 사람이 펫을 쓰고 있어요. 잠시 후 다시 시도하세요"'),
    ],
    # 설정 페이지 음성 목록 (미리듣기 이름)
    "src/host/voice/voices.ts": [
        ('name: "晓晓",', 'name: "샤오샤오",'),
        ('tag: "女 · 通用",', 'tag: "여성 · 범용",'),
        ('name: "晓伊",', 'name: "샤오이",'),
        ('tag: "女 · 活泼",', 'tag: "여성 · 발랄",'),
        ('name: "云希",', 'name: "윈시",'),
        ('tag: "男 · 年轻",', 'tag: "남성 · 젊음",'),
        ('name: "云健",', 'name: "윈젠",'),
        ('tag: "男 · 沉稳",', 'tag: "남성 · 차분",'),
    ],
    "src/host/voice/builtin-deepseek-tts.ts": [
        ('"海星"', '"불가사리"'),
        ('"女声"', '"여성 음성"'),
        ('"暗潮"', '"암초"'),
        ('"男声"', '"남성 음성"'),
    ],
    "src/host/voice/builtin-dsh.ts": [
        ('"DSH 语音插件"', '"DSH 음성 플러그인"'),
    ],
}

# 영역 안에 같은 문구가 여러 번 나와도 전부 같은 번역으로 바꾸면 되는 항목.
# (region, 원문) 형태. 위 REGION_UI에서 중복으로 걸리는 것을 여기서 허용한다.
REGION_ALLOW_MULTI = {
    ("src/client/baifan/show.ts", '"这一页找不到这只宠物"'),
    ("src/host/tool-detail/copy.ts", '"这里得改改"'),
    ("src/host/tool-detail/copy.ts", '"学个新本事"'),
    ("src/host/tool-detail/copy.ts", '"叫人来搭把手"'),
}

# 펫이 작업 중에 중얼거리는 대사 표 (lib/index.js 의 tool-detail/copy.ts).
# 양이 많아 JSON으로 분리했다: { 중국어: 한국어 }
TOOL_COPY_PATH = os.path.join(HERE, "tool_copy_map.json")
TOOL_COPY_REGION = "src/host/tool-detail/copy.ts"


def patch_geocode(check_only: bool) -> str:
    """도시 이름을 한국어로 (geocode language=ko 우선, zh 폴백)."""
    path = GEO_BUNDLE
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if GEO_MARKER in src:
        return "ALREADY-PATCHED"

    for name, needle in (("url", GEOCODE_KO_URL),
                         ("search", SEARCH_PLACE_OLD),
                         ("ipfields", IP_API_URL_OLD),
                         ("askip", ASK_IP_OLD),
                         ("title", IP_TITLE_OLD),
                         ("reverse", REVERSE_GEO_ANCHOR)):
        if src.count(needle) != 1:
            return "GEO-ANCHOR-MISS:%s=%d" % (name, src.count(needle))

    if check_only:
        return "WOULD-PATCH"

    src = src.replace(GEOCODE_KO_URL, GEOCODE_KO_REPLACEMENT, 1)
    src = src.replace(SEARCH_PLACE_OLD, SEARCH_PLACE_NEW, 1)
    src = src.replace(IP_API_URL_OLD, IP_API_URL_NEW, 1)
    src = src.replace(ASK_IP_OLD, ASK_IP_NEW, 1)
    src = src.replace(IP_TITLE_OLD, IP_TITLE_NEW, 1)
    src = src.replace(REVERSE_GEO_ANCHOR, REVERSE_GEO_HELPER, 1)

    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "PATCHED"


def revert_geocode() -> str:
    path = GEO_BUNDLE
    if not os.path.exists(path):
        return "MISSING"
    with io.open(path, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    if GEO_MARKER not in src:
        return "NOT-PATCHED"
    src = src.replace(REVERSE_GEO_HELPER, REVERSE_GEO_ANCHOR, 1)
    src = src.replace(IP_TITLE_NEW, IP_TITLE_OLD, 1)
    src = src.replace(ASK_IP_NEW, ASK_IP_OLD, 1)
    src = src.replace(IP_API_URL_NEW, IP_API_URL_OLD, 1)
    src = src.replace(SEARCH_PLACE_NEW, SEARCH_PLACE_OLD, 1)
    src = src.replace(GEOCODE_KO_REPLACEMENT, GEOCODE_KO_URL, 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    return "REVERTED"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--revert", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(PET_ROOT):
        print("dsh-pet not found: %s" % PET_ROOT)
        return 1

    rc = 0
    for name, path in TARGETS.items():
        if name == "tray":
            res = revert_tray(path) if args.revert else patch_tray(path, args.check)
        else:
            res = revert_file(path) if args.revert else patch_file(path, args.check)
        print("%-12s %s" % (name, res))
        if res.startswith(("MISSING", "ANCHOR-MISS", "NO-LABEL", "NO-TRAY")):
            rc = 1

    # 로케일 사전은 웹 번들에만 있고, 하드코딩 치환은 두 번들 모두에 적용한다
    for label, path, with_dicts in (("locale", TARGETS["client"], True),
                                    ("helper", SHARED_CORE, False)):
        res = revert_locale(path) if args.revert else patch_locale(path, args.check, with_dicts)
        print("%-12s %s" % (label, res))
        if res.startswith(("MISSING", "ANCHOR-MISS", "HARDCODED-AMBIGUOUS", "NO-DICT-FILE")):
            rc = 1

    res = revert_wmo() if args.revert else patch_wmo(args.check)
    print("%-12s %s" % ("weather", res))
    if res.startswith(("MISSING", "WMO-")):
        rc = 1

    res = revert_geocode() if args.revert else patch_geocode(args.check)
    print("%-12s %s" % ("city", res))
    if res.startswith(("MISSING", "GEO-")):
        rc = 1

    for label, path in (("todo-ui", TARGETS["client"]), ("todo-helper", SHARED_CORE)):
        res = revert_region_ui(path) if args.revert else patch_region_ui(path, args.check)
        print("%-12s %s" % (label, res))
        if res.startswith(("MISSING", "REGION-")):
            rc = 1

    res = revert_tool_copy() if args.revert else patch_tool_copy(args.check)
    print("%-12s %s" % ("narration", res))
    if res.startswith(("MISSING", "TOOL-", "NO-MAP")):
        rc = 1

    # 음성 이름 등 host 번들에만 있는 영역
    host_js = os.path.join(PET_ROOT, "lib", "index.js")
    res = revert_region_ui(host_js) if args.revert else patch_region_ui(host_js, args.check)
    print("%-12s %s" % ("host-ui", res))
    if res.startswith(("MISSING", "REGION-")):
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

