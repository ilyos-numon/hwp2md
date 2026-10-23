import os
from pathlib import Path

import pytest

import hwp2md
from hwp2md import convert, convert_bytes
from hwp2md.convert import read_blocks
from hwp2md.detect import detect_format
from hwp2md.errors import (
    DrmProtectedError,
    EncryptedDocumentError,
    Hwp2mdError,
    NotHwpFileError,
    UnsupportedHwpError,
)
from hwp2md.memory import STATUS_BY_CODE, convert_to_response, error_code
from synth_hwp5 import FIXTURE_PARAGRAPHS, build_hwp5
from synth_hwpx import build_zip, hwpx_entries

NS_ODF = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"


def _drm_bytes() -> bytes:
    return b"\x9b\x20" + b"DRMONE  " + os.urandom(4000)


def _encrypted_manifest() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<odf:manifest xmlns:odf="{NS_ODF}">'
        '<odf:file-entry odf:full-path="Contents/section0.xml" odf:media-type="text/xml">'
        '<odf:encryption-data odf:checksum-type="SHA1" odf:checksum="AAAA">'
        '<odf:algorithm odf:algorithm-name="AES"/>'
        "</odf:encryption-data></odf:file-entry></odf:manifest>"
    ).encode()


def _plain_manifest() -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<odf:manifest xmlns:odf="{NS_ODF}">'
        '<odf:file-entry odf:full-path="Contents/section0.xml" odf:media-type="text/xml"/>'
        "</odf:manifest>"
    ).encode()


def _hwpx_with_manifest(manifest: bytes) -> bytes:
    entries = hwpx_entries(FIXTURE_PARAGRAPHS)
    entries["META-INF/manifest.xml"] = manifest
    return build_zip(entries)


# --- 예외 계층 ---


@pytest.mark.parametrize("cls", [DrmProtectedError, EncryptedDocumentError])
def test_protection_errors_are_unsupported(cls: type[Exception]) -> None:
    assert issubclass(cls, UnsupportedHwpError)
    assert issubclass(cls, Hwp2mdError)


def test_package_exports_protection_errors() -> None:
    assert hwp2md.DrmProtectedError is DrmProtectedError
    assert hwp2md.EncryptedDocumentError is EncryptedDocumentError
    assert "DrmProtectedError" in hwp2md.__all__
    assert "EncryptedDocumentError" in hwp2md.__all__


# --- DRM 래핑 서명 ---


def test_drm_signature_bytes() -> None:
    with pytest.raises(DrmProtectedError, match=r"^DRM-protected document: <memory>$"):
        detect_format(_drm_bytes())


def test_drm_signature_path(tmp_path: Path) -> None:
    path = tmp_path / "wrapped.hwp"
    path.write_bytes(_drm_bytes())
    with pytest.raises(DrmProtectedError, match="DRM-protected document: "):
        detect_format(path)
    out = tmp_path / "out"
    out.mkdir()
    with pytest.raises(DrmProtectedError):
        convert(path, out)
    assert list(out.iterdir()) == []


def test_drm_prefix_only() -> None:
    with pytest.raises(DrmProtectedError):
        read_blocks(b"\x9b\x20" + b"\x00" * 100)


def test_drm_marker_within_64_bytes() -> None:
    data = b"x" * 50 + b"DRMONE" + b"y" * 100
    with pytest.raises(DrmProtectedError):
        read_blocks(data)


def test_drm_marker_after_64_bytes_is_not_hwp() -> None:
    data = b"x" * 64 + b"DRMONE" + b"y" * 100
    with pytest.raises(NotHwpFileError) as info:
        read_blocks(data)
    assert not isinstance(info.value, UnsupportedHwpError)


def test_drm_convert_to_response() -> None:
    status, body = convert_to_response(_drm_bytes(), "x.hwp")
    assert status == 415
    assert body["error"]["code"] == "drm"
    assert set(body) == {"error"}


# --- HWP 5.0 FileHeader 속성 ---


def test_hwp5_encrypted_bit() -> None:
    with pytest.raises(EncryptedDocumentError, match=r"^encrypted document: <memory>$"):
        read_blocks(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x3))


@pytest.mark.parametrize("properties", [0x11, 0x401, 0x10, 0x400])
def test_hwp5_drm_bits(properties: int) -> None:
    with pytest.raises(DrmProtectedError, match=r"^DRM-protected document: <memory>$"):
        read_blocks(build_hwp5(FIXTURE_PARAGRAPHS, properties=properties))


def test_hwp5_encrypted_bit_checked_before_drm() -> None:
    with pytest.raises(EncryptedDocumentError):
        read_blocks(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x13))


def test_hwp5_drm_bit_path(tmp_path: Path) -> None:
    path = tmp_path / "drm.hwp"
    path.write_bytes(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x11))
    with pytest.raises(DrmProtectedError, match=f"DRM-protected document: {path}"):
        read_blocks(path)


def test_hwp5_distribution_still_unsupported() -> None:
    with pytest.raises(UnsupportedHwpError) as info:
        read_blocks(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x5))
    assert not isinstance(info.value, (DrmProtectedError, EncryptedDocumentError))
    status, body = convert_to_response(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x5), "x.hwp")
    assert (status, body["error"]["code"]) == (415, "unsupported")


def test_hwp5_plain_still_converts() -> None:
    assert convert_bytes(build_hwp5(FIXTURE_PARAGRAPHS, properties=0x1), "x.hwp").markdown


@pytest.mark.parametrize(
    ("properties", "code"),
    [(0x3, "encrypted"), (0x11, "drm"), (0x401, "drm")],
)
def test_hwp5_convert_to_response(properties: int, code: str) -> None:
    status, body = convert_to_response(build_hwp5(FIXTURE_PARAGRAPHS, properties=properties), "x")
    assert status == 415
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str)


# --- HWPX 암호화 매니페스트 ---


def test_hwpx_encrypted_manifest() -> None:
    with pytest.raises(EncryptedDocumentError, match=r"^encrypted document: <memory>$"):
        read_blocks(_hwpx_with_manifest(_encrypted_manifest()))


def test_hwpx_encrypted_manifest_path(tmp_path: Path) -> None:
    path = tmp_path / "enc.hwpx"
    path.write_bytes(_hwpx_with_manifest(_encrypted_manifest()))
    with pytest.raises(EncryptedDocumentError):
        read_blocks(path)


def test_hwpx_encryption_data_without_namespace() -> None:
    manifest = b"<manifest><file-entry><encryption-data/></file-entry></manifest>"
    with pytest.raises(EncryptedDocumentError):
        read_blocks(_hwpx_with_manifest(manifest))


def test_hwpx_plain_manifest_converts() -> None:
    assert read_blocks(_hwpx_with_manifest(_plain_manifest()))


def test_hwpx_encrypted_convert_to_response() -> None:
    status, body = convert_to_response(_hwpx_with_manifest(_encrypted_manifest()), "x.hwpx")
    assert status == 415
    assert body["error"]["code"] == "encrypted"


# --- 오류 코드 ---


def test_status_by_code_protection() -> None:
    assert STATUS_BY_CODE["drm"] == 415
    assert STATUS_BY_CODE["encrypted"] == 415


def test_error_code_prefers_subclass() -> None:
    assert error_code(DrmProtectedError("e")) == "drm"
    assert error_code(EncryptedDocumentError("e")) == "encrypted"
    assert error_code(UnsupportedHwpError("e")) == "unsupported"
