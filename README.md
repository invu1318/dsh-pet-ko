# dsh-pet-ko

[dsh-pet](https://github.com/PC2005-cloud/dsh-pet)을 **한국어**로 쓰기 위한 패치입니다.

dsh-pet은 UI 로케일을 zh / en / ja / es / fr / de / ru / pt만 지원합니다. 우클릭 메뉴 라벨은
로케일이 아니라 번들에 하드코딩되어 있고, 설정 페이지·펫 대화 패널은 자체 로케일 사전을 쓰는데
거기에 `ko`가 없습니다. 이 저장소는 **두 곳 모두** 한국어로 바꿉니다.

> 펫이 **하는 말**(혼잣말·대화·잠꼬대·작업 상태)은 이 패치가 아니라 `main-config.jsonc`에서
> `whisperPrompt` 등으로 설정합니다. 아래 [말도 한국어로](#말도-한국어로) 참고.

## 무엇이 바뀌나

### 1. 우클릭 메뉴

메뉴 트리 **163개 노드**, 번역 대상 **175개 항목**이 한국어가 됩니다.

| 영역 | 전 | 후 |
|---|---|---|
| 루트 메뉴 | 查看余额 · 待办事项 · 碎碎念 · 对话 · 睡觉 | 잔액 보기 · 할 일 · 혼잣말 · 대화 · 자기 |
| 표시 위치 | 显示位置 ▸ 仅网页 / 仅桌面 / 两者 / 都不 | 표시 위치 ▸ 웹만 / 데스크톱만 / 둘 다 / 모두 끔 |
| 동작 트리 | 动作 ▸ 待机 / 转向 / 拖拽 / 点击回应 / 移动 / 小动作 / 玩耍 / 吃什么 / 时节 / 文字 | 동작 ▸ 대기 / 방향 전환 / 드래그 / 클릭 반응 / 이동 / 잔동작 / 놀이 / 먹기 / 절기 / 글자 |
| 애니메이션 114개 | 待机呼吸休闲 · 东张西望 · 吃白饭 … | 대기 숨쉬기 · 두리번두리번 · 쌀밥 먹기 … |
| 짤(밈) 27개 | 大的要来啦 · 就一碗 · 可爱 … | 큰 거 온다 · 한 그릇만 · 귀여움 … |
| 단축키 힌트 | `L 键` · `1 键` | `L 키` · `1 키` |
| 트레이 | 退出 | 종료 |

### 2. 설정 페이지 · 펫 대화 패널

`pet.config` **218키**, `pet.chat` **50키** — 합계 **268개 문자열**이 한국어로 나옵니다.

| 영역 | 전(영어로 폴백) | 후 |
|---|---|---|
| 탭 이름 | Pet Config | 펫 설정 |
| 펫 설정 카드 | Size (width px) · Name · Persona (optional) | 크기(가로 px) · 이름 · 페르소나(선택) |
| 전역 스위치 | System notifications · Click sound · System tray | 시스템 알림 · 클릭음 · 시스템 트레이 |
| 물리 · 글꼴 | Gravity · Bounciness · Font size (px) | 중력 · 반발력 · 글꼴 크기(px) |
| 모델 설정 | Follow current conversation · Chat history rounds | 현재 대화 따르기 · 대화 기록 라운드 |
| 대화 패널 | Say something… · Load earlier · Persona | 무슨 말이든 해보세요… · 이전 대화 불러오기 · 페르소나 |

여기에 더해 `t()`를 우회하던 중문 9곳(아바타 업로드 오류, 테스트 알림 문구,
CJK 구분자 `、`·`：` 등)도 한국어·한국어 구두점으로 바꿉니다.

## 요구 사항

- Python 3.8+
- dsh-pet이 설치된 DSH 프로필 (기본 `desktop`)
- 한국어 로케일 활성화 — [dsh-locale-ko](https://github.com/jjoni12/dsh-locale-ko)
  (DSH 프로필의 로케일 목록에 `한국어`가 보이면 이미 된 상태입니다)

패치는 `$DSH_HOME/profiles/desktop/node_modules/dsh-pet` 아래 파일 3개를 직접 수정합니다.

## 사용법

```powershell
$env:DSH_HOME = "$env:USERPROFILE\.dsh"

python patch_dsh_pet_ko.py --check    # 먼저 확인 (파일은 건드리지 않음)
python patch_dsh_pet_ko.py            # 적용
python verify_dsh_pet_ko.py           # 검증
```

그 다음 펫을 재시작합니다.

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:13302/dsh-pet-7340/reload -Method Post
```

- **데스크톱 펫**: 위 `reload`로 즉시 반영
- **웹 화면의 펫 · 설정 페이지**: 브라우저 **새로고침(F5)** 필요 (클라이언트 번들은 페이지 로드 시 내려감)

> DSH 웹 포트가 13302가 아니면 `POST /dsh-pet-7340/reload`의 포트만 맞춰 주세요.

### 확인 출력 예시

```
$ python patch_dsh_pet_ko.py --check
client       WOULD-PATCH(label=2,hint=1)
shared-core  WOULD-PATCH(label=2,hint=1)
tray         WOULD-PATCH
locale       WOULD-PATCH(ns=2,hardcoded=9)

$ python verify_dsh_pet_ko.py
client       175 entries
shared-core  175 entries
config source : live /dsh-pet-7340/config
required names: 175
translated    : 175
missing       : 0
values with Han: 0

[locale] pet.config: 218 키 (누락 0, 초과 0, 한자 0, 플레이스홀더 0)

[locale] pet.chat: 50 키 (누락 0, 초과 0, 한자 0, 플레이스홀더 0)

RESULT: OK — 메뉴 라벨과 설정·대화 UI가 모두 한국어입니다
```

### 되돌리기

```powershell
python patch_dsh_pet_ko.py --revert
```

두 패치 모두 마커 블록(`__DSH_PET_KO__`, `// ---- dsh-pet ko locale patch`)을 주입하는
방식이라, 원복은 그 블록 제거로 끝납니다. 로케일 패치만 되돌리면 파일이 **바이트 단위로**
원본과 일치하는 것을 확인했습니다. dsh-pet을 재설치해도 원래대로 돌아갑니다.

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
- 패치 후 dsh-pet 내부 구조가 바뀌면 `ANCHOR-MISS` / `HARDCODED-MISS`가 날 수 있습니다. 그때는 `--check` 출력을 보고 이슈로 알려 주세요.
- **비공식 패치**입니다. dsh-pet 원저작자와 무관하며, 문제는 이 저장소로 주세요.

## 크레딧

- [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet) — 원본 플러그인 (코드 MIT)
- [jjoni12/dsh-locale-ko](https://github.com/jjoni12/dsh-locale-ko) — DSH 한국어 언어팩 (이 패치의 전제)
- 펫 이미지 "大肥鱼"는 커뮤니티 2차창작이며 **비상업** 조건입니다. 이 저장소는 표시 문자열만 다루고 원본 애셋을 재배포하지 않습니다.

## 라이선스

이 패치 스크립트: MIT

적용 대상인 dsh-pet의 애셋(애니메이션·밈 이미지)은 비상업 조건이며, 이 저장소에 포함되지 않습니다.
