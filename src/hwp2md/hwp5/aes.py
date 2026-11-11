"""Pure-Python AES-128 ECB decryption (FIPS-197 equivalent inverse cipher, T-tables)."""

from __future__ import annotations

import struct


def _xtime(a: int) -> int:
    a <<= 1
    return (a ^ 0x11B) & 0xFF if a & 0x100 else a


def _gmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xtime(a)
        b >>= 1
    return r


def _build_sboxes() -> tuple[list[int], list[int]]:
    inv = [0] * 256
    for x in range(1, 256):
        for y in range(1, 256):
            if _gmul(x, y) == 1:
                inv[x] = y
                break
    sbox = [0] * 256
    for x in range(256):
        b = inv[x]
        s = b
        for shift in range(1, 5):
            s ^= ((b << shift) | (b >> (8 - shift))) & 0xFF
        sbox[x] = s ^ 0x63
    inv_sbox = [0] * 256
    for x, s in enumerate(sbox):
        inv_sbox[s] = x
    return sbox, inv_sbox


SBOX, INV_SBOX = _build_sboxes()


def _rotr8(w: int) -> int:
    return ((w >> 8) | (w << 24)) & 0xFFFFFFFF


def _build_td() -> tuple[list[int], list[int], list[int], list[int]]:
    td0 = []
    for x in range(256):
        s = INV_SBOX[x]
        td0.append(
            (_gmul(s, 0x0E) << 24) | (_gmul(s, 0x09) << 16) | (_gmul(s, 0x0D) << 8) | _gmul(s, 0x0B)
        )
    td1 = [_rotr8(w) for w in td0]
    td2 = [_rotr8(w) for w in td1]
    td3 = [_rotr8(w) for w in td2]
    return td0, td1, td2, td3


_TD0, _TD1, _TD2, _TD3 = _build_td()
_RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def expand_key(key: bytes) -> list[int]:
    """AES-128 key expansion → 44 big-endian words (FIPS-197 §5.2)."""
    if len(key) != 16:
        raise ValueError("AES-128 key must be 16 bytes")
    w = list(struct.unpack(">4I", key))
    for i in range(4, 44):
        t = w[i - 1]
        if i % 4 == 0:
            t = ((t << 8) | (t >> 24)) & 0xFFFFFFFF
            t = (
                (SBOX[t >> 24] << 24)
                | (SBOX[(t >> 16) & 0xFF] << 16)
                | (SBOX[(t >> 8) & 0xFF] << 8)
                | SBOX[t & 0xFF]
            ) ^ (_RCON[i // 4 - 1] << 24)
        w.append(w[i - 4] ^ t)
    return w


def _inv_mix_word(w: int) -> int:
    # InvMixColumns(w) == Td(Sbox(byte)) 조합
    return (
        _TD0[SBOX[w >> 24]]
        ^ _TD1[SBOX[(w >> 16) & 0xFF]]
        ^ _TD2[SBOX[(w >> 8) & 0xFF]]
        ^ _TD3[SBOX[w & 0xFF]]
    )


def _decrypt_round_keys(key: bytes) -> list[int]:
    w = expand_key(key)
    dk: list[int] = []
    for r in range(10, -1, -1):
        words = w[4 * r : 4 * r + 4]
        if 0 < r < 10:
            words = [_inv_mix_word(x) for x in words]
        dk.extend(words)
    return dk


def aes128_ecb_decrypt(key: bytes, data: bytes) -> bytes:
    """AES-128 ECB 복호. len(key)!=16 또는 len(data)%16!=0 → ValueError."""
    if len(key) != 16:
        raise ValueError("AES-128 key must be 16 bytes")
    if len(data) % 16 != 0:
        raise ValueError("AES-128 ECB data length must be a multiple of 16")
    dk = _decrypt_round_keys(key)
    td0, td1, td2, td3, isb = _TD0, _TD1, _TD2, _TD3, INV_SBOX
    k0, k1, k2, k3 = dk[0:4]
    last = dk[40:44]
    inner = [tuple(dk[4 * r : 4 * r + 4]) for r in range(1, 10)]
    out: list[int] = []
    append = out.append
    for b0, b1, b2, b3 in struct.iter_unpack(">4I", data):
        s0 = b0 ^ k0
        s1 = b1 ^ k1
        s2 = b2 ^ k2
        s3 = b3 ^ k3
        for r0, r1, r2, r3 in inner:
            t0 = td0[s0 >> 24] ^ td1[(s3 >> 16) & 255] ^ td2[(s2 >> 8) & 255] ^ td3[s1 & 255] ^ r0
            t1 = td0[s1 >> 24] ^ td1[(s0 >> 16) & 255] ^ td2[(s3 >> 8) & 255] ^ td3[s2 & 255] ^ r1
            t2 = td0[s2 >> 24] ^ td1[(s1 >> 16) & 255] ^ td2[(s0 >> 8) & 255] ^ td3[s3 & 255] ^ r2
            t3 = td0[s3 >> 24] ^ td1[(s2 >> 16) & 255] ^ td2[(s1 >> 8) & 255] ^ td3[s0 & 255] ^ r3
            s0, s1, s2, s3 = t0, t1, t2, t3
        append(
            (
                (isb[s0 >> 24] << 24)
                | (isb[(s3 >> 16) & 255] << 16)
                | (isb[(s2 >> 8) & 255] << 8)
                | isb[s1 & 255]
            )
            ^ last[0]
        )
        append(
            (
                (isb[s1 >> 24] << 24)
                | (isb[(s0 >> 16) & 255] << 16)
                | (isb[(s3 >> 8) & 255] << 8)
                | isb[s2 & 255]
            )
            ^ last[1]
        )
        append(
            (
                (isb[s2 >> 24] << 24)
                | (isb[(s1 >> 16) & 255] << 16)
                | (isb[(s0 >> 8) & 255] << 8)
                | isb[s3 & 255]
            )
            ^ last[2]
        )
        append(
            (
                (isb[s3 >> 24] << 24)
                | (isb[(s2 >> 16) & 255] << 16)
                | (isb[(s1 >> 8) & 255] << 8)
                | isb[s0 & 255]
            )
            ^ last[3]
        )
    return struct.pack(f">{len(out)}I", *out)
