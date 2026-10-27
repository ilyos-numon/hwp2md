# vendor — 동봉한 외부 자원

모두 내려받은 원본을 수정하지 않고 그대로 둔다. 외부 CDN 을 부르지 않도록 서버가 `/static/vendor/...` 로 직접 제공한다.
(Pyodide 는 예외로 계속 CDN 에서 불러온다 — `pyodide-runner.js` 참고)

| 파일 | 원본 URL | 버전 | SHA-256 | 라이선스 |
|------|----------|------|---------|----------|
| `marked.min.js` | https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js | 12.0.2 | `15fabce5b65898b32b03f5ed25e9f891a729ad4c0d6d877110a7744aa847a894` | MIT (`marked.LICENSE.md`) |
| `marked.LICENSE.md` | https://cdn.jsdelivr.net/npm/marked@12.0.2/LICENSE.md | 12.0.2 | `8e3a3f82f59a60958f56ca08f445647c32a4733dc7ca6c2c46f6eb898471ab9c` | MIT 원문 |
| `gsap/gsap.min.js` | https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js | 3.13.0 | `96c01b81f44a3290e2b4532f55e2c9534b2adc43273a19f3756b2cb41f0fd0b6` | GSAP Standard "no charge" (`gsap/LICENSE.md`) |
| `gsap/ScrollTrigger.min.js` | https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js | 3.13.0 | `308219390e5e3b84cda0c481e70caa9820883ae10bda44e6e9a149a81aac4b3f` | GSAP Standard "no charge" |
| `gsap/SplitText.min.js` | https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/SplitText.min.js | 3.13.0 | `5e519ea2470faa15ca4d4f27e9263e5906c07c034a9b4771164dee108136563a` | GSAP Standard "no charge" |
| `gsap/ScrambleTextPlugin.min.js` | https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrambleTextPlugin.min.js | 3.13.0 | `e9ce04a07d932d8506f21a0db0e394ce526f69b9f1a93c70b64de3b823daa452` | GSAP Standard "no charge" |
| `fonts/PretendardVariable.woff2` | https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2 | 1.3.9 | `9599f12fd42fc0bce1cd50b47a0c022e108d7aa64dd0d1bb0ed44f3282d900b4` | SIL OFL 1.1 (`fonts/OFL-Pretendard.txt`) |
| `fonts/OFL-Pretendard.txt` | https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/LICENSE.txt | 1.3.9 | `b04538c9abec39a3db75108cf0af0fd9c77032fe8aa2cf38345b4d250e98e38e` | SIL OFL 1.1 원문 |
| `fonts/JetBrainsMono-Regular.woff2` | https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/fonts/webfonts/JetBrainsMono-Regular.woff2 | v2.304 | `a9cb1cd82332b23a47e3a1239d25d13c86d16c4220695e34b243effa999f45f2` | SIL OFL 1.1 (`fonts/OFL-JetBrainsMono.txt`) |
| `fonts/JetBrainsMono-Medium.woff2` | https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/fonts/webfonts/JetBrainsMono-Medium.woff2 | v2.304 | `086c48dfbea9ddaff1320f7e09399b8e2924e88ce67453721255db3bdbb5a353` | SIL OFL 1.1 |
| `fonts/JetBrainsMono-SemiBold.woff2` | https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/fonts/webfonts/JetBrainsMono-SemiBold.woff2 | v2.304 | `918edad542a1da608fd2ba8daebaff9ac802309103fe760eed465b8b4e47faf1` | SIL OFL 1.1 |
| `fonts/OFL-JetBrainsMono.txt` | https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304/OFL.txt | v2.304 | `30f0c136e3c88e422d0791acd97238870f9054a9729bc34cf2ff0d4ed8cac4ad` | SIL OFL 1.1 원문 |
| `fonts/fonts.css` | (이 저장소에서 작성) | — | — | 이 저장소 라이선스 |

글꼴은 `fonts/fonts.css` 의 `@font-face` 로 선언한다 ("Pretendard Variable" 100–900, "JetBrains Mono" 400/500/600).
`marked.min.js` 는 이 단계 이전부터 있던 파일이며 교체하지 않았다.
