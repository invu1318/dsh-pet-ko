#!/usr/bin/env python3
"""dsh-pet 한국어 패치 검증기.

메뉴 라벨 패치(웹/데스크톱/트레이)와 설정·대화 UI 로케일 패치를 함께 검증한다.
"""
import io, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALE_KO_PATH = os.path.join(HERE, "pet_locale_ko.json")

PET_ROOT = os.path.join(os.environ.get("DSH_HOME", os.path.expanduser(r"~\.dsh")),
                        "profiles", "desktop", "node_modules", "dsh-pet")
CLIENT = os.path.join(PET_ROOT, "lib", "client.js")
SHARED = os.path.join(PET_ROOT, "runtime", "electron-helper", "shared-core.js")
INDEX_JS = os.path.join(PET_ROOT, "lib", "index.js")
WMO_MARKER = "__DSH_PET_KO_WMO__"
# Open-Meteo current/daily가 쓰는 코드만 표에 있다
WMO_EXPECTED = {0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67,
                71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99}
def resolve_cfg_url():
    """DSH 웹 포트는 고정이 아니다. DSH_WEB_URL이 있으면 그걸 쓰고,
    없으면 흔한 포트를 훑어 /dsh-pet-7340/config 가 살아 있는 곳을 찾는다."""
    env = os.environ.get("DSH_WEB_URL")
    candidates = []
    if env:
        candidates.append(env.rstrip("/"))
    candidates += ["http://127.0.0.1:%d" % p for p in (13302, 4039, 12467)]
    for base in candidates:
        url = base + "/dsh-pet-7340/config"
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return url
        except Exception:
            continue
    return None
HAN = re.compile(r"[\u4e00-\u9fff]")
FIXED_LABELS = ["显示位置","仅网页","仅桌面","两者","都不","更多","动作","配图",
    "纳入对话的配图","其他","待机","转向","拖拽","点击回应","移动","余额档位",
    "工作状态","查看余额","待办事项","碎碎念","对话","睡觉","起来","回到初始位置",
    "重载配置","打开网站","打开软件","打开 AI 设置","退出"]

def load_dict(path):
    src = io.open(path, encoding="utf-8").read()
    if "__DSH_PET_KO__" not in src:
        return None
    start = src.index("const __DSH_PET_KO__ =")
    end = src.index("function koLabel", start)
    blob = src[start:end].strip().rstrip(";").replace("const __DSH_PET_KO__ =", "", 1)
    return json.loads(blob)

def required_names(cfg):
    need = set(FIXED_LABELS)
    a = cfg.get("animations", {})
    for k in ("idle", "turn", "drag", "clicks"):
        need.update(a.get(k) or [])
    for m in (a.get("moves") or {}).get("actions") or []:
        if m.get("name"): need.add(m["name"])
    for c in a.get("categories") or []:
        need.add(c.get("id")); need.update(c.get("actions") or [])
    ev = {"balance": "余额档位", "whisper": "碎碎念", "workStatus": "工作状态"}
    for key, pool in (a.get("events") or {}).items():
        if key in ev: need.add(ev[key])
        for slot in pool:
            if isinstance(slot, str): need.add(slot)
            else: need.update(slot)
    for s in a.get("sleep") or []:
        for phase in ("start", "loop", "end"): need.update(s.get(phase) or [])
    need.update(a.get("baifan") or [])
    need.update((cfg.get("memes") or {}).keys())
    return {n for n in need if n}

def read_ko_table(src, var):
    """번들에 주입된 한국어 사전 리터럴을 JSON으로 읽는다."""
    start = src.index("const %s = " % var)
    i = start + len("const %s = " % var)
    depth = 0
    while i < len(src):
        c = src[i]
        if c == '"':
            i += 1
            while i < len(src) and src[i] != '"':
                i += 2 if src[i] == "\\" else 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return json.loads(src[start + len("const %s = " % var):i + 1])


