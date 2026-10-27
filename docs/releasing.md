# 릴리스 절차

PyPI 배포 이름은 `hwp2markdown`, 콘솔 명령·import 이름은 `hwp2md` 다. 게시는 GitHub Actions(`.github/workflows/release.yml`, 이름 `Release`)가 PyPI Trusted Publishing 으로 한다. 저장소에 API 토큰을 두지 않는다.

## 처음 한 번: 수동 설정

| # | 작업 | 위치 | 값 |
|---|------|------|----|
| U1 | PyPI 계정 2FA 확인 후 pending publisher 등록 | pypi.org → Account settings → Publishing → Add a new pending publisher (GitHub) | PyPI Project Name `hwp2markdown` · Owner = 저장소 소유 계정(origin URL 의 첫 경로 조각) · Repository name `hwp2md` · Workflow name `release.yml` · Environment name `pypi` |
| U2 | GitHub environment 생성 | 저장소 Settings → Environments → New environment | 이름 `pypi`. (선택) Deployment branches and tags → 태그 규칙 `v*.*.*` |
| U3 | 릴리스 승인 | 릴리스 게이트에서 게시 여부 확인 | "v0.1.0 게시 승인" |
| U4 | (필요 시) gh 토큰에 workflow scope 추가 | 터미널 `gh auth refresh -h github.com -s workflow` (저장소 소유 계정으로) | push 가 workflow scope 로 거절될 때만 |

## 워크플로우

- `CI` (`.github/workflows/ci.yml`): 모든 브랜치 push 와 pull request 에서 돈다. 태그 push 로는 돌지 않는다. job 은 `lint`·`typecheck`·`unit (3.11)`·`unit (3.13)`·`e2e`·`dist`. 단위·E2E 는 `-m "not real_samples"` 로 저장소에 없는 실제 샘플 테스트를 제외한다. `dist` 는 `uv build` → `twine check --strict` → `scripts/check_dist.py` 로 배포물을 검사한다.
- `Release` (`.github/workflows/release.yml`): `v*.*.*` 태그 push 에서만 돈다.
  - `build`: 단위 테스트 → `uv build --out-dir dist` → `twine check --strict` → `scripts/check_dist.py dist --tag <태그>` (태그와 패키지 버전이 다르면 실패) → artifact `dist` 업로드.
  - `publish`: `build` 뒤에 environment `pypi` 에서 `pypa/gh-action-pypi-publish@release/v1` 로 게시한다.
  - `binaries`: `build` 뒤에 4개 러너(`windows-2022`·`macos-15`·`macos-15-intel`·`ubuntu-22.04`)에서 `uv run --with pyinstaller==6.22.3 python scripts/build_binary.py --out build/bin` 으로 실행 파일을 만들고, `HWP2MD_BINARY` 를 지정해 `tests/e2e/test_binary_smoke.py` 를 돌린 뒤 artifact `bin-<platform>` 으로 올린다. 자산 이름은 `hwp2md-windows-x64.exe`·`hwp2md-macos-arm64`·`hwp2md-macos-x64`·`hwp2md-linux-x64` 이고 버전을 넣지 않는다.
  - `github-release`: `binaries`·`publish` 가 모두 성공한 뒤 실행 파일 4개와 `SHA256SUMS`(`sha256sum hwp2md-* | sort -k2`)를 태그의 GitHub Release 에 올린다. Release 가 없으면 만들고(`--generate-notes`), 있으면 `--clobber` 로 덮어쓴다. 이 job 만 `contents: write` 권한을 갖는다.

## 릴리스 순서

1. `src/hwp2md/__init__.py` 의 `__version__` 을 올린다 (버전은 이 한 곳에만 있다). 커밋하고 main 에 push 한다.
2. main 의 `CI` 가 전부 성공(green)인지 확인한다.
3. 로컬에서 미리 확인한다 (선택):
   ```bash
   uv build --out-dir dist
   uvx --from 'twine>=6.1' twine check --strict dist/*
   uv run python scripts/check_dist.py dist --tag vX.Y.Z
   ```
