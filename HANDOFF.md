# dsh-pet 한국어화 작업 — 세션 인계 요약

> 새 세션(`C:\work\dsh-pet-ko` 워크스페이스)에서 이 문서를 읽고 이어가면 됩니다.

---

## 1. 한 줄 요약

DSH 데스크톱 펫 플러그인 **dsh-pet**을 한국어로 쓰기 위한 패치 저장소입니다.
**우클릭 메뉴**(176항목)·**설정 페이지·펫 대화 패널**(283키)·**날씨**(문구 28종 + 도시명)를
모두 한국어화했고, 펫이 하는 말도 한국어입니다. 패치는 GitHub에 공개되어 있습니다.

**현재 상태: 전부 완료. 추가 작업 없음.**

---

## 2. 무엇이 되어 있나

| 항목 | 상태 | 위치 |
|---|---|---|
| dsh-pet 설치 | **0.4.9**, 프로필 `desktop` | `~/.dsh/profiles/desktop/node_modules/dsh-pet` |
| 한국어 언어팩 | `dsh-plugin-locale-ko` 0.4.1 설치됨 | 프로필 번들 4번째 |
| 펫 말(혼잣말·대화·잠꼬대·작업상태) 한국어화 | 적용 완료 | `~/.dsh/dsh-pet/main-config.jsonc` |
| 메뉴 라벨 한국어화 (176개 항목) | 적용 완료 | dsh-pet 번들 3개 파일 직접 패치 |
| **날씨 한국어화 (문구 28종 + 도시명)** | **적용 완료** | `lib/index.js` WMO 표 + IP 역지오코딩 |
| **설정·대화 UI 한국어화 (283키)** | **적용 완료** | `lib/client.js`에 ko 사전 주입 |
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

## 5. 설정 페이지·대화 패널 한국어화 (이번에 추가한 부분)

### 왜 영어로 나왔나

설정 페이지는 하드코딩이 아니라 **자체 로케일 사전**을 씁니다.

```js
ctx.locale.register(NS$1, dicts$1);   // NS$1 = "pet.config"
ctx.locale.register(NS, dicts);       // NS   = "pet.chat"
```

그런데 `dicts`에 **zh/en/ja/es/fr/de/ru/pt 8개만** 있고 `ko`가 없습니다.
프레임워크 폴백 체인이 `ko → en`이라 **한국어 화면에서 영어가 표시**됐습니다.
(중국어가 아니라 영어로 보이는 게 포인트)

### 어떻게 해결했나

`lib/client.js`에서 각 사전 선언 **바로 앞**에 ko 사전을 주입하고, 표에 `ko:` 항목을 추가합니다.

```js
// 주입 (pet.config / pet.chat 각각)
const __DSH_PET_KO_PET_CONFIG__ = { "nav": "펫 설정", … };

// 표에 한 줄 추가
const dicts$1 = {
  zh: zh$1, en: en$1, ja: ja$1, es: es$1,
  fr: fr$1, de: de$1, ru: ru$1, pt: pt$1,
  ko: __DSH_PET_KO_PET_CONFIG__      // ← 추가
};
```

- **다른 언어 사전은 한 글자도 안 건드립니다.**
- `t()` 호출 지점도 안 바꿉니다.
- 폴백이 `ko → en`이라 키가 빠져도 영어로 안전하게 떨어집니다.
- 주입 위치가 `const NS...` **앞**이어야 TDZ 에러가 안 납니다.

### 커버리지

| 네임스페이스 | 키 수 |
|---|---|
| `pet.config` (설정 페이지) | 233 |
| `pet.chat` (펫 대화 패널) | 50 |
| **합계** | **283** |

추가로 `t()`를 우회하던 하드코딩 중문 **15곳**도 교체했습니다:
아바타 업로드 오류 3, 테스트 알림 제목·본문 2, CJK 구분자 `、`·`：` 3, 목소리 선택 라벨 1,
날씨 버블 6(`天气`·`暂时查不到天气`·`体感`·`湿度`·`风速`·`观测 `).

### 0.4.9에서 새로 번역한 것

0.4.7~0.4.9 사이에 추가된 기능들. 기존 사전으로는 영어나 중문이 나오던 부분.

| 릴리스 | 기능 | 번역 |
|---|---|---|
| 0.4.7 | 음성 서비스 개편 (스위치 4개 + 음성 인식) | 새 키 3 + 의미가 바뀐 키 4 재번역 |
| 0.4.8 | 위치·날씨 (도시·자동 감지) | 새 키 9 + 날씨 버블 6 |
| 0.4.9 | 창이 활성일 때도 알림 | 새 키 2 |

