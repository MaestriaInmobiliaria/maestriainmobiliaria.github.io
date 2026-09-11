"""Genera imagenes de marcador de posicion (verde/dorado) mientras llegan
las fotos reales. NO son parte del diseno final."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
VERDE = (2, 47, 42)
VERDE2 = (6, 66, 60)
DORADO = (198, 161, 91)
MARFIL = (245, 239, 227)


def _font(size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def card(w, h, texto, path, sub="FOTO PENDIENTE"):
    img = Image.new("RGB", (w, h), VERDE)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=(
            int(VERDE[0] + (VERDE2[0] - VERDE[0]) * t),
            int(VERDE[1] + (VERDE2[1] - VERDE[1]) * t),
            int(VERDE[2] + (VERDE2[2] - VERDE[2]) * t)))
    d.rectangle([12, 12, w - 12, h - 12], outline=DORADO, width=2)
    f1, f2 = _font(max(16, h // 12)), _font(max(11, h // 26))
    d.text((w / 2, h / 2 - h // 16), texto, font=f1, fill=MARFIL, anchor="mm")
    d.text((w / 2, h / 2 + h // 12), sub, font=f2, fill=DORADO, anchor="mm")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=88)


def main():
    a = ROOT / "assets" / "img"
    card(1600, 900, "MAESTRÍA INMOBILIARIA", a / "hero.jpg", "Imagen de portada pendiente")
    card(1200, 800, "Propiedad", a / "placeholder.jpg")
    for slug, n in (("casa-condominio-san-pedro", 3),
                    ("departamento-centro-concepcion", 2),
                    ("casa-hualpen-familiar", 1)):
        for i in range(1, n + 1):
            card(1200, 800, slug.replace("-", " ").title(),
                 ROOT / "data" / "propiedades" / "_fotos" / slug / f"{i:02d}.jpg")
    for slug, nom in (("jonathan-fox", "Jonathan Fox"),
                      ("camila-cardenas", "Camila Cárdenas"),
                      ("nicolas-herrera", "Nicolás Herrera"),
                      ("luciano-alarcon", "Luciano Alarcón")):
        card(600, 700, nom, a / "equipo" / f"{slug}.jpg", "Foto pendiente")
    print("placeholders OK")


if __name__ == "__main__":
    main()
