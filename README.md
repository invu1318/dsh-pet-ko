# dsh-pet-ko

[dsh-pet](https://github.com/PC2005-cloud/dsh-pet)을 **한국어**로 쓰기 위한 패치입니다.

dsh-pet은 UI 로케일을 zh / en / ja / es / fr / de / ru / pt만 지원합니다. 우클릭 메뉴 라벨은
로케일이 아니라 번들에 하드코딩되어 있고, 설정 페이지·펫 대화 패널은 자체 로케일 사전을 쓰는데
거기에 `ko`가 없습니다. 이 저장소는 **두 곳 모두** 한국어로 바꿉니다.

> 펫이 **하는 말**(혼잣말·대화·잠꼬대·작업 상태)은 이 패치가 아니라 `main-config.jsonc`에서
> `whisperPrompt` 등으로 설정합니다. 아래 [말도 한국어로](#말도-한국어로) 참고.

## 무엇이 바뀌나

### 1. 우클릭 메뉴

메뉴 트리 **163개 노드**, 번역 대상 **176개 항목**이 한국어가 됩니다.

| 영역 | 전 | 후 |
|---|---|---|
| 루트 메뉴 | 查看余额 · 查询天气 · 待办事项 · 碎碎念 · 对话 · 睡觉 | 잔액 보기 · 날씨 조회 · 할 일 · 혼잣말 · 대화 · 자기 |
| 표시 위치 | 显示位置 ▸ 仅网页 / 仅桌面 / 两者 / 都不 | 표시 위치 ▸ 웹만 / 데스크톱만 / 둘 다 / 모두 끔 |
| 동작 트리 | 动作 ▸ 待机 / 转向 / 拖拽 / 点击回应 / 移动 / 小动作 / 玩耍 / 吃什么 / 时节 / 文字 | 동작 ▸ 대기 / 방향 전환 / 드래그 / 클릭 반응 / 이동 / 잔동작 / 놀이 / 먹기 / 절기 / 글자 |
| 애니메이션 114개 | 待机呼吸休闲 · 东张西望 · 吃白饭 … | 대기 숨쉬기 · 두리번두리번 · 쌀밥 먹기 … |
| 짤(밈) 27개 | 大的要来啦 · 就一碗 · 可爱 … | 큰 거 온다 · 한 그릇만 · 귀여움 … |
| 단축키 힌트 | `L 键` · `1 键` | `L 키` · `1 키` |
| 트레이 | 退出 | 종료 |

### 2. 설정 페이지 · 펫 대화 패널

`pet.config` **233키**, `pet.chat` **50키** — 합계 **283개 문자열**이 한국어로 나옵니다.

| 영역 | 전(영어로 폴백) | 후 |
|---|---|---|
| 탭 이름 | Pet Config | 펫 설정 |
| 펫 설정 카드 | Size (width px) · Name · Persona (optional) | 크기(가로 px) · 이름 · 페르소나(선택) |
| 전역 스위치 | System notifications · Click sound · System tray | 시스템 알림 · 클릭음 · 시스템 트레이 |
| 물리 · 글꼴 | Gravity · Bounciness · Font size (px) | 중력 · 반발력 · 글꼴 크기(px) |
| 모델 설정 | Follow current conversation · Chat history rounds | 현재 대화 따르기 · 대화 기록 라운드 |
| 음성 (0.4.7+) | Speak manual whispers · Speak work status · Speech recognition | 수동 혼잣말 읽기 · 작업 상태 읽기 · 음성 인식 |
| 위치·날씨 (0.4.8+) | Location · City · Detect | 위치 · 도시 · 자동 감지 |
| 대화 패널 | Say something… · Load earlier · Persona | 무슨 말이든 해보세요… · 이전 대화 불러오기 · 페르소나 |

여기에 더해 `t()`를 우회하던 중문 15곳(아바타 업로드 오류, 테스트 알림 문구,
CJK 구분자 `、`·`：`, 날씨 버블의 `体感`·`湿度`·`风速`·`观测` 등)도
한국어·한국어 구두점으로 바꿉니다.

### 3. 날씨

「날씨 조회」를 눌렀을 때 뜨는 버블 전체가 한국어가 됩니다.
사전에도 `t()`에도 잡히지 않는 곳이라 별도 처리가 필요했습니다 — [자세히](#날씨는-세-곳을-따로-고쳐야-했다).

| 영역 | 전 | 후 |
|---|---|---|
| 날씨 문구 28종 | 晴 · 多云 · 小雨 · 雷阵雨 | 맑음 · 구름 조금 · 약한 비 · 뇌우 |
| 버블 라벨 | 体感 · 湿度 · 风速 · 观测 08:45 | 체감 · 습도 · 풍속 · 관측 08:45 |
| 도시명 | 首尔特别市 · 韩国 | 서울특별시 |
| 조회 실패 | 暂时查不到天气 | 이번엔 날씨를 찾지 못했어요 |

### 4. 나머지 UI 전체

메뉴·설정 밖의 화면들도 번역했습니다. 이 영역들은 `t()`를 전혀 쓰지 않는 하드코딩이라
번들 소스의 `#region` 경계를 이용해 영역 단위로 치환했습니다 — [자세히](#나머지-ui는-영역region-단위로-바꿨다).

| 영역 | 전 | 후 |
|---|---|---|
| **할 일 패널** | 待办事项 · 记一件要做的事… · 0 项未完成 | 할 일 · 할 일을 적어보세요… · 0개 남음 |
| **마감 선택기** | 一 二 三 四 五 六 日 · 今天 · 上个月 | 월 화 수 목 금 토 일 · 오늘 · 지난달 |
| **마감 표시** | 明天 09:00 · 已逾期2小时 · 还剩30分钟 | 내일 09:00 · 2시간 지남 · 30분 남음 |
| **음성 입력** | 按住说话 · 识别中… · 没录到声音 | 눌러서 말하기 · 인식 중… · 녹음된 소리가 없어요 |
| **잔액 게이지** | 周 · 月 · 额度已用 45% · 已重置 | 주 · 월 · 사용량 45% · 리셋됨 |
| **시스템 알림** | 对话完成 · 生成失败 · 正在申请权限 | 대화 완료 · 생성 실패 · 권한을 요청하는 중 |
| **「밥 먹기」 미니게임** | 开饭了—— · 饿了饿了饿了 · 接住！ | 밥 시간이야—— · 배고파 배고파 배고파 · 받아! |
| **작업 중 대사 127개** | 翻翻 {target} 看看嘛 · 折腾折腾 git 仓库 | {target} 좀 볼까 · git 좀 만져볼게 |
| **음성 이름** | 晓晓 · 晓伊 · 云希 · 云健 | 샤오샤오 · 샤오이 · 윈시 · 윈젠 |

## 요구 사항

- Python 3.8+
- dsh-pet이 설치된 DSH 프로필 (기본 `desktop`)
- 한국어 로케일 활성화 — [dsh-locale-ko](https://github.com/jjoni12/dsh-locale-ko)
  (DSH 프로필의 로케일 목록에 `한국어`가 보이면 이미 된 상태입니다)

패치는 `$DSH_HOME/profiles/desktop/node_modules/dsh-pet` 아래 파일 3개를 직접 수정합니다.

### 지원 버전

**dsh-pet 0.4.9** 기준으로 검증했습니다. 0.4.6~0.4.9에서 패치 앵커가 그대로 유지됩니다.
0.4.5 이전은 사전 키가 적어(218키) 일부 항목만 번역됩니다.

업데이트 후에는 `--check`가 `ANCHOR-MISS` 또는 `HARDCODED-MISS`를 내는지 먼저 확인하세요.

## 사용법

```powershell
$env:DSH_HOME = "$env:USERPROFILE\.dsh"

python patch_dsh_pet_ko.py --check    # 먼저 확인 (파일은 건드리지 않음)
python patch_dsh_pet_ko.py            # 적용
python verify_dsh_pet_ko.py           # 검증
```

그 다음 펫을 재시작합니다.

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:$($env:DSH_WEB_URL -replace '.*:','')/dsh-pet-7340/reload -Method Post
```

- **데스크톱 펫**: 위 `reload`로 즉시 반영
- **웹 화면의 펫 · 설정 페이지**: 브라우저 **새로고침(F5)** 필요 (클라이언트 번들은 페이지 로드 시 내려감)

> DSH 웹 포트는 실행할 때마다 바뀝니다. `$env:DSH_WEB_URL`에서 확인하거나,
> DSH 창의 주소를 그대로 쓰세요. `verify_dsh_pet_ko.py`는 이 변수와 흔한 포트를 자동으로 훑습니다.
>
> 번들을 새로 읽히는 가장 확실한 방법은 **DSH 재시작**입니다. 업데이트 직후에는 위 `reload`가
> 404를 낼 수 있습니다(구 번들이 메모리에 남아 있음).

### 확인 출력 예시

```
$ python patch_dsh_pet_ko.py --check
client       WOULD-PATCH(label=2,hint=1)
shared-core  WOULD-PATCH(label=2,hint=1)
tray         WOULD-PATCH
locale       WOULD-PATCH(ns=2,hardcoded=15)
helper       WOULD-PATCH(ns=0,hardcoded=6)
weather      WOULD-PATCH(codes=28)
city         WOULD-PATCH
todo-ui      WOULD-PATCH(119)
todo-helper  WOULD-PATCH(83)
narration    WOULD-PATCH(127)
host-ui      WOULD-PATCH(13)

$ python verify_dsh_pet_ko.py
client       176 entries
shared-core  176 entries
config source : bundled assets/config.jsonc
required names: 175
translated    : 175
missing       : 0
values with Han: 0

[locale] pet.config: 233 키 (누락 0, 초과 0, 한자 0, 플레이스홀더 0)

[locale] pet.chat: 50 키 (누락 0, 초과 0, 한자 0, 플레이스홀더 0)

[weather] WMO 표 28개 (중문 잔존 0)
[weather] client env-view 라벨 OK
[weather] shared-core env-view 라벨 OK
[weather] 도시명 OK (IP 좌표 → 역지오코딩 ko, geocode ko→zh 폴백)
[ui] client 번역 OK
[ui] shared-core 번역 OK
[ui] 작업 대사(127개) OK
[ui] 음성 이름 OK

RESULT: OK — 메뉴·설정·대화·날씨·할일·음성·대사가 모두 한국어입니다
```

### 되돌리기

```powershell
python patch_dsh_pet_ko.py --revert
```

패치는 모두 마커(`__DSH_PET_KO__`, `// ---- dsh-pet ko locale patch`,
`__DSH_PET_KO_WMO__`, `[dsh-pet-ko]`)를 남기므로 원복이 그 흔적을 지우는 방식으로 동작합니다.
로케일 패치만 되돌리면 파일이 **바이트 단위로** 원본과 일치하는 것을 확인했습니다.
`--revert` 뒤 `--check`는 전 항목이 `WOULD-PATCH`로 돌아와야 정상입니다.
dsh-pet을 재설치해도 원래대로 돌아갑니다.

## 어떻게 동작하나

### 메뉴 — 라벨 그리는 한 지점만 후킹

dsh-pet은 같은 메뉴 코드를 **웹 번들과 데스크톱 헬퍼 두 곳에 중복**해서 가지고 있습니다.

| 대상 | 파일 |
|---|---|
| 웹 클라이언트 | `lib/client.js` |
| 데스크톱 헬퍼 | `runtime/electron-helper/shared-core.js` |
| 트레이 | `runtime/electron-helper/main/tray.js` |

그래서 `ctx.locale.register()` 같은 로케일 API로는 메뉴를 번역할 수 없습니다.
대신 **라벨을 그리는 단 한 곳**을 후킹합니다.

```js
// 원본
label.textContent = node.label;
hint.textContent  = node.hint;

// 패치 후
label.textContent = koLabel(node.label);   // 표시 직전 사전 조회
hint.textContent  = koHint(node.hint);     // "L 键" → "L 키"
```

**메뉴 트리 구조는 건드리지 않습니다.** 라벨은 순수 표시용이고, 실제 동작은 다른 필드가 결정합니다.

| 용도 | 필드 | 패치 영향 |
|---|---|---|
| 애니메이션 재생 | `node.anim` — 원본 중국어 이름 그대로 | 없음 |
| 짤 전송 | `node.image` — 원본 이름 그대로 | 없음 |
| 사전에 없는 문자열 | 그대로 표시 (fallback) | 없음 |

따라서 표시명을 바꿔도 재생·전송·파일 탐색은 영향받지 않습니다.

### 설정·대화 — 로케일 사전에 ko 추가

프레임워크는 `ctx.locale.register(ns, dicts)`로 등록된 사전을 쓰고, 없으면 `en`으로
폴백합니다. dsh-pet은 `pet.config`·`pet.chat`에 8개 언어만 등록하므로 한국어 화면에서
영어가 나왔습니다. 패치는 두 표에 `ko` 항목을 추가할 뿐입니다.

```js
const dicts$1 = {
  zh: zh$1, en: en$1, ja: ja$1, es: es$1,
  fr: fr$1, de: de$1, ru: ru$1, pt: pt$1,
  ko: __DSH_PET_KO_PET_CONFIG__      // ← 추가
};
```

다른 언어 사전은 한 글자도 건드리지 않고, `t()` 호출 지점도 바꾸지 않습니다.
폴백 체인은 `ko → en`이라 사전에 없는 키가 생겨도 영어로 안전하게 떨어집니다.

### 그런데 사전에 없는 문자열

dsh-pet은 일부 문구를 `t()`를 거치지 않고 코드에 직접 박아 둡니다.
날씨 버블이 대표적입니다(`src/shared/env-view.ts`, 그리고 같은 코드가
데스크톱 헬퍼 `shared-core.js`에도 중복돼 있습니다).

```js
label: "体感"                       // → label: "체감"
{ footer: "观测 " + observed }       // → { footer: "관측 " + observed }
```

이런 문자열은 `patch_dsh_pet_ko.py`의 `HARDCODED` 목록에서 원문→번역으로 직접 치환합니다.
각 항목은 번들에 **정확히 한 번만** 나타나야 하고(아니면 `HARDCODED-AMBIGUOUS`),
`--revert` 시 원문으로 되돌립니다.

현재 15곳을 다룹니다: 아바타 업로드 오류 3, 테스트 알림 2, CJK 구분자 3,
목소리 선택 라벨 1, 날씨 버블 6.

### 날씨는 세 곳을 따로 고쳐야 했다

날씨 버블이 중국어로 나오던 원인은 한 군데가 아니었습니다.

| 무엇 | 어디 | 왜 |
|---|---|---|
| `晴`·`多云`·`小雨` … 28종 | `lib/index.js`의 WMO 표 | 서버가 날씨 코드를 **중국어 문구로 바꿔서** 내려보냄 |
| `体感`·`湿度`·`风速`·`观测` | `env-view.ts` (웹·헬퍼 **양쪽**) | 하드코딩. 한쪽만 고치면 데스크톱 펫에서 계속 중문 |
| `首尔特别市`·`韩国` | IP 위치 API (`?lang=zh-CN`) | 도시명을 중국어로 받아 그대로 버블 제목에 씀 |

도시명은 이렇게 해결합니다.

1. IP API에 `lat`·`lon`도 함께 요청
2. 그 좌표로 **한국어 역지오코딩**(BigDataCloud, `localityLanguage=ko`) — `서울특별시`
3. 도시명 검색(Open-Meteo)은 `language=ko`를 먼저, 실패하면 기존 `zh`로 폴백
   (`ko`는 `Seoul`·`부산`·`Tokyo`에 강하고, `北京` 같은 중국어 입력에 약하다)
4. 역지오코딩이 실패하면 중문 `region`을 **표시에서 뺀다** — 중문이 제목에 붙지 않게

확인은 이렇게 합니다(DSH 인증 없이 날씨 경로만 실행):

```powershell
node check_weather_ko.mjs
```

```
버블 제목: 서울특별시   OK
날씨 버블: { 제목: '서울특별시', 요약: '대체로 맑음', 기온: '5.3°C',
             체감: '2.6°C', 습도: '80%', 풍속: '6.5 km/h' }
RESULT: OK — 날씨 버블이 전부 한국어입니다
```

### 나머지 UI는 영역(#region) 단위로 바꿨다

할 일 패널·음성 입력·잔액 게이지·미니게임은 `t()`도 안 쓰고 사전도 없습니다.
그런데 `"完成"`·`"今天"` 같은 짧은 문자열이 파일 곳곳에 흩어져 있어
단순 치환은 위험합니다. 번들에 남아 있는 `//#region` 경계를 이용해 **영역 안에서만**
치환하면 안전합니다.

```python
def region_span(src, name):
    start = src.find("//#region " + name)
    end   = src.find("//#endregion", start)
    return start, end
```

세 가지 규칙을 지킵니다.

1. 그 영역 안에서 **정확히 한 번** 나와야 한다 → 아니면 `REGION-AMBIGUOUS`로 중단
2. 같은 문구를 같은 값으로 여러 번 바꿔야 하면 `REGION_ALLOW_MULTI`에 등록
3. **웹(`client.js`)과 데스크톱 헬퍼(`shared-core.js`) 양쪽**에 적용 —
   한쪽만 고치면 데스크톱 펫에 중문이 남습니다

작업 중 대사 127개는 양이 많아 [tool_copy_map.json](tool_copy_map.json)으로 분리했습니다.

```
node check_todo_ko.mjs
```
```
WEEKDAYS: "일", "월", "화", "수", "목", "금", "토"
  due_null         "기한 없음"
  remaining_soon   "2시간 남음"
  span_day         "5일"
RESULT: OK — 할 일 포맷이 전부 한국어
```

## 말도 한국어로

메뉴·UI와 별개로, 펫이 하는 말은 `~/.dsh/dsh-pet/main-config.jsonc`에서 설정합니다.

```jsonc
{
  "pets": [
    {
      "id": "main",
      "name": "파란 머리 메이드",
      "whisperPrompt": "너는 주인 책상 위에 사는 작고 귀여운 파란 머리 메이드야. 반드시 한국어로만 말하고, 자연스럽고 짧게 20자 이내로. …"
    }
  ],
  "sleepRefuseTexts": ["자는데 방해하지 마……", "으응…… 조금만 더 잘게."],
  "sleepStartTexts": ["너무 졸려…… 나 먼저 잘게."],
  "sleepEndTexts": ["으응…… 일어났어."],
  "workStatusTexts": [["다음 단계를 고민 중이야"], ["작업 처리 중이야"], ["이 단계는 정리했어"]]
}
```

`whisperPrompt`는 모델에게 주는 인성이므로, 한국어로만 답하라는 지시를 넣으면 됩니다.
`workStatusTexts`는 6단계(생각 / 작업 / 정리 / 대기 / 성공 / 오류) 고정 문구입니다.

## 알려진 제한

- **업데이트하면 패치가 사라집니다.** dsh-pet을 업데이트/재설치하면 파일이 교체되므로 `patch_dsh_pet_ko.py`를 다시 실행하세요. `--check`로 상태 확인 가능.
- **짤 이미지 안의 글자는 여전히 중국어**입니다. 그림 파일이라 번역 대상이 아닙니다.
- **날씨는 외부 API 3곳에 의존합니다** — `ip-api.com`(위치), `bigdatacloud.net`(한국어 지명),
  `open-meteo.com`(날씨). 어디든 막히면 해당 부분만 원래 동작(중문/영문 지명)으로 돌아갑니다.
- **개발자용 메시지는 번역하지 않았습니다** — provider 등록 검증 오류, 내부 로그,
  잔액 provider 예외 문구. 화면에 보이지 않고 플러그인 개발자의 디버깅용입니다.
- 패치 후 dsh-pet 내부 구조가 바뀌면 `ANCHOR-MISS` / `HARDCODED-AMBIGUOUS` / `WMO-MISS` /
  `GEO-ANCHOR-MISS` / `REGION-AMBIGUOUS` / `TOOL-MISS`가 날 수 있습니다.
  그때는 `--check` 출력을 보고 이슈로 알려 주세요.
- **비공식 패치**입니다. dsh-pet 원저작자와 무관하며, 문제는 이 저장소로 주세요.

## 크레딧

- [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet) — 원본 플러그인 (코드 MIT)
- [jjoni12/dsh-locale-ko](https://github.com/jjoni12/dsh-locale-ko) — DSH 한국어 언어팩 (이 패치의 전제)
- 펫 이미지 "大肥鱼"는 커뮤니티 2차창작이며 **비상업** 조건입니다. 이 저장소는 표시 문자열만 다루고 원본 애셋을 재배포하지 않습니다.

## 라이선스

이 패치 스크립트: MIT

적용 대상인 dsh-pet의 애셋(애니메이션·밈 이미지)은 비상업 조건이며, 이 저장소에 포함되지 않습니다.