메뉴에도 `查询天气`(날씨 조회)가 추가되어 사전이 175 → 176항목이 됐습니다.

### 사전 파일

`pet_locale_ko.json` — 이 파일이 단일 소스입니다. 스크립트가 읽어서 번들에 주입합니다.
번역을 고칠 때는 이 JSON만 수정하고 `patch --revert` 후 다시 적용하면 됩니다.

---

## 5-B. 날씨 한국어화 (0.4.8+ 기능)

**날씨 조회를 눌렀더니 한자가 나온다**는 제보로 시작한 작업. 원인이 **세 군데**였다.

| 무엇이 중문이었나 | 어디 | 왜 놓쳤나 |
|---|---|---|
| `晴`·`多云`·`小雨` … 28종 | `lib/index.js`의 `TEXT_BY_CODE` | 서버가 날씨 코드를 **중국어 문구로 만들어** 내려보냄. 클라이언트만 고쳐선 안 됨 |
| `体感`·`湿度`·`风速`·`观测` | `env-view.ts` | 하드코딩. **웹 번들과 `shared-core.js` 양쪽에 중복** |
| `首尔特别市`·`韩国` | IP 위치 API (`?lang=zh-CN`) | 도시명을 중국어로 받아 버블 제목에 그대로 씀 |

### 세 번 헛짚은 기록 (다음에 같은 실수 하지 말 것)

1. `client.js`의 `env-view`만 고쳤다 → **데스크톱 펫은 `shared-core.js`를 쓰므로 계속 중문**
2. 하드코딩 라벨을 다 고쳤다 → **`summary`(맑음/흐림)는 서버 WMO 표에서 오므로 계속 중문**
3. 그것도 고쳤다 → **도시명이 IP API에서 중국어로 와서 제목이 `首尔特别市`**

### 도시명 해결 방식

```
ip-api (?lang=zh-CN, lat/lon 추가 요청)
  └→ 좌표로 BigDataCloud 역지오코딩 (localityLanguage=ko)  → "서울특별시"
       └→ 실패하면 중문 region을 표시에서 제거 (제목에 중문이 붙지 않게)

도시명 검색(Open-Meteo): language=ko 먼저 → 실패 시 기존 zh
  · ko는 Seoul / 부산 / Tokyo 에 강함
  · 北京 같은 중국어 입력엔 약해서 zh 폴백이 필요
```

### 확인

```powershell
node check_weather_ko.mjs
```

DSH 인증(401) 없이 날씨 경로만 실행해, 버블에 뜰 문자열을 그대로 출력한다.

```
버블 제목: 서울특별시   OK
날씨 버블: { 제목: '서울특별시', 요약: '대체로 맑음', 기온: '5.3°C',
             체감: '2.6°C', 습도: '80%', 풍속: '6.5 km/h' }
RESULT: OK — 날씨 버블이 전부 한국어입니다
```

### 주의: 외부 API 3곳 의존

`ip-api.com`(위치) · `bigdatacloud.net`(한국어 지명) · `open-meteo.com`(날씨).
어디든 막히면 그 부분만 원래 동작으로 폴백한다(중문 지명이 다시 보일 수 있음).

---

## 6. 저장소 (C:\work\dsh-pet-ko)

