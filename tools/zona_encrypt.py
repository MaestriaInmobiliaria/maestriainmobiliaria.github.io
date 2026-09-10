#!/usr/bin/env python3
"""Genera el `blob` cifrado de un módulo de la Zona de miembros.

Cifra el ENLACE del módulo con la CLAVE que le darás a los agentes.
El resultado (una línea base64) se pega en `data/zona_miembros.yaml` → módulo → `blob`.
La clave y el enlace no quedan en texto plano en el sitio.

Uso:
    python tools/zona_encrypt.py "CLAVE-DEL-MODULO" "https://enlace-real-del-modulo"

Esquema (igual que assets/js/main.js):
    key   = PBKDF2-HMAC-SHA256(clave, salt, 200000, 32 bytes)
    ks    = SHA256(key||ctr_be32) concatenado
    ct    = ("M1|"+url)  XOR  ks
    tag   = HMAC-SHA256(key, ct)[:16]
    blob  = base64( salt[16] | iters[4 BE] | tag[16] | ct )
"""
import base64
import hashlib
import hmac
import os
import struct
import sys

ITERS = 200_000


def keystream(key: bytes, n: int) -> bytes:
    out = b""
    ctr = 0
    while len(out) < n:
        out += hashlib.sha256(key + struct.pack(">I", ctr)).digest()
        ctr += 1
    return out[:n]


def encrypt(clave: str, url: str, iters: int = ITERS) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), salt, iters, 32)
    pt = ("M1|" + url).encode("utf-8")
    ks = keystream(key, len(pt))
    ct = bytes(a ^ b for a, b in zip(pt, ks))
    tag = hmac.new(key, ct, hashlib.sha256).digest()[:16]
    blob = salt + struct.pack(">I", iters) + tag + ct
    return base64.b64encode(blob).decode("ascii")


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    clave, url = sys.argv[1], sys.argv[2]
    if not url.startswith(("http://", "https://")):
        print("El enlace debe empezar con http:// o https://")
        return 1
    print("\nblob: \"" + encrypt(clave, url) + "\"\n")
    print("Pega esa línea en data/zona_miembros.yaml, en el módulo que corresponda.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
