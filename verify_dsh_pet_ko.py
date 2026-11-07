#!/usr/bin/env python3
"""dsh-pet 한국어 패치 검증기 (임시 실행용 사본)."""
import io, json, os, re, sys, urllib.request

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
        import json as _j
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
    ok = not missing and not dirty
    print("\nRESULT:", "OK — 메뉴 라벨이 전부 한국어입니다" if ok else "확인 필요")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