4. 태그를 만들고 push 한다.
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```
5. GitHub Actions 에서 `Release` 실행의 `build`·`publish`·`binaries`(4개)·`github-release` 가 성공했는지 확인하고, https://pypi.org/project/hwp2markdown/ 에서 새 버전을, https://github.com/ilyos-numon/hwp2md/releases/latest 에서 자산 5개(실행 파일 4개 + `SHA256SUMS`)를 확인한다.
6. Homebrew 탭을 갱신한다. 탭 저장소는 `ilyos-numon/homebrew-tap` 이고 로컬 작업 위치는 `build/homebrew-tap` 이다(`build/` 는 커밋하지 않는다). formula 는 Release 의 `SHA256SUMS` 로 생성하며 직접 고치지 않는다.
   ```bash
   git clone https://github.com/ilyos-numon/homebrew-tap.git build/homebrew-tap   # 처음 한 번
   uv run python scripts/update_formula.py --version X.Y.Z --out build/homebrew-tap/Formula/hwp2md.rb
   cd build/homebrew-tap
   git add Formula/hwp2md.rb && git commit -m "hwp2md X.Y.Z" && git push origin main
   brew update && brew upgrade hwp2md && brew test hwp2md   # 확인
   ```
   탭 README 원본은 `packaging/homebrew/README.md` 다. 바꿨으면 탭의 `README.md` 로 복사해 같이 커밋한다.

## 실패 대응

- `build` 가 `version-mismatch` 로 실패: 태그와 `__version__` 이 다르다. 태그를 지우고 맞는 커밋에 다시 태그한다.
  ```bash
  git tag -d vX.Y.Z
  git push origin :refs/tags/vX.Y.Z
  # __version__ 을 고친 커밋에서
  git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z
  ```
- `build` 의 다른 검사(단위 테스트·twine·check_dist) 실패: 원인을 고쳐 main 에 반영하고, 위와 같이 태그를 지운 뒤 다시 태그한다.
- `publish` 실패 (Trusted Publishing 오류): U1 의 Owner·Repository·Workflow·Environment 값과 U2 environment 이름 `pypi` 가 정확한지 확인한 뒤, Actions 에서 실패한 job 을 다시 실행한다.
- `binaries` 실패: 일시적 오류(러너 대기열·네트워크)면 Actions 에서 실패한 job 만 다시 실행한다. `github-release` 도 그 뒤 다시 돈다. 코드 수정이 필요하면 고쳐 main 에 반영하고, 위와 같이 태그를 지운 뒤 다시 태그한다. 이때 `publish` 가 이미 성공했다면 같은 버전은 PyPI 에 다시 올릴 수 없으므로 `__version__` 을 올린 새 버전으로 릴리스한다.
- `github-release` 실패: `binaries`·`publish` 가 모두 성공했는지 확인하고 job 을 다시 실행한다. 이미 올라간 자산은 `--clobber` 로 덮어쓴다.
- `macos-15-intel` 러너가 없어지거나 계속 대기하면: `release.yml` 의 matrix 에서 `macos-x64` 행을 빼고, `scripts/update_formula.py` 의 필수 자산과 formula 의 `on_macos` → `on_intel` 블록에서 `hwp2md-macos-x64` 를 빼는 후속 변경을 한다. README 의 실행 파일 표와 `docs/decisions.md` 도 함께 고친다.
- PyPI 는 같은 버전을 다시 올릴 수 없다 (삭제한 버전도 마찬가지). 이미 게시된 버전에 문제가 있으면 `__version__` 을 올려 새 버전으로 다시 릴리스한다.

## GitHub Pages

- 브라우저 체험 사이트(https://ilyos-numon.github.io/hwp2md/)는 `Pages` 워크플로우(`.github/workflows/pages.yml`)가 main push 때 빌드·배포한다. 수동 실행(workflow_dispatch)도 된다.
- 저장소가 비공개면 `build` job 을 건너뛴다 (Pages 는 공개 저장소에서만 켠다).
- 로컬 빌드: `uv run python scripts/build_pages.py --out dist-pages` (출력: `.nojekyll`·`index.html`(소개)·`convert.html`(변환)·`static/`·`pkg/hwp2md.zip`).
- 로컬 미리보기: `python -m http.server 8771 --directory dist-pages` 후 http://localhost:8771/ 을 연다. 사이트 안의 경로는 모두 상대 경로라 `/hwp2md/` 같은 하위 경로에서도 같게 동작한다.
