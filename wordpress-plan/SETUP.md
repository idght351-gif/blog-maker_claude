# 워드프레스 구축 진행표 (휴대폰으로 따라하기)

블로그 이름: **백호 머니** / 도메인: **baekhomoney.com** (2026-11-18 미등록 확인)
다음 세션은 이 표에서 [ ] 첫 칸부터 이어서 안내한다. 완료되면 [x]로 바꾸고 커밋.

- [x] 1. Cloudflare 가입 + baekhomoney.com 구매 (2026-11-18 등록, 만료 2027-11-18) (해외결제 카드 안 되면 가비아로 대체)
- [x] 2. (완료 2026-11-18, 호스팅 아이디 baekhomoney) 카페24 **뉴매니지드 워드프레스 호스팅 스타트업** 신청 (월 500원/1년 약정 450원, 설치비 5,000원, SSD 700MB, 트래픽 1.6GB/일). 애드센스 워드프레스(1,980원~, AdSense for Platforms·AI 자동글)는 이전 시 애드센스 연동 문제 우려로 제외. 카페24 회원 아이디는 beakhomoney(철자 주의)
- [x] 3. (완료 2026-11-19, A 레코드·접속·wp-json 응답 확인) Cloudflare DNS(A @·www → 183.111.138.226, 프록시 끔=회색 구름) + 카페24에 baekhomoney.com·www 연결 (카페24 서버 IP는 baekhomoney.mycafe24.com 조회값)
- [x] 4. (SSL 발급·대표도메인 완료 2026-11-19, 사이트주소 https 자동변경됨) 남은 것: 설정>일반 워드프레스 주소(siteurl)를 https로, 사이트 제목 백호 머니. http→https 자동 이동은 6단계 플러그인으로
- [x] 5. (완료 2026-11-19, 제목 백호 머니·서울·https 확인) 고유주소(퍼머링크) = 글 이름, 사이트 제목·언어·시간대 설정
- [x] 6. (완료 2026-11-19, http→https 301 확인. 카페24 기본 플러그인: WP Super Cache·Two Factor·NinjaFirewall·WPForce Logout·Complianz) 테마(GeneratePress 또는 Kadence) + 플러그인(Rank Math, UpdraftPlus) 설치
- [x] 7. (완료 2026-11-19) Application Password(claude) → request_credential로 baekhomoney.com Basic 인증 저장(프록시 자동 주입, 값 모름). REST 인증·임시저장(글 id 7)·이미지 업로드 테스트 성공
- [x] 8. (완료 2026-11-19) 페이지 발행: 소개(/about) 운영자 소개(/author-profile) 문의(/contact) 개인정보처리방침(/privacy-policy) 면책 고지(/disclaimer). 운영자=직장인 백호(직장인 개인투자자, 5년+), 문의=개인 Gmail 공개(사용자 선택). 작성자 slug baekho, 태그라인, 카테고리 7개, 주 메뉴. 스크립트 automation/setup_pages.py·setup_site.py
- [ ] 9. 구글 서치 콘솔(도메인 속성, DNS TXT) + 사이트맵 제출
- [ ] 10. 첫 글(SCHD) 임시저장 → 검수 → 발행

## 자동화 메모
- REST: `curl https://baekhomoney.com/wp-json/wp/v2/...` 인증 헤더 없이 호출하면 프록시가 Basic 인증을 넣어 줌.
- 글은 항상 `"status":"draft"`로만 올린다. 발행은 사용자가 검수 후 직접.
- 이미지: `POST /wp/v2/media` (Content-Disposition 파일명 + Content-Type image/webp).
- 카테고리(ETF 종류만, 2026-11-19 사용자 결정): 배당 ETF 2, 성장 ETF 3, 안전자산 ETF 4(채권·금·원자재). 가이드·포트폴리오는 리포트 안 항목이라 카테고리 아님.
- 태그 ID: 미국상장 9, 국내상장 10, 연금저축 11, ISA 12, IRP 13, 월배당 14, 커버드콜 15, 채권 16, 금 17, 원자재 18. 주 메뉴 ID 8 (배당·성장·안전자산·국내상장 ETF·소개).
- REST 도우미: `python3 wordpress-plan/automation/wp.py GET /posts` (automation 폴더에서 실행)
