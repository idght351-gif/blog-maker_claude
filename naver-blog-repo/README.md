# 은똥이의 먹보여행 — 네이버 블로그 글쓰기 자동화

사진(+짧은 메모)을 주면 기존 블로그 스타일과 검색 데이터에 맞춰 리뷰를 쓰고, **네이버 블로그 임시저장까지** 자동으로 하는 도구 모음입니다. 발행은 사람이 직접 합니다.

- 블로그: `blog.naver.com/seoeunjin13` (카테고리 `먹보여행`)
- 글쓰기 규칙: [`STYLE.md`](STYLE.md) ← 가장 중요한 문서
- 진행 상황·결정 사항: [`HANDOFF.md`](HANDOFF.md), [`CONVERSATION_LOG.md`](CONVERSATION_LOG.md)

---

## 1. 준비 (새 컴퓨터에서 한 번)

```bash
# 파이썬 패키지
pip install -r requirements.txt
# 브라우저 자동화 (Node.js 18+ 필요)
npm install
npx playwright install chromium
# (선택) Claude Code용 Playwright 스킬
npm install -g @playwright/cli@latest && playwright-cli install --skills
```

### 환경 변수 (비밀 정보 — 절대 깃에 올리지 않기)
| 이름 | 용도 |
|---|---|
| `NAVER_AD_API_KEY`, `NAVER_AD_SECRET`, `NAVER_AD_CUSTOMER_ID` | 네이버 검색광고 API → 키워드 월간 검색수 (searchad.naver.com → 도구 → API 사용 관리) |
| `NAVER_ID`, `NAVER_PW` | (선택) 비밀번호 로그인용. 해외 IP에서는 캡차가 떠서 **QR 로그인 권장** |
| `NAVER_STATE_DIR` | (선택) 로그인 상태 저장 폴더. 기본값은 저장소 안 `.state/` (깃 제외) |

### 네이버 로그인 (QR)
```bash
node automation/qr_login.js
```
`.state/shots/qr.png`에 QR 화면이 저장됩니다 → 휴대폰 **네이버 앱 → 검색창 옆 렌즈 → QR 스캔** → 화면에 나온 숫자 선택. 로그인 상태는 `.state/naver-state.json`에 저장되고 이후 모든 스크립트가 이걸 씁니다.

---

## 2. 글 한 편 만드는 순서

| 단계 | 명령 / 방법 | 설명 |
|---|---|---|
| 1. 사진 받기 | Google Drive `블로그` 폴더 → `scripts/decode_drive.py` | HEIC → JPG (`photos/<가게>/jpg/`) |
| 2. 얼굴 모자이크 | `python3 scripts/blur_faces.py photos/<가게>/jpg <출력폴더>` | 초상권 필수. 애매한 후보(`review_*.jpg`)는 눈으로 확인 후 `apply_review` |
| 3. 영상 → GIF | `python3 scripts/make_gif.py <영상> <출력.gif> [시작초] [길이초]` | 3~4초, 720px |
| 4. 가게 조사 | 네이버 검색 상위 블로그 10개 (`data/research/<가게>/`) | 빈 정보는 2개 이상 글에서 겹치는 내용만 |
| 5. 키워드 | `python3 scripts/keyword_volume.py "지역 맛집" "지역 업종"` | 검색광고 API 월간 검색수 (키 없으면 자동완성) |
| 6. 초안 작성 | `drafts/build_<가게>.py` (쿠로카메 파일을 복사해서 시작) | `python3 drafts/build_<가게>.py` → 미리보기 HTML |
| 7. 규칙 점검 | `python3 scripts/lint_post.py drafts/build_<가게>.py` | 27개 항목 통과까지 수정 |
| 8. 입력 순서표 | `python3 scripts/make_spec3.py drafts/build_<가게>.py drafts/<가게>_upload drafts/<가게>_spec3.json` | 사진은 1600px로 미리 만들어 둠 |
| 9. 임시저장 | `node automation/write_draft3.js drafts/<가게>_spec3.json <제목 문구>` | 검증(빠진 줄 0·순서·인용구·장소) 통과 시에만 저장 |
| 10. 보정 | `automation/fix_draft.js`, `save_draft.js` | 장소·정렬이 빠졌을 때 |
| 11. 앱에서 마무리 | 블로그 앱 | **맨 위 '위치 추가'(앱 전용)**, 영수증 인증, 발행 |

