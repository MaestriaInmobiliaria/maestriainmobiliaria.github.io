#!/usr/bin/env python3
"""Extrae un JPEG base64 de un archivo tool-result de mcp__Claude_Browser__javascript_tool.

El archivo es un JSON [{type,text}, ...] donde text[0] contiene:
    "<MARKER><base64>"\n\n(captured at origin ...)

Uso:  python tools/decode_b64.py <archivo_txt> <MARKER> <salida.jpg>
"""
import base64
import json
import sys
from pathlib import Path


def main() -> int:
    src, marker, out = sys.argv[1], sys.argv[2], sys.argv[3]
    data = json.load(open(src, encoding="utf-8"))
    text = data[0]["text"] if isinstance(data, list) else data["text"]
    if marker not in text:
        print(f"marcador {marker!r} no encontrado")
        return 1
    b64 = text.split(marker, 1)[1]
    # cortar en la comilla de cierre del string JS
    for stop in ('"\n', '"\r', '"'):
        if stop in b64:
            b64 = b64.split(stop, 1)[0]
            break
    b64 = b64.strip()
    b64 += "=" * (-len(b64) % 4)
    raw = base64.b64decode(b64)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_bytes(raw)
    print(f"OK {out}  {len(raw)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
