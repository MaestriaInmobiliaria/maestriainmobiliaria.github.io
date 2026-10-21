"""Ubicacion aproximada de una propiedad para el mapa publico del sitio.

El repo es publico, asi que NUNCA se guardan coordenadas exactas ni nada que permita
recalcularlas. Este script desplaza el punto real entre 250 y 350 m en una direccion
ALEATORIA (secrets, no reproducible) y guarda solo el punto desplazado en el YAML de
la propiedad (campo `ubicacion_aprox`). No usar semillas derivadas del slug ni de
ningun dato publico: se podria invertir el desplazamiento.

Uso:
    python tools/mapa_aprox.py LAT LNG                     # solo imprime el punto desplazado
    python tools/mapa_aprox.py LAT LNG --aplicar SLUG      # y lo escribe en data/propiedades/SLUG.yaml
"""
from __future__ import annotations

import argparse
import math
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROPS = ROOT / "data" / "propiedades"
R_TIERRA = 6371008.8  # m

DIST_MIN, DIST_MAX = 250.0, 350.0


def desplazar(lat: float, lng: float) -> tuple[float, float]:
    rnd = secrets.SystemRandom()
    dist = rnd.uniform(DIST_MIN, DIST_MAX)
    ang = rnd.uniform(0.0, 2 * math.pi)
    dlat = (dist * math.cos(ang)) / R_TIERRA
    dlng = (dist * math.sin(ang)) / (R_TIERRA * math.cos(math.radians(lat)))
    return lat + math.degrees(dlat), lng + math.degrees(dlng)


def aplicar(slug: str, lat: float, lng: float) -> None:
    f = PROPS / f"{slug}.yaml"
    if not f.exists():
        raise SystemExit(f"No existe {f}")
    txt = f.read_text(encoding="utf-8")
    bloque = f"ubicacion_aprox:\n  lat: {lat:.5f}\n  lng: {lng:.5f}\n"
    if re.search(r"^ubicacion_aprox:", txt, flags=re.M):
        txt = re.sub(r"^ubicacion_aprox:\n(?:[ \t]+.*\n?)*", bloque, txt, flags=re.M)
    else:
        txt = txt.rstrip("\n") + "\n" + bloque
    f.write_text(txt, encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lat", type=float)
    ap.add_argument("lng", type=float)
    ap.add_argument("--aplicar", metavar="SLUG")
    a = ap.parse_args()
    if not (-90 <= a.lat <= 90 and -180 <= a.lng <= 180):
        raise SystemExit("Coordenadas fuera de rango")
    lat2, lng2 = desplazar(a.lat, a.lng)
    if a.aplicar:
        aplicar(a.aplicar, lat2, lng2)
        print(f"{a.aplicar}: ubicacion_aprox escrita")
    else:
        print(f"{lat2:.5f}, {lng2:.5f}")


if __name__ == "__main__":
    main()