---

## 3. 폴더 구조

```
STYLE.md                    글쓰기 규칙 (학습 결과 + 사용자 지시, v4)
HANDOFF.md                  진행 상태·주의사항
CONVERSATION_LOG.md         지금까지 요청·결정 정리
scripts/
  collect.py                블로그 글 수집 (python3 scripts/collect.py seoeunjin13)
  analyze_posts.py          다른 블로그 글 구조 분석
  keyword_volume.py         검색량(검색광고 API)·자동완성
  lint_post.py              초안 규칙 점검 (27개 항목)
  make_spec3.py             초안 → 에디터 입력 순서표
  blur_faces.py             얼굴 모자이크 (사진·영상)
  make_gif.py               영상 → GIF
  decode_drive.py           Drive 다운로드 결과 → HEIC → JPG
automation/                 네이버 에디터 자동화 (Playwright)
  qr_login.js               QR 로그인 (권장)
  write_draft3.js           임시저장 입력기 (현재 방식)
  fix_draft.js / save_draft.js / resave_and_delete.js / delete_draft.js
  fetch_views.js            블로그 통계: 글별 조회수
  fetch_search_kw.js        블로그 통계: 유입 검색어
  fetch_referer.js          블로그 통계: 유입 경로
  login.js, login2.js       비밀번호 로그인 (해외 IP는 캡차 → 비권장)
  write_draft.js, write_draft2.js   이전 버전 (기록용)
  probes/                   기능 확인용 시험 스크립트
drafts/
  build_kurokame.py         쿠로카메 초안 (내용 + 미리보기 생성) ← 새 글의 견본
  kurokame.md / kurokame.html   초안 텍스트 / 미리보기
  kurokame_spec3.json       에디터 입력 순서표
data/
  index.json                197개 글 목록 (협찬 여부, 공감, 댓글, 실제 조회수 등)
  tiers.json                학습 순위 (실제 조회수 기준)
  views.json                글별 조회수 (블로그 통계)
  search_keywords.json      유입 검색어 (주간 상위 20 × 25주)
  posts_all.json            197개 글 구조 데이터 (글번호 → 내용)
  research/kurokame/        쿠로카메 상위 블로그 10개, 키워드 검색량
  research/popular/         인기 맛집 글 40개 분석, 검색 화면 구조, 내 글 순위
models/yunet.onnx           얼굴 인식 모델
```

깃에 **올리지 않는 것** (`.gitignore`): 사진·영상 원본(`photos/`, `drafts/*_upload/`), 블로그 원본 HTML(`raw/`, `collect.py`로 다시 받기), 로그인 상태(`.state/`).

---

## 4. 꼭 알아둘 주의사항
- 글쓰기 화면의 **"작성 중인 글을 이어서 쓸까요?" 창에서 '취소'를 누르면 그 글이 지워집니다.** 입력기들은 이 창이 뜨면 이어쓰기로 열어 제목을 확인하고, 시험 글이 아니면 아무것도 바꾸지 않고 멈춥니다.
- 네이버 에디터에 글자를 빠르게 직접 입력하면 한글이 사라집니다 → 본문은 **서식 붙여넣기**, 제목은 **한 글자씩 입력**.
- 맨 위 **'위치 추가'는 블로그 앱 전용**(PC 웹 불가). 맨 아래 장소 지도는 PC에서 자동.
- **내돈내산 방문 인증**은 영수증 리뷰(MY플레이스)를 먼저 해야 목록에 나타납니다. 있으면 입력기가 글 맨 위에 붙입니다.
- 발행은 자동화하지 않습니다.
