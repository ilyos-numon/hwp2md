"""Synthetic HWP 5.0 distribution-document (배포용 문서) helpers. Test-only.

정방향 AES-128 ECB 와 DISTRIBUTE_DOC_DATA 역 XOR 로 ViewText 스트림을 만든다.
"""

from __future__ import annotations

import struct

from hwp2md.hwp5.aes import SBOX, expand_key
from hwp2md.hwp5.distdoc import HWPTAG_DISTRIBUTE_DOC_DATA

DOC_DATA_SIZE = 256


def _xtime(a: int) -> int:
    a <<= 1
    return (a ^ 0x11B) & 0xFF if a & 0x100 else a


def _encrypt_block(round_keys: list[bytes], block: bytes) -> bytes:
    s = [b ^ k for b, k in zip(block, round_keys[0], strict=True)]
    for rnd in range(1, 11):
        s = [SBOX[b] for b in s]
        # ShiftRows (state 는 열 우선: s[c*4 + r])
        s = [s[((c + r) % 4) * 4 + r] for c in range(4) for r in range(4)]
        if rnd != 10:
            mixed: list[int] = []
            for c in range(4):
                a = s[c * 4 : c * 4 + 4]
                t = a[0] ^ a[1] ^ a[2] ^ a[3]
                mixed.extend(a[r] ^ t ^ _xtime(a[r] ^ a[(r + 1) % 4]) for r in range(4))
            s = mixed
        s = [b ^ k for b, k in zip(s, round_keys[rnd], strict=True)]
    return bytes(s)


def aes128_ecb_encrypt(key: bytes, data: bytes) -> bytes:
    """테스트용 정방향 AES-128 ECB (FIPS-197 §5.1)."""
    if len(key) != 16 or len(data) % 16 != 0:
        raise ValueError("bad key or data length")
    words = expand_key(key)
    round_keys = [struct.pack(">4I", *words[4 * r : 4 * r + 4]) for r in range(11)]
    return b"".join(_encrypt_block(round_keys, data[i : i + 16]) for i in range(0, len(data), 16))


def _mask(seed: int) -> bytes:
    state = seed & 0xFFFFFFFF
    out = bytearray()

    def rand() -> int:
        nonlocal state
        state = (state * 214013 + 2531011) & 0xFFFFFFFF
        return (state >> 16) & 0x7FFF

    while len(out) < DOC_DATA_SIZE:
        value = rand() & 0xFF
        count = (rand() & 0x0F) + 1
        out += bytes([value]) * count
    return bytes(out[:DOC_DATA_SIZE])


def build_distribute_doc_data(seed: int, key: bytes) -> bytes:
    """256B DISTRIBUTE_DOC_DATA payload. 평문(seed + 채움 + 키) 을 오프셋 4 이후만 XOR."""
    if len(key) != 16:
        raise ValueError("key must be 16 bytes")
    plain = bytearray((i * 7 + 3) & 0xFF for i in range(DOC_DATA_SIZE))
    plain[0:4] = struct.pack("<I", seed & 0xFFFFFFFF)
    offset = 4 + (seed & 0xF)
    plain[offset : offset + 16] = key
    mask = _mask(seed)
    for i in range(4, DOC_DATA_SIZE):
        plain[i] ^= mask[i]
    return bytes(plain)


def encrypt_view_text(
    section: bytes, *, seed: int = 0x2A7F3C11, key: bytes = bytes(range(16))
) -> bytes:
    """레코드 헤더(평문) + 256B DISTRIBUTE_DOC_DATA + AES(section, 0 패딩)."""
    header = struct.pack("<I", HWPTAG_DISTRIBUTE_DOC_DATA | (DOC_DATA_SIZE << 20))
    padded = section + b"\x00" * (-len(section) % 16)
    return header + build_distribute_doc_data(seed, key) + aes128_ecb_encrypt(key, padded)
