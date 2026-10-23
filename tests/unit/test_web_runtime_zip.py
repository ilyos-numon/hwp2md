import io
import zipfile

import pytest
from starlette.testclient import TestClient

from hwp2md.web.app import build_runtime_zip, create_app

HANCOM_NOTICE = (
    "본 제품은 한글과컴퓨터의 한/글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다."
)

NEW_MODULES = (
    "hwp2md/hwpml/reader.py",
    "hwp2md/equation/__init__.py",
    "hwp2md/hwp5/aes.py",
    "hwp2md/ole.py",
    "hwp2md/skips.py",
)


@pytest.mark.parametrize("name", NEW_MODULES)
def test_runtime_zip_contains_new_module(name: str) -> None:
    with zipfile.ZipFile(io.BytesIO(build_runtime_zip())) as zf:
        assert name in zf.namelist()


def test_index_has_hancom_notice_and_skipped_region() -> None:
    with TestClient(create_app()) as client:
        resp = client.get("/")
    assert resp.status_code == 200
    assert HANCOM_NOTICE in resp.text
    assert 'id="skipped"' in resp.text
    assert '<div id="skipped" role="status" hidden></div>' in resp.text
