# dsh-pet-ko

[dsh-pet](https://github.com/PC2005-cloud/dsh-pet) 우클릭 메뉴를 **한국어**로 바꾸는 패치입니다.

dsh-pet은 UI 로케일을 zh / en / ja / es / fr / de / ru / pt만 지원하고, 우클릭 메뉴 라벨은
로케일이 아니라 번들에 하드코딩되어 있습니다. 이 저장소는 그 라벨들을 한국어로 바꿉니다.

> 펫이 **하는 말**(혼잣말·대화·잠꼬대·작업 상태)은 이 패치가 아니라 `main-config.jsonc`에서
> `whisperPrompt` 등으로 설정합니다. 아래 [말도 한국어로](#말도-한국어로) 참고.

## 무엇이 바뀌나

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

## 요구 사항

- Python 3.8+
- dsh-pet이 설치된 DSH 프로필 (기본 `desktop`)

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
- **웹 화면의 펫**: 브라우저 **새로고침(F5)** 필요 (클라이언트 번들은 페이지 로드 시 내려감)

> DSH 웹 포트가 13302가 아니면 `POST /dsh-pet-7340/reload`의 포트만 맞춰 주세요.

### 확인 출력 예시

```
$ python patch_dsh_pet_ko.py --check
client       WOULD-PATCH(label=2,hint=1)
shared-core  WOULD-PATCH(label=2,hint=1)
tray         WOULD-PATCH

$ python verify_dsh_pet_ko.py
client       175 entries
shared-core  175 entries
config source : live /dsh-pet-7340/config
required names: 175
translated    : 175
missing       : 0
values with Han: 0

RESULT: OK — 메뉴 라벨이 전부 한국어입니다
```

### 되돌리기

```powershell
python patch_dsh_pet_ko.py --revert
```

패치는 `__DSH_PET_KO__` 마커 블록을 주입하는 방식이라, 원복은 그 블록 제거로 끝납니다.
dsh-pet을 재설치해도 원래대로 돌아갑니다.

## 어떻게 동작하나

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

### 안전성

**메뉴 트리 구조는 건드리지 않습니다.** 라벨은 순수 표시용이고, 실제 동작은 다른 필드가 결정합니다.

| 용도 | 필드 | 패치 영향 |
|---|---|---|
| 애니메이션 재생 | `node.anim` — 원본 중국어 이름 그대로 | 없음 |
| 짤 전송 | `node.image` — 원본 이름 그대로 | 없음 |
| 사전에 없는 문자열 | 그대로 표시 (fallback) | 없음 |

따라서 표시명을 바꿔도 재생·전송·파일 탐색은 영향받지 않습니다.

## 말도 한국어로

메뉴와 별개로, 펫이 하는 말은 `~/.dsh/dsh-pet/main-config.jsonc`에서 설정합니다.

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
- 패치 후 dsh-pet 내부 구조가 바뀌면 `ANCHOR-MISS`가 날 수 있습니다. 그때는 `--check` 출력을 보고 이슈로 알려 주세요.
- **비공식 패치**입니다. dsh-pet 원저작자와 무관하며, 문제는 이 저장소로 주세요.

## 크레딧

- [PC2005-cloud/dsh-pet](https://github.com/PC2005-cloud/dsh-pet) — 원본 플러그인 (코드 MIT)
- 펫 이미지 "大肥鱼"는 커뮤니티 2차창작이며 **비상업** 조건입니다. 이 저장소는 표시 문자열만 다루고 원본 애셋을 재배포하지 않습니다.

## 라이선스

이 패치 스크립트: MIT

적용 대상인 dsh-pet의 애셋(애니메이션·밈 이미지)은 비상업 조건이며, 이 저장소에 포함되지 않습니다.
