# 네이버 블로그 자동화 (폰 앱 클라우드 세션)

작업 폴더는 `naver-blog-repo/`. 흐름·명령은 `naver-blog-repo/README.md`, 글 스타일은 `naver-blog-repo/STYLE.md`.
사용자는 모든 작업을 휴대폰 Claude 앱으로 한다. 토큰을 아끼는 것이 중요하다.

## 구글 드라이브: 토큰 아끼기 규칙
- 드라이브 작업은 `node naver-blog-repo/automation/drive.js <명령>` 한 줄로 끝낸다.
  Google Drive 커넥터로 파일 목록 조회, 파일별 다운로드, 파일별 삭제를 하지 않는다.
- "N번 사진 업로드" → `drive.js download N naver-blog-repo/photos/<임시>/raw` → 사진은 전부 열지 말고 영수증·간판·대표 몇 장만 봐서 가게를 판단 → `drive.js claim N <가게>` → 글쓰기 (README 표 순서).
- "N번 블로그 등록" → `drive.js clear N` (RSS로 발행 확인 → 새 `N_빈폴더` 만들고 예전 폴더의 공유(은똥 편집자)를 그대로 복사 → 예전 폴더째 휴지통).
- 임시저장 끝 → `drive.js done N`, 영수증 등록 피드백 → `drive.js feedback N`. 기록은 드라이브 폴더 설명에 저장돼서 세션이 바뀌어도 남는다.
- 세션 시작 때 `drive.js cleanup`이 자동 실행된다 (정리 예정일이 지났고 발행이 확인된 폴더만 비움).
- drive.js가 토큰·환경 변수 오류를 내면, 커넥터는 폴더 단위로만 쓴다: `search_files`로 번호 폴더 ID 찾기 → `trash_file`(폴더 ID) → `create_file`(title `N_빈폴더`, contentMimeType `application/vnd.google-apps.folder`) → 예전 폴더의 공유 대상을 `get_file_permissions`로 확인해 새 폴더에 같은 권한으로 공유 (메일 주소를 파일에 적지 않기). 그리고 사용자에게 환경 변수 확인을 부탁한다.
