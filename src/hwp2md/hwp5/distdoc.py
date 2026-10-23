"""HWP 5.0 배포용 문서 ViewText 스트림 복호 (한컴 공개 문서 절차)."""

from __future__ import annotations

import struct

from ..errors import UnsupportedHwpError
from .aes import aes128_ecb_decrypt

HWPTAG_DISTRIBUTE_DOC_DATA = 0x1C  # 28
_DOC_DATA_SIZE = 256
_KEY_SIZE = 16


def _msvc_rand(seed: int) -> list[int]:
    """MSVC srand(seed) 후 rand() 로 256B 난수 배열을 만든다.
    홀수 번째 rand() & 0xFF = 값, 짝수 번째 (rand() & 0xF) + 1 = 반복 횟수."""
    state = seed & 0xFFFFFFFF
    out: list[int] = []
    while len(out) < _DOC_DATA_SIZE:
        state = (state * 214013 + 2531011) & 0xFFFFFFFF
        value = ((state >> 16) & 0x7FFF) & 0xFF
        state = (state * 214013 + 2531011) & 0xFFFFFFFF
        count = (((state >> 16) & 0x7FFF) & 0x0F) + 1
        out.extend([value] * count)
    return out[:_DOC_DATA_SIZE]


def distribution_key(record_payload: bytes) -> bytes:
    """DISTRIBUTE_DOC_DATA 256B → AES-128 키 16B.
    seed = 앞 4B UINT32 LE, 오프셋 4 이후를 마스크로 XOR, 키 = 4 + (seed & 0xF) 부터 16B."""
    if len(record_payload) != _DOC_DATA_SIZE:
        raise UnsupportedHwpError("distribution document: bad header")
    (seed,) = struct.unpack_from("<I", record_payload, 0)
    mask = _msvc_rand(seed)
    offset = 4 + (seed & 0xF)
    return bytes(record_payload[i] ^ mask[i] for i in range(offset, offset + _KEY_SIZE))


def decrypt_view_text(stream: bytes) -> bytes:
    """ViewText/Section<N> 스트림 → 복호한 (압축 상태 그대로의) 섹션 바이트."""
    if len(stream) < 4:
        raise UnsupportedHwpError("distribution document: bad header")
    (header,) = struct.unpack_from("<I", stream, 0)
    tag_id = header & 0x3FF
    size = (header >> 20) & 0xFFF
    if tag_id != HWPTAG_DISTRIBUTE_DOC_DATA or size != _DOC_DATA_SIZE:
        raise UnsupportedHwpError("distribution document: bad header")
    start = 4 + _DOC_DATA_SIZE
    if len(stream) < start:
        raise UnsupportedHwpError("distribution document: bad header")
    key = distribution_key(bytes(stream[4:start]))
    body = stream[start:]
    usable = len(body) - len(body) % 16
    return aes128_ecb_decrypt(key, bytes(body[:usable]))
