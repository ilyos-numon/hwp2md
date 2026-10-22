# Tasks

## 1. 블록 모델·이미지 네이밍·렌더·변환 결과

- [x] 1.1 `Image(file_name, data)` 블록과 `images.py`(`image_dir_name`, `sniff_ext`, `normalize_ext`, `ImageNamer`)를 추가하고 `tests/unit/test_images.py`의 네이밍·확장자 케이스가 통과하는지 확인한다
- [x] 1.2 `render_blocks(blocks, *, image_dir="")`가 `Image`를 `![그림 N](dir/file)`(공백 → `%20`)로 렌더하도록 바꾸고 렌더 단위 테스트(순번·빈 image_dir·공백 경로)가 통과하는지 확인한다
- [x] 1.3 `convert()`가 고유 `file_name`마다 `<out>/<stem>_images/`에 파일을 쓰고 `ConvertResult.image_count/image_dir/image_files`를 채우도록 바꾸고, 이미지 없는 기존 fixture에서 폴더가 생기지 않고 `image_count == 0`인 테스트와 기존 단위 테스트 171개가 통과하는지 확인한다

## 2. 합성 HWP 5.0 fixture

- [x] 2.1 `SynthImage`·`collect_images`·`build_bin_data`·`build_picture_control`·`build_cfb` BinData 스토리지 확장과 공용 fixture 4종(`FIXTURE_ITEMS_IMAGES`, `_IMAGE_REUSE`, `_IMAGE_IN_CELL`, `_IMAGE_MISSING`)을 추가하고, `tests/unit/test_synth_hwp5.py`의 구조 테스트(BIN_DATA 레코드 필드, `BinData/BIN0001.png` 스트림 바이트, 그림 레코드 offset 71 값, 레코드 level)가 통과하는지 확인한다
- [x] 2.2 이미지 없는 기존 fixture 6종의 `build_hwp5` sha256과 `build_docinfo()` 30바이트가 변하지 않았음을 기존 테스트로 확인한다

## 3. HWP 5.0 리더

- [x] 3.1 `records.py` 상수(`HWPTAG_BIN_DATA`, `HWPTAG_SHAPE_COMPONENT`, `HWPTAG_SHAPE_COMPONENT_PICTURE`, `CTRL_ID_GSO`)와 `docinfo.py`의 `BinDataEntry`·`parse_bin_data`·`DocInfo.bin_data`를 추가하고 `tests/unit/test_hwp5_bindata.py`의 파싱·잘림 케이스가 통과하는지 확인한다
- [x] 3.2 `reader.py`에 `Hwp5Package`·`read_hwp5_package`(BinData 스트림 수집)·`BinDataStore.resolve`(스트림 탐색·압축 해제 규칙·캐시)를 추가하고 압축/비압축·누락·LINK 케이스 테스트가 통과하는지 확인한다
- [x] 3.3 `body.py`에 `parse_picture_bindata_id`와 `gso` 분기(`_parse_gso`), 셀 단락 `bin_data=None`, flatten의 `Image` 무시를 넣고 `read_blocks`가 fixture 4종에서 `EXPECTED_BLOCKS_IMAGE*`와 같은지 확인한다

## 4. 합성 HWPX fixture

- [x] 4.1 `synth_hwpx.py`에 `pic_paragraph_xml`(`hp:pic/hc:img@binaryItemIDRef`), 셀 안 그림, manifest `opf:item`, `BinData/image{k}.{ext}` 엔트리(`missing` 제외)를 추가하고 `tests/unit/test_synth_hwpx.py`의 구조 테스트가 통과하는지 확인한다
- [x] 4.2 이미지 없는 기존 fixture 3종의 `build_hwpx` sha256과 `content.hpf` 바이트가 변하지 않았음을 기존 테스트로 확인한다

## 5. HWPX 리더

- [x] 5.1 `hwpx/bindata.py`(`parse_manifest`, `BinItemStore.resolve`)와 `reader.py`의 `HwpxPackage`·`read_hwpx_package`(BinData 엔트리 수집, 50MB 상한)를 추가하고 `tests/unit/test_hwpx_bindata.py`의 manifest·fallback·누락·과대 케이스가 통과하는지 확인한다
- [x] 5.2 `body.py`가 `hp:pic`·`hp:container` 안 `hp:pic`을 `Image`로 바꾸고 `hp:ctrl`·셀 안은 제외하도록 바꾸고, `read_blocks`가 fixture 4종에서 `EXPECTED_BLOCKS_IMAGE*`와 같은지 확인한다
- [x] 5.3 `tests/unit/test_cross_format.py`에 이미지 fixture 4종의 두 포맷 Markdown·카운트·파일 바이트 동일성 테스트를 추가하고 통과하는지 확인한다

## 6. 문서

- [x] 6.1 `docs/decisions.md`에 결정 3건(이미지 블록·파일명·링크 규칙 / 제외 범위 / BinData 해석·압축 규칙), `README.md` "현재 지원"과 실행 예시의 `_images/` 설명, `tests/fixtures/README.md`에 이미지 기대값 안내를 적고 `sanitize-check.sh`가 OK인지 확인한다

## 7. CLI

- [ ] 7.1 `cli.py` 2행에 이미지 ≥1일 때 ` · 이미지 K개`, 3행 `  이미지: <dir>/ (n files)`를 추가하고 합성 이미지 fixture 수동 실행으로 3행 출력과 이미지 없는 fixture의 2행 불변을 확인한다

## 8. E2E

- [ ] 8.1 `tests/e2e/test_cli_image.py`(두 포맷 성공·재사용·셀 제외·누락·2행 불변·비압축·실제 샘플 5개)를 작성하고 기존 E2E 정규식 3줄(`test_cli_convert.py:79`, `test_cli_heading.py:45`, `test_cli_hwpx.py:32`)에 `(?: · 이미지 \d+개)?`를 추가한다
- [ ] 8.2 `uv run pytest tests/e2e -q`가 45 passed·failed 0이고 증거 파일(`image_hwp5.md`, `image_hwpx.md`, 실제 샘플 `.md` 5개, `img_001.png`)이 `ILLY_SHOT_DIR`에 있는지 확인한다

## 9. 리뷰·기록

- [ ] 9.1 reviewer가 diff와 증거 파일(PNG를 직접 열어 확인)을 성공 기준 표와 대조하고, scribe가 `RESULT.md`·`.ai/STATE.md`를 기록한다