def verify_locale():
    """설정·대화 UI 로케일 패치 검증. 문제 수를 돌려준다."""
    problems = 0
    src = io.open(CLIENT, encoding="utf-8").read()

    if "// ---- dsh-pet ko locale patch" not in src:
        print("\n[locale] NOT PATCHED")
        return 1

    ref = json.load(io.open(LOCALE_KO_PATH, encoding="utf-8"))
    for ns, var in (("pet.config", "__DSH_PET_KO_PET_CONFIG__"),
                    ("pet.chat", "__DSH_PET_KO_PET_CHAT__")):
        if src.count("const %s = {" % var) != 1:
            print("\n[locale] %s 선언을 찾을 수 없음" % var); problems += 1; continue
        if src.count("ko: %s" % var) != 1:
            print("\n[locale] %s 가 사전 표에 연결되지 않음" % var); problems += 1

        table = read_ko_table(src, var)
        shipped = ref[ns]
        missing = [k for k in shipped if k not in table]
        extra = [k for k in table if k not in shipped]
        hanja = [(k, v) for k, v in table.items() if HAN.search(v)]
        badph = []
        for k, v in shipped.items():
            a = sorted(re.findall(r"\{(\w+)\}", v))
            b = sorted(re.findall(r"\{(\w+)\}", table.get(k, "")))
            if a != b:
                badph.append((k, a, b))
        print("\n[locale] %s: %d 키 (누락 %d, 초과 %d, 한자 %d, 플레이스홀더 %d)"
              % (ns, len(table), len(missing), len(extra), len(hanja), len(badph)))
        for k in missing[:5]: print("   - missing %s" % k)
        for k in extra[:5]: print("   + extra %s" % k)
        for k, v in hanja[:5]: print("   ! 한자 %s -> %s" % (k, v[:60]))
        for k, a, b in badph[:5]: print("   ! %s 플레이스홀더 %s != %s" % (k, a, b))
        problems += len(missing) + len(extra) + len(hanja) + len(badph)

    # t()를 우회하는 하드코딩 중문이 남아 있는지.
    # zh 원본 사전(다른 언어용 정상 데이터)과 주입 사전 본문은 제외한다.
    stripped = re.sub(r"const __DSH_PET_KO_[A-Z_]+__ = \{.*?\n\};", "", src, flags=re.S)
    stripped = re.sub(r"//#region src/client/(settings|chat)/locales/.*?//#endregion",
                      "", stripped, flags=re.S)
    leftovers = [s for s in ("上传失败", "测试通知", "系统通知已就绪",
                             "浏览器不支持缩放这张图", "暂时查不到天气",
                             '"体感"', '"湿度"', '"风速"')
                 if s in stripped]
    if leftovers:
        print("\n[locale] 하드코딩 중문 잔존: %s" % ", ".join(leftovers))
        problems += len(leftovers)
    return problems


