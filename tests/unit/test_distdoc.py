import struct
import time

import pytest

from hwp2md.errors import UnsupportedHwpError
from hwp2md.hwp5.aes import aes128_ecb_decrypt
from hwp2md.hwp5.distdoc import (
    HWPTAG_DISTRIBUTE_DOC_DATA,
    decrypt_view_text,
    distribution_key,
)
from synth_distdoc import (
    aes128_ecb_encrypt,
    build_distribute_doc_data,
    encrypt_view_text,
)

# FIPS-197 Appendix C.1 (AES-128)
FIPS_KEY = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
FIPS_PLAIN = bytes.fromhex("00112233445566778899aabbccddeeff")
FIPS_CIPHER = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")


def test_fips197_c1_decrypt() -> None:
    assert aes128_ecb_decrypt(FIPS_KEY, FIPS_CIPHER) == FIPS_PLAIN


def test_fips197_c1_encrypt_helper() -> None:
    assert aes128_ecb_encrypt(FIPS_KEY, FIPS_PLAIN) == FIPS_CIPHER


def test_ecb_multi_block_roundtrip() -> None:
    key = bytes(range(100, 116))
    data = bytes((i * 31 + 7) & 0xFF for i in range(16 * 9))
    assert aes128_ecb_decrypt(key, aes128_ecb_encrypt(key, data)) == data


def test_ecb_empty() -> None:
    assert aes128_ecb_decrypt(FIPS_KEY, b"") == b""


@pytest.mark.parametrize(
    ("key", "data"),
    [(b"\x00" * 15, b"\x00" * 16), (b"\x00" * 17, b"\x00" * 16), (FIPS_KEY, b"\x00" * 15)],
)
def test_aes_bad_lengths(key: bytes, data: bytes) -> None:
    with pytest.raises(ValueError):
        aes128_ecb_decrypt(key, data)


def test_tag_constant() -> None:
    assert HWPTAG_DISTRIBUTE_DOC_DATA == 0x1C


@pytest.mark.parametrize("seed", [0x2A7F3C11, 0x00000000, 0xFFFFFFFF, 0x12345670, 0x8765432F])
def test_distribution_key_roundtrip(seed: int) -> None:
    key = bytes((seed + i * 13) & 0xFF for i in range(16))
    payload = build_distribute_doc_data(seed, key)
    assert len(payload) == 256
    assert payload[:4] == struct.pack("<I", seed)
    assert distribution_key(payload) == key


def test_distribution_key_offset_boundaries_differ() -> None:
    # seed & 0xF == 0 → 오프셋 4, == 15 → 오프셋 19
    key = bytes(range(16))
    p0 = build_distribute_doc_data(0x10, key)
    p15 = build_distribute_doc_data(0x1F, key)
    assert distribution_key(p0) == key
    assert distribution_key(p15) == key


@pytest.mark.parametrize("size", [0, 1, 15, 16, 17, 1000])
def test_decrypt_view_text_roundtrip(size: int) -> None:
    section = bytes((i * 5 + 1) & 0xFF for i in range(size))
    stream = encrypt_view_text(section)
    plain = decrypt_view_text(stream)
    assert plain[:size] == section
    assert len(plain) == size + (-size % 16)


def test_decrypt_view_text_custom_seed_and_key() -> None:
    section = b"hello distribution" * 3
    stream = encrypt_view_text(section, seed=0x0BADF00F, key=b"K" * 16)
    assert decrypt_view_text(stream)[: len(section)] == section


def test_decrypt_view_text_ignores_trailing_partial_block() -> None:
    section = bytes(range(32))
    stream = encrypt_view_text(section) + b"\x01\x02\x03"
    assert decrypt_view_text(stream) == section


def _header(tag: int, size: int) -> bytes:
    return struct.pack("<I", tag | (size << 20))


@pytest.mark.parametrize(
    "stream",
    [
        b"",
        b"\x1c\x00",
        _header(0x1B, 256) + b"\x00" * 256,
        _header(0x1C, 255) + b"\x00" * 256,
        _header(0x1C, 256) + b"\x00" * 100,
    ],
)
def test_decrypt_view_text_bad_header(stream: bytes) -> None:
    with pytest.raises(UnsupportedHwpError, match="distribution document: bad header"):
        decrypt_view_text(stream)


def test_decrypt_1mb_timing() -> None:
    data = bytes((i * 131 + 17) & 0xFF for i in range(1 << 20))
    start = time.perf_counter()
    out = aes128_ecb_decrypt(FIPS_KEY, data)
    elapsed = time.perf_counter() - start
    print(f"\n[s8] aes128_ecb_decrypt 1MB: {elapsed:.3f}s")
    assert len(out) == len(data)
    assert elapsed <= 10.0
