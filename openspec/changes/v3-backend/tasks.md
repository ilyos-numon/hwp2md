# Tasks

## 1. 외부 자원 동봉

- [x] 1.1 GSAP 3.13.0 스크립트 4개와 라이선스 안내를 `static/vendor/gsap/` 에 둔다
- [x] 1.2 Pretendard Variable·JetBrains Mono woff2 와 OFL 전문, `fonts.css` 를 `static/vendor/fonts/` 에 두거나 실패 경로(시스템 글꼴)로 기록한다
- [x] 1.3 marked MIT 라이선스 파일과 `vendor/README.md`(원본 URL·버전·SHA-256)를 쓴다

## 2. 변환 화면

- [x] 2.1 V3 `base.css`·`app.css`·`theme.js` 를 `static/` 아래로 옮긴다
- [x] 2.2 `static/index.html` 을 V3 변환 화면으로 바꾼다 (vendor 자원, 데모 제거, 절대경로)
- [x] 2.3 `static/js/app.js` 에 실제 MODES 를 연결하고 모션 제약을 지키며, 이전 `static/app.js`·`static/style.css` 를 지운다

## 3. 소개 페이지

- [x] 3.1 `static/about.html`·`landing.css`·`effects.js`·`landing.js` 를 vendor 자원과 서버 경로로 옮긴다
- [x] 3.2 `app.py` 에 `GET /about` 을 추가하고 단위 테스트를 더한다

## 4. 문서

- [x] 4.1 README·`docs/feature-reference.md` §9·`docs/decisions.md`·`NOTICE`·`design/v3/README.md` 를 새 구조에 맞춘다

## 5. 검증

- [ ] 5.1 `tests/e2e/test_web_v3.py` (외부 요청 0, 성공·오류·소개·다크·좁은 화면, 스크린샷)를 쓴다
- [ ] 5.2 LINT·TYPECHECK·TEST·E2E 전체·wheel 내용·sanitize 를 실행해 로그를 남긴다
- [ ] 5.3 diff·스크린샷 리뷰와 RESULT 기록
