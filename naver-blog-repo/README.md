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

### 구글 드라이브 연결 (Drive API, 처음 한 번)
1. https://console.cloud.google.com → 새 프로젝트 → **API 및 서비스 → 라이브러리 → Google Drive API 사용**
2. **OAuth 동의 화면**: 외부(External), 앱 이름 아무거나, 테스트 사용자에 본인 구글 계정 추가
3. **사용자 인증 정보 → OAuth 클라이언트 ID → 애플리케이션 유형 "데스크톱 앱"** → JSON 다운로드
4. 받은 JSON을 `.state/google-credentials.json` 으로 저장 (깃에 안 올라감)
5. `node automation/drive.js auth` → 브라우저에서 로그인·허용
6. `node automation/drive.js init` → 내 드라이브에 `1_빈폴더` ~ `5_빈폴더` 생성
7. `powershell -ExecutionPolicy Bypass -File automation\register_cleanup_task.ps1` → 매일 정리 작업 등록

### 사진 폴더 흐름 — 번호로 부르기 (사용자 지시 2026-11-12)
폴더 이름은 항상 `<번호>_빈폴더` 또는 `<번호>_<가게이름>` 입니다.

| 사용자가 하는 말 | Claude가 하는 일 | 폴더 이름 |
|---|---|---|
| **"2번 사진 업로드"** | 사진을 보고 가게 이름 판단 → `drive.js claim 2 <가게>` → `drive.js download 2 photos/<가게>/raw` → **바로 글쓰기 시작** → 영수증 있으면 영수증 리뷰 등록(확인 없이) → 임시저장 → 내돈내산 카드 → `drive.js done 2` | `2_빈폴더` → `2_<가게>` |
| **"3번 사진 업로드"인데 폴더에 영수증만 있을 때** | 영수증에서 가게 확인 → `drive.js receipt 3 <가게>` → 영수증 리뷰 등록(`receipt_review.js --submit`) → `node automation/edit_nds.js <가게>` (발행된 예전 글을 찾아 **썸네일 바로 아래**에 영수증 인증 카드 추가 → **수정 발행**) → "등록했어요" 보고 | `3_빈폴더` → `3_<가게>` |
| 영수증 등록 보고에 사용자가 피드백 | `drive.js feedback 3` → **피드백 받은 날부터 3일 뒤** 자동으로 비움 | → `3_빈폴더` |
| **"1번 블로그 등록"** | `drive.js clear 1` — 블로그 RSS에서 발행 확인 → 같은 번호로 빈 폴더 새로 만들고 공유(은똥) 복사 → 예전 폴더째 휴지통 | `1_<가게>` → `1_빈폴더` |
| (폰 클라우드 세션) | 클라우드 환경 변수 `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` 이 있으면 PC와 똑같이 `drive.js` 사용. 작업 기록은 드라이브 폴더 설명에 저장. 저장소 맨 위 `CLAUDE.md`·`.claude/settings.json`은 `repo_root/`에서 관리 (`push_github.ps1`이 맨 위로 올림) | |
| (클라우드·폰 세션에서 drive.js를 못 쓸 때) | 드라이브 커넥터로 **파일 목록 조회·파일별 삭제 금지**. `search_files`로 번호 폴더 ID만 찾고 → `trash_file`(폴더 ID 한 번) → `create_file`(title `N_빈폴더`, contentMimeType `application/vnd.google-apps.folder`). 호출 3번으로 끝 | |
| (말 안 해도) 임시저장 3일 뒤부터 매일 10시 | `drive.js cleanup` — 발행 확인된 것만 위와 같이 정리 | |

- 발행이 안 보이면 지우지 않습니다. 지운 파일은 드라이브 휴지통에서 30일 안에 복구할 수 있습니다.
- 상태 보기: `drive.js status`. 폴더가 모자라면 `drive.js init 8`처럼 개수를 늘립니다.

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
| 11. 영수증 리뷰 | `node automation/receipt_review.js <영수증.jpg> <가게> <리뷰.txt> <음식사진.jpg> --submit` (환경 변수 `RR_STEPS='["^다음$"]'`, `RR_PICK`=방문 정보·키워드 목록) | 사용자 지시: 확인 없이 바로 등록 |
| 12. 내돈내산 카드 | `node automation/add_nds.js <제목 문구> <가게>` | 임시저장 글 맨 위에 카드 추가 후 저장 |
| 13. 썸네일 | `drafts/<가게>_thumb.json` 작성 → `node automation/make_thumb.js drafts/<가게>_thumb.json photos/<가게>/thumb/thumbnail.jpg` → `node automation/add_thumb.js <제목 문구> photos/<가게>/thumb/thumbnail.jpg` | 기존 썸네일 스타일(손글씨 가게명♥·분홍 리본·말풍선·반짝이·워터마크)로 1080px 정사각형 생성 → **최상단(내돈내산 카드 위)**에 넣고 대표 사진 지정 후 저장. 반드시 12번 다음에 실행 |
| 13-1. 발행 글 썸네일 교체 | `node automation/edit_thumb.js <가게> <새 썸네일.jpg> [--dry] [--category 먹보여행]` | 첫 사진 삭제 → 새 썸네일 맨 위·대표 지정 → 수정 발행 |
| 14. 앱에서 마무리 | 블로그 앱 | **맨 위 '위치 추가'(앱 전용)**, 발행 |

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
