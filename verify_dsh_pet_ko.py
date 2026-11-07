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
CFG_URL = "http://127.0.0.1:13302/dsh-pet-7340/config"
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
                             "浏览器不支持缩放这张图")
                 if s in stripped]
    if leftovers:
        print("\n[locale] 하드코딩 중문 잔존: %s" % ", ".join(leftovers))
        problems += len(leftovers)
    return problems


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
    try:
        with urllib.request.urlopen(CFG_URL, timeout=8) as r:
            cfg = json.loads(r.read().decode("utf-8")).get("main", {})
        live = True
    except Exception:
        cfg = {"animations": {}, "memes": {}}
        live = False
    need = required_names(cfg)
    missing = sorted(n for n in need if n not in dicts["client"])
    print("config source : %s" % ("live /dsh-pet-7340/config" if live else "unavailable"))
    print("required names: %d" % len(need))
    print("translated    : %d" % (len(need) - len(missing)))
    print("missing       : %d" % len(missing))
    for n in missing: print("   - %s" % n)
    dirty = [(k, v) for k, v in dicts["client"].items() if HAN.search(v)]
    print("values with Han: %d" % len(dirty))
    for k, v in dirty: print("   ! %s -> %s" % (k, v))

    locale_problems = verify_locale()

    ok = not missing and not dirty and locale_problems == 0
    print("\nRESULT:", "OK — 메뉴 라벨과 설정·대화 UI가 모두 한국어입니다"
          if ok else "확인 필요")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