```
C:\work\dsh-pet-ko\
├── .git\                    origin -> github.com/invu1318/dsh-pet-ko
├── .gitattributes
├── .gitignore               backup/ 제외 (남의 코드 재배포 방지)
├── LICENSE                  MIT
├── README.md                사용법·원리·제한
├── HANDOFF.md               이 문서
├── patch_dsh_pet_ko.py      --check / (없음) / --revert
├── verify_dsh_pet_ko.py     커버리지 검증 (메뉴 + 로케일 + 날씨)
├── check_weather_ko.mjs     날씨 버블 종단 확인 (인증 없이 실행)
└── pet_locale_ko.json       한국어 사전 283키 (번역 수정은 여기서)
```

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
Invoke-WebRequest -Uri "$env:DSH_WEB_URL/dsh-pet-7340/reload" -Method Post
```
설정 페이지는 **F5 새로고침** 필요.

### 검증 방법

1. `verify_dsh_pet_ko.py` — 메뉴 176 + 로케일 283키, 플레이스홀더/한자/누락 검사
2. `node --check lib/client.js` — 문법 검사
3. 로케일 하네스 — 번들을 VM에서 로드해 283키가 실제로 한국어로 해석되는지 확인
4. GUI 눈으로 확인 — 설정 → 펫 설정 탭, 펫 대화 탭

---

## 7. 이어서 할 때 알아야 할 것

### 업데이트하면 패치가 사라진다
dsh-pet을 업데이트/재설치하면 번들이 교체되어 패치가 날아갑니다.
그때 `patch_dsh_pet_ko.py`를 다시 실행하면 됩니다. `--check`로 상태 확인 가능.
- `ANCHOR-MISS` → dsh-pet 내부 구조가 바뀐 것. 앵커 문자열 갱신 필요.
- `HARDCODED-MISS` → 하드코딩 문자열이 바뀐 것. `HARDCODED` 목록 갱신 필요.

### 업데이트 절차 (실제로 해 본 순서)

1. `npm view dsh-pet version` 으로 새 버전 확인
2. 새 버전의 `lib/client.js`에서 사전 키 diff — 새 키와 영문이 바뀐 키를 뽑아
   `pet_locale_ko.json` 갱신 (플레이스홀더 `{n}` 보존 필수)
3. 새로 생긴 하드코딩 중문을 찾아 `HARDCODED` 목록에 추가
4. 프로필 업그레이드:
   ```powershell
   $rt = "C:\Users\krez13\AppData\Local\Programs\DeepSeek Harness\resources\runtime\primary-runtime\dependencies"
   cd C:\Users\krez13\.dsh\profiles\desktop
   & "$rt\node\bin\node.exe" "$rt\pnpm\bin\pnpm.mjs" add dsh-pet@<버전> --ignore-scripts
   ```
   dsh-pet에는 install 스크립트가 없어 `--ignore-scripts`가 안전하다.
5. `patch_dsh_pet_ko.py` → `verify_dsh_pet_ko.py` → `node --check`
6. **DSH 재시작** (아래 참고)

### DSH 재시작이 필요한 이유
업그레이드 직후에는 플러그인 라우트가 **404**다. DSH 프로세스가 구 번들을 메모리에 들고 있어서다.
`POST /dsh-pet-7340/reload`도 405가 난다. 재시작하면 401(인증 필요)로 바뀌는데,
그게 정상 — 라우트가 살아 있다는 뜻이다.

재시작은 루트 `DeepSeek Harness.exe`(부모가 없는 프로세스)를 종료하면 된다.
DSH를 켜면 **웹 포트가 매번 바뀐다.** `$env:DSH_WEB_URL` 또는 이 세션의 GUI URL을 보라.

### 남은 개선 여지
- **짤 이미지 안의 글자는 여전히 중국어** — 그림 파일이라 번역 대상이 아님. 하려면 이미지 재생성이 필요.
- **아직 중문인 영역** — 사용 빈도가 낮아 손대지 않았다. 같은 방식(하드코딩 치환 목록)으로 확장 가능:
  - `src/shared/todo/*` — 할 일 패널·마감 선택기 (약 60개)
  - `src/client/baifan/*` — 「吃白饭」 미니게임 대사 (약 30개)
  - `src/shared/chat/hear-control.ts` — 음성 입력 안내 (16개)
  - `src/shared/balance/*` — 잔액 버블 (18개)
  - `src/shared/notify.ts` — 시스템 알림 제목·본문 (8개)

### 세션/환경 제약
- **이 DSH 웹 GUI는 인증이 필요**해서 에이전트가 브라우저로 열면 401입니다.
  화면 확인은 사용자가 직접 해야 합니다.
- 세션 시작 시 `C:\work\dsh-pet-ko`에 Windows 파일 권한 문제가 있었음.
  `diagnose-windows-sandbox-acl` 스킬로 복구했고, 그 기록(`.acl-recovery/`)은 `.gitignore`에 넣었음.
- `C:\work\dsh-pet-ko` 워크스페이스는 이미 등록됨 (id `e6651c31`)

---

## 8. 참고 링크

- 원본 플러그인: https://github.com/PC2005-cloud/dsh-pet
- 한국어 언어팩(전제 조건): https://github.com/jjoni12/dsh-locale-ko
- 우리 저장소: https://github.com/invu1318/dsh-pet-ko
- dsh-pet API 문서: https://github.com/PC2005-cloud/dsh-pet/blob/main/API.md

## 9. 라이선스 주의

dsh-pet 애셋(애니메이션·밈 이미지)은 **비상업** 조건입니다.
펫 이미지 "大肥鱼"는 커뮤니티 2차창작이며 원저작자는
[PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet)입니다.
우리 패치는 표시 문자열만 다루고 원본 애셋을 재배포하지 않습니다.