def verify_weather(problems):
    """날씨 문구·도시명 한국어화 검증."""
    # 1. WMO 표: lib/index.js의 날씨 문구 28개
    if not os.path.exists(INDEX_JS):
        print("\n[weather] lib/index.js 없음"); return problems + 1
    idx = io.open(INDEX_JS, encoding="utf-8").read()
    if WMO_MARKER not in idx:
        print("\n[weather] NOT PATCHED (WMO 표)"); return problems + 1
    table = {}
    begin = idx.find("const TEXT_BY_CODE = {")
    if begin < 0:
        print("\n[weather] TEXT_BY_CODE 표를 찾을 수 없음"); return problems + 1
    end = idx.find("};", begin)
    for m in re.finditer(r'\n\t(\d+): "([^"]*)"', idx[begin:end]):
        table[int(m.group(1))] = m.group(2)
    hanja = {c: v for c, v in table.items() if HAN.search(v)}
    print("\n[weather] WMO 표 %d개 (중문 잔존 %d)" % (len(table), len(hanja)))
    for c, v in list(hanja.items())[:5]:
        print("   ! %s -> %s" % (c, v))
    problems += len(hanja)
    missing_codes = [c for c in range(0, 100) if c in WMO_EXPECTED and c not in table]
    if missing_codes:
        print("   - 빠진 코드: %s" % missing_codes)
        problems += len(missing_codes)

    # 2. env-view 라벨: 웹/데스크톱 두 번들 모두
    for label, path in (("client", CLIENT), ("shared-core", SHARED)):
        if not os.path.exists(path):
            continue
        body = io.open(path, encoding="utf-8").read()
        begin = body.find("//#region src/shared/env-view.ts")
        if begin < 0:
            continue
        end = body.find("//#endregion", begin)
        seg = body[begin:end]
        bad = [s for s in ("体感", "湿度", "风速", "暂时查不到天气", "观测 ")
               if s in seg]
        if bad:
            print("\n[weather] %s env-view 중문 잔존: %s" % (label, ", ".join(bad)))
            problems += len(bad)
        else:
            print("[weather] %s env-view 라벨 OK" % label)

    # 3. 도시명: IP 좌표 → 한국어 역지오코딩, geocode는 ko 우선 → zh 폴백
    checks = (("IP 좌표 요청", "country,lat,lon"),
              ("역지오코딩", "koreanPlaceName"),
              ("역지오코딩 URL", "REVERSE_GEO_URL"),
              ("제목 중문 제거", "shownRegion"),
              ("ko geocode", "GEOCODE_URL_KO"),
              ("zh 폴백", "await fetchJson(GEOCODE_URL +"))
    for name, needle in checks:
        if needle not in idx:
            print("[weather] 도시명 패치 누락: %s" % name)
            problems += 1
    if all(n in idx for _x, n in checks):
        print("[weather] 도시명 OK (IP 좌표 → 역지오코딩 ko, geocode ko→zh 폴백)")
    return problems


def load_local_config():
    """번들 기본 설정(assets/config.jsonc)에서 이름 목록을 읽는다.

    웹 API는 인증이 필요해 401이 나므로, 라이브 설정을 못 얻을 때의 기준으로 쓴다.
    이 파일은 애니메이션·짤 이름의 완전한 참조라 커버리지 검사에 충분하다.
    """
    path = os.path.join(PET_ROOT, "assets", "config.jsonc")
    if not os.path.exists(path):
        return None
    raw = io.open(path, encoding="utf-8").read()
    # JSONC -> JSON: 주석과 후행 쉼표 제거
    raw = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*|/\*.*?\*/', lambda m: m.group(1) or "", raw, flags=re.S)
    raw = re.sub(r",(\s*[}\]])", r"\1", raw)
    try:
        return json.loads(raw)
    except Exception:
        return None


def main():
    dicts = {}
    for label, path in (("client", CLIENT), ("shared-core", SHARED)):
        d = load_dict(path)
        if d is None:
            print("%-12s NOT PATCHED" % label); return 1
        dicts[label] = d
        print("%-12s %d entries" % (label, len(d)))
    if dicts["client"] != dicts["shared-core"]:
        print("!! 웹/데스크톱 사전이 다릅니다"); return 1

    cfg_url = resolve_cfg_url()
    cfg, source = None, "unavailable"
    if cfg_url is not None:
        try:
            with urllib.request.urlopen(cfg_url, timeout=8) as r:
                cfg = json.loads(r.read().decode("utf-8")).get("main", {})
            source = cfg_url
        except Exception:
            cfg = None
    if cfg is None:
        cfg = load_local_config()
        if cfg is not None:
            source = "bundled assets/config.jsonc"
    if cfg is None:
        cfg = {"animations": {}, "memes": {}}
    need = required_names(cfg)
    missing = sorted(n for n in need if n not in dicts["client"])
    print("config source : %s" % source)
    print("required names: %d" % len(need))
    print("translated    : %d" % (len(need) - len(missing)))
    print("missing       : %d" % len(missing))
    for n in missing: print("   - %s" % n)
    dirty = [(k, v) for k, v in dicts["client"].items() if HAN.search(v)]
    print("values with Han: %d" % len(dirty))
    for k, v in dirty: print("   ! %s -> %s" % (k, v))

    locale_problems = verify_locale()
    weather_problems = verify_weather(locale_problems)

    ok = not missing and not dirty and weather_problems == 0
    print("\nRESULT:", "OK — 메뉴·설정·대화 UI·날씨가 모두 한국어입니다"
          if ok else "확인 필요")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
