# 워드프레스 구축 진행표 (휴대폰으로 따라하기)

블로그 이름: **백호 머니** / 도메인: **baekhomoney.com** (2026-11-18 미등록 확인)
다음 세션은 이 표에서 [ ] 첫 칸부터 이어서 안내한다. 완료되면 [x]로 바꾸고 커밋.

- [x] 1. Cloudflare 가입 + baekhomoney.com 구매 (2026-11-18 등록, 만료 2027-11-18) (해외결제 카드 안 되면 가비아로 대체)
- [x] 2. (완료 2026-11-18, 호스팅 아이디 baekhomoney) 카페24 **뉴매니지드 워드프레스 호스팅 스타트업** 신청 (월 500원/1년 약정 450원, 설치비 5,000원, SSD 700MB, 트래픽 1.6GB/일). 애드센스 워드프레스(1,980원~, AdSense for Platforms·AI 자동글)는 이전 시 애드센스 연동 문제 우려로 제외. 카페24 회원 아이디는 beakhomoney(철자 주의)
- [x] 3. (완료 2026-11-19, A 레코드·접속·wp-json 응답 확인) Cloudflare DNS(A @·www → 183.111.138.226, 프록시 끔=회색 구름) + 카페24에 baekhomoney.com·www 연결 (카페24 서버 IP는 baekhomoney.mycafe24.com 조회값)
- [ ] 4. SSL(https) 확인(카페24 인증서관리) → 워드프레스 설정>일반 주소 2개를 https://baekhomoney.com 으로 변경 (현재 내부 링크가 baekhomoney.mycafe24.com)
- [ ] 5. 고유주소(퍼머링크) = 글 이름, 사이트 제목·언어·시간대 설정
- [ ] 6. 테마(GeneratePress 또는 Kadence) + 플러그인(Rank Math, UpdraftPlus) 설치
- [ ] 7. Application Password 발급 → 보안 입력창으로 저장 → Claude 연결 테스트(임시저장 1건)
- [ ] 8. 필수 페이지: 소개·운영자 소개·문의·개인정보처리방침
- [ ] 9. 구글 서치 콘솔(도메인 속성, DNS TXT) + 사이트맵 제출
- [ ] 10. 첫 글(SCHD) 임시저장 → 검수 → 발행
