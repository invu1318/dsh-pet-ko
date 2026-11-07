# dsh-pet 한국어화 작업 — 세션 인계 요약

> 새 세션(`C:\work\dsh-pet-ko` 워크스페이스)에서 이 문서를 읽고 이어가면 됩니다.

---

## 1. 한 줄 요약

DSH 데스크톱 펫 플러그인 **dsh-pet**을 한국어로 쓰기 위한 패치 저장소입니다.
**우클릭 메뉴**(175항목)와 **설정 페이지·펫 대화 패널**(268키) 모두 한국어화 완료했고,
펫이 하는 말도 한국어입니다. 패치는 GitHub에 공개되어 있습니다.

**현재 상태: 전부 완료. 추가 작업 없음.**

---

## 2. 무엇이 되어 있나

| 항목 | 상태 | 위치 |
|---|---|---|
| dsh-pet 설치 | 0.4.5, 프로필 `desktop` | `~/.dsh/profiles/desktop/node_modules/dsh-pet` |
| 한국어 언어팩 | `dsh-plugin-locale-ko` 0.4.1 설치됨 | 프로필 번들 4번째 |
| 펫 말(혼잣말·대화·잠꼬대·작업상태) 한국어화 | 적용 완료 | `~/.dsh/dsh-pet/main-config.jsonc` |
| 메뉴 라벨 한국어화 (175개 항목) | 적용 완료 | dsh-pet 번들 3개 파일 직접 패치 |
| **설정·대화 UI 한국어화 (268키)** | **적용 완료** | `lib/client.js`에 ko 사전 주입 |
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
| `pet.config` (설정 페이지) | 218 |
| `pet.chat` (펫 대화 패널) | 50 |
| **합계** | **268** |

추가로 `t()`를 우회하던 하드코딩 중문 **9곳**도 교체했습니다:
아바타 업로드 오류 3, 테스트 알림 제목·본문 2, CJK 구분자 `、`·`：` 3, 목소리 선택 라벨 1.

### 사전 파일

`pet_locale_ko.json` — 이 파일이 단일 소스입니다. 스크립트가 읽어서 번들에 주입합니다.
번역을 고칠 때는 이 JSON만 수정하고 `patch --revert` 후 다시 적용하면 됩니다.

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
├── verify_dsh_pet_ko.py     커버리지 검증 (메뉴 + 로케일)
└── pet_locale_ko.json       한국어 사전 268키 (번역 수정은 여기서)
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
Invoke-WebRequest -Uri http://127.0.0.1:13302/dsh-pet-7340/reload -Method Post
```
설정 페이지는 **F5 새로고침** 필요.

### 검증 방법

1. `verify_dsh_pet_ko.py` — 메뉴 175 + 로케일 268키, 플레이스홀더/한자/누락 검사
2. `node --check lib/client.js` — 문법 검사
3. 로케일 하네스 — 번들을 VM에서 로드해 268키가 실제로 한국어로 해석되는지 확인
4. GUI 눈으로 확인 — 설정 → 펫 설정 탭, 펫 대화 탭

---

## 7. 이어서 할 때 알아야 할 것

### 업데이트하면 패치가 사라진다
dsh-pet을 업데이트/재설치하면 번들이 교체되어 패치가 날아갑니다.
그때 `patch_dsh_pet_ko.py`를 다시 실행하면 됩니다. `--check`로 상태 확인 가능.
- `ANCHOR-MISS` → dsh-pet 내부 구조가 바뀐 것. 앵커 문자열 갱신 필요.
- `HARDCODED-MISS` → 하드코딩 문자열이 바뀐 것. `HARDCODED` 목록 갱신 필요.

### 남은 개선 여지
- **짤 이미지 안의 글자는 여전히 중국어** — 그림 파일이라 번역 대상이 아님. 하려면 이미지 재생성이 필요.
- **대화 패널·설정 외 다른 UI 일부는 중문 하드코딩** — `src/shared/todo/*`, `src/client/baifan/*` 등.
  사용 빈도가 낮아 손대지 않았음. 필요하면 같은 방식(하드코딩 치환 목록)으로 확장 가능.

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
