# dsh-pet 한국어화 작업 — 세션 인계 요약

> 새 세션(`C:\work\dsh-pet-ko` 워크스페이스)에서 이 문서를 읽고 이어가면 됩니다.

---

## 1. 한 줄 요약

DSH 데스크톱 펫 플러그인 **dsh-pet**을 설치하고, 펫이 **한국어로 말하게** 하고,
**우클릭 메뉴 전체를 한국어로** 바꾼 뒤, 그 패치를 GitHub에 공개했습니다.

**현재 상태: 전부 완료. 추가 작업 없음.**

---

## 2. 무엇이 되어 있나

| 항목 | 상태 | 위치 |
|---|---|---|
| dsh-pet 설치 | 0.4.5, 프로필 `desktop` | `~/.dsh/profiles/desktop/node_modules/dsh-pet` |
| 펫 말(혼잣말·대화·잠꼬대·작업상태) 한국어화 | 적용 완료 | `~/.dsh/dsh-pet/main-config.jsonc` |
| 메뉴 라벨 한국어화 (175개 항목) | 적용 완료 | dsh-pet 번들 3개 파일 직접 패치 |
| 패치 스크립트 | 커밋·푸시 완료 | `C:\work\dsh-pet-ko\` |
| GitHub 저장소 | 공개 | https://github.com/invu1318/dsh-pet-ko |

---

## 3. 펫 말 한국어화 (설정만으로 됨)

파일: `C:\Users\krez13\.dsh\dsh-pet\main-config.jsonc`

한국어로 바꾼 키:

- `pets[0].name` → `파란 머리 메이드`
- `pets[0].whisperPrompt` → "반드시 한국어로만, 20자 이내, 반말, 중국어·영어 금지" 지시 포함
- `sleepRefuseTexts` / `sleepStartTexts` / `sleepEndTexts` → 한국어 대사
- `workStatusTexts` → 6단계(생각/작업/정리/대기/성공/오류) 한국어 문구

**주의:** 이 파일은 `PUT /dsh-pet-7340/config` API나 설정 페이지에서 저장해도
화이트리스트 밖 키(`sleepRefuseTexts` 등)는 보존됩니다.

검증된 실제 출력 예:
```
"히히, 나 아직 안 자고 있었어~"
"주인님 기다리고 있지~ 이제 자러 가요."
"어떡하지… 버터 지워버렸어…"
```

---

## 4. 메뉴 한국어 패치 (핵심 기술 내용)

### 왜 로케일로 안 되나

dsh-pet은 UI 로케일을 zh/en/ja/es/fr/de/ru/pt만 지원하고,
**우클릭 메뉴 라벨은 로케일이 아니라 번들에 하드코딩**돼 있습니다.
게다가 같은 코드가 **웹과 데스크톱 헬퍼 두 곳에 중복**돼 있습니다.

```
웹         : lib/client.js
데스크톱   : runtime/electron-helper/shared-core.js
트레이     : runtime/electron-helper/main/tray.js
```

### 어떻게 해결했나

라벨을 그리는 **단일 지점**만 후킹했습니다.

```js
label.textContent = koLabel(node.label);   // 표시 직전 사전 조회
hint.textContent  = koHint(node.hint);     // "L 键" -> "L 키"
```

`mountContextMenu` 함수 **앞에** `__DSH_PET_KO__` 사전(175항목)과
`koLabel`/`koHint` 함수를 주입하는 방식입니다. 마커 문자열로 적용 여부를 판별합니다.

### 안전한 이유 (중요)

**메뉴 트리 구조는 건드리지 않습니다.** 라벨은 순수 표시용입니다.

| 용도 | 사용 필드 | 패치 영향 |
|---|---|---|
| 애니메이션 재생 | `node.anim` (원본 중국어 이름) | 없음 |
| 짤 전송 | `node.image` (원본 이름) | 없음 |
| 사전에 없는 문자열 | 그대로 표시 | 없음 |

패치 전후 `node --check` 통과, 패치 후에도 펫이 정상 동작하는 것 확인.

### 커버리지

- 고정 라벨 29 + 애니메이션 114 + 짤 27 + 트레이 1 = **175개**
- 메뉴 트리 노드 **163개**
- 한자 잔존 **0개** (`写福字` → `복 글씨 쓰기`로 수정 이력 있음)

---

## 5. 저장소 (C:\work\dsh-pet-ko)

```
C:\work\dsh-pet-ko\
├── .git\                    origin -> github.com/invu1318/dsh-pet-ko
├── .gitattributes
├── .gitignore               backup/ 제외 (남의 코드 재배포 방지)
├── LICENSE                  MIT
├── README.md                사용법·원리·제한
├── patch_dsh_pet_ko.py      --check / (없음) / --revert
└── verify_dsh_pet_ko.py     커버리지 검증
```

- 커밋: `213aaff` dsh-pet 우클릭 메뉴 한국어 패치
- 원격: public, 토픽 dsh / dsh-plugin / deepseek-harness / desktop-pet / korean / i18n-ko
- **원본 백업은 커밋하지 않음** (되돌리기는 `--revert` 또는 재설치로 충분)

### 사용법

```powershell
$env:DSH_HOME = "$env:USERPROFILE\.dsh"
python C:\work\dsh-pet-ko\patch_dsh_pet_ko.py --check   # 확인
python C:\work\dsh-pet-ko\patch_dsh_pet_ko.py           # 적용
python C:\work\dsh-pet-ko\verify_dsh_pet_ko.py          # 검증
python C:\work\dsh-pet-ko\patch_dsh_pet_ko.py --revert  # 원복
```

적용 후 펫 재시작:
```powershell
Invoke-WebRequest -Uri http://127.0.0.1:13302/dsh-pet-7340/reload -Method Post
```
웹 화면 펫은 **F5 새로고침** 필요.

---

## 6. 이어서 할 때 알아야 할 것

### 업데이트하면 패치가 사라진다
dsh-pet을 업데이트/재설치하면 번들이 교체되어 패치가 날아갑니다.
그때 `patch_dsh_pet_ko.py`를 다시 실행하면 됩니다. `--check`로 상태 확인 가능.
`ANCHOR-MISS`가 나오면 dsh-pet 내부 구조가 바뀐 것이니 앵커 문자열을 갱신해야 합니다.

### 남은 개선 여지
- **짤 이미지 안의 글자는 여전히 중국어** — 그림 파일이라 번역 대상이 아님. 하려면 이미지 재생성이 필요.
- **설정 페이지(桌宠配置 탭) UI는 중국어** — dsh-pet이 `pet.config` 네임스페이스에 ko 사전을 등록하지 않음. DSH의 `ctx.locale.register(ns, 'ko', {...})`로 별도 플러그인을 만들어 붙이면 가능하나, 아직 하지 않음. **이게 가장 자연스러운 다음 작업.**

### 세션/환경 제약
- 이전 세션의 워크스페이스는 `default-workspace`라 `C:\work`에 쓰기가 막혀 있었음
- `C:\work`는 Windows ACL 문제도 있음
- **새 세션은 `C:\work\dsh-pet-ko` 워크스페이스에서 시작해야** 정상적으로 파일 작업 가능
- `C:\work\dsh-pet-ko` 워크스페이스는 이미 등록됨 (id `e6651c31`)

---

## 7. 참고 링크

- 원본 플러그인: https://github.com/PC2005-cloud/dsh-pet
- 우리 저장소: https://github.com/invu1318/dsh-pet-ko
- dsh-pet API 문서: https://github.com/PC2005-cloud/dsh-pet/blob/main/API.md

## 8. 라이선스 주의

dsh-pet 애셋(애니메이션·밈 이미지)은 **비상업** 조건입니다.
펫 이미지 "大肥鱼"는 커뮤니티 2차창작이며 원저작자는
[PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet)입니다.
우리 패치는 표시 문자열만 다루고 원본 애셋을 재배포하지 않습니다.
