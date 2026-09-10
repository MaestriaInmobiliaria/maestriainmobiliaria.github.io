#!/usr/bin/env python3
"""Normaliza las imagenes del encabezado.

Toma los archivos crudos que dejaste en assets/_hero_src/ (los que
descargaste de ChatGPT, cualquier tamano/relacion) y genera versiones
2400x1350 (16:9), nitidas y optimizadas, en assets/img/hero/.

Uso:
    python tools/prep_hero.py                 # procesa todo assets/_hero_src/
    python tools/prep_hero.py a1.jpg a2.jpg   # procesa archivos puntuales

Nombres de salida = mismo nombre base con .jpg.  Ej: crudas/a1.png -> hero/a1.jpg
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
HERO = ROOT / "assets" / "img" / "hero"
CRUDAS = ROOT / "assets" / "_hero_src"   # imagenes crudas, fuera de la ruta que se publica
TARGET = (2400, 1350)          # 16:9
QUALITY = 82


def procesar(src: Path) -> Path:
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    # recorte central a 16:9 y reescala a 2400x1350
    im = ImageOps.fit(im, TARGET, method=Image.LANCZOS, centering=(0.5, 0.42))
    # leve nitidez para compensar el reescalado del generador
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=90, threshold=2))
    out = HERO / (src.stem + ".jpg")
    im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    kb = out.stat().st_size // 1024
    print(f"  OK {src.name} -> {out.name}  ({TARGET[0]}x{TARGET[1]}, {kb} KB)")
    return out


def main(argv: list[str]) -> int:
    if argv:
        fuentes = [CRUDAS / a if not Path(a).is_absolute() else Path(a) for a in argv]
    else:
        if not CRUDAS.exists():
            print(f"No existe {CRUDAS}. Crea la carpeta y deja ahi las imagenes de ChatGPT.")
            return 1
        fuentes = sorted(
            p for p in CRUDAS.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )
    if not fuentes:
        print("No hay imagenes que procesar.")
        return 1
    for f in fuentes:
        if not f.exists():
            print(f"  ! no encontrado: {f}")
            continue
        procesar(f)
    print(f"\nListo. Revisa {HERO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
