#!/usr/bin/env python3
"""Generador estatico del sitio de Maestria Inmobiliaria.

Uso:
    python build.py            # genera dist/
    python build.py --serve    # genera y levanta servidor local en :8000
"""
from __future__ import annotations

import argparse
import datetime as dt
import http.server
import os
import shutil
import socketserver
from pathlib import Path

import markdown as md
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
ASSETS = ROOT / "assets"
CONTENT = ROOT / "content"
DIST = ROOT / "dist"

TIPO_LABEL = {
    "casa": "Casa",
    "departamento": "Departamento",
    "oficina": "Oficina",
    "local": "Local comercial",
    "bodega": "Bodega",
    "terreno": "Terreno",
    "parcela": "Parcela",
    "sitio": "Sitio",
}
OPERACION_LABEL = {"venta": "Venta", "arriendo": "Arriendo"}


# --------------------------------------------------------------------------- #
# Carga de datos
# --------------------------------------------------------------------------- #
def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_site() -> dict:
    return load_yaml(DATA / "site.yaml")


def load_agentes() -> dict:
    data = load_yaml(DATA / "agentes.yaml")
    return {a["slug"]: a for a in data.get("agentes", [])}


def fmt_precio(prop: dict) -> str:
    moneda = prop.get("moneda", "UF")
    valor = prop.get("precio")
    if valor is None:
        return "Consultar"
    if moneda == "UF":
        return f"UF {valor:,.0f}".replace(",", ".")
    if moneda == "CLP":
        return f"${valor:,.0f}".replace(",", ".")
    return f"{moneda} {valor:,.0f}".replace(",", ".")


def load_propiedades(agentes: dict) -> list[dict]:
    props = []
    carpeta = DATA / "propiedades"
    for f in sorted(carpeta.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        p = load_yaml(f)
        if not p:
            continue
        p.setdefault("slug", f.stem)
        p["tipo_label"] = TIPO_LABEL.get(p.get("tipo", ""), p.get("tipo", ""))
        p["operacion_label"] = OPERACION_LABEL.get(p.get("operacion", ""), "")
        p["precio_fmt"] = fmt_precio(p)
        p["url"] = f"/propiedades/{p['slug']}/"
        fotos = p.get("fotos", [])
        p["fotos"] = [f"/img/propiedades/{p['slug']}/{x}" for x in fotos]
        p["portada"] = p["fotos"][0] if p["fotos"] else "/img/placeholder.jpg"
        ag = p.get("agente")
        p["agente_obj"] = agentes.get(ag) if ag else None
        if p.get("descripcion"):
            p["descripcion_html"] = md.markdown(p["descripcion"].strip())
        props.append(p)
    # disponibles primero, luego por destacada, luego por codigo
    orden_estado = {"disponible": 0, "reservada": 1, "vendida": 2}
    props.sort(key=lambda x: (
        orden_estado.get(x.get("estado", "disponible"), 0),
        0 if x.get("destacada") else 1,
        str(x.get("codigo", "")),
    ))
    return props


def load_blog() -> list[dict]:
    posts = []
    carpeta = CONTENT / "blog"
    if not carpeta.exists():
        return posts
    for f in sorted(carpeta.glob("*.md"), reverse=True):
        raw = f.read_text(encoding="utf-8")
        front, _, body = raw.partition("\n---\n") if raw.startswith("---") else ("", "", raw)
        meta = yaml.safe_load(front.lstrip("-\n")) if front else {}
        meta = meta or {}
        meta["slug"] = f.stem
        meta["url"] = f"/blog/{f.stem}/"
        meta["html"] = md.markdown(body.strip(), extensions=["extra"])
        posts.append(meta)
    return posts


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # assets -> dist raiz (css/, js/, img/)
    for sub in ("css", "js", "img"):
        src = ASSETS / sub
        if src.exists():
            shutil.copytree(src, DIST / sub)

    # fotos de propiedades -> dist/img/propiedades/<slug>/
    fotos_src = DATA / "propiedades" / "_fotos"
    if fotos_src.exists():
        shutil.copytree(fotos_src, DIST / "img" / "propiedades", dirs_exist_ok=True)

    site = load_site()
    agentes = load_agentes()
    props = load_propiedades(agentes)
    posts = load_blog()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(
        site=site,
        agentes=list(agentes.values()),
        anio=dt.date.today().year,
    )

    comunas = sorted({p["comuna"] for p in props if p.get("comuna")})
    tipos = sorted({p["tipo"] for p in props if p.get("tipo")})
    # las destacadas del inicio incluyen vendidas (se muestran con franja "Vendido")
    destacadas = [p for p in props if p.get("destacada")
                  and p.get("estado") in ("disponible", "vendida", "reservada")][:6]
    disponibles = [p for p in props if p.get("estado") == "disponible"]

    def render(tpl: str, out: str, **ctx) -> None:
        html = env.get_template(tpl).render(**ctx)
        dest = DIST / out
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")

    render("index.html", "index.html",
           destacadas=destacadas, total=len(disponibles), page="inicio")
    render("propiedades.html", "propiedades/index.html",
           propiedades=disponibles, comunas=comunas, tipos=tipos,
           tipo_label=TIPO_LABEL, page="propiedades")
    for p in props:
        render("propiedad.html", f"propiedades/{p['slug']}/index.html",
               p=p, relacionadas=[x for x in disponibles if x["slug"] != p["slug"]][:3],
               page="propiedades")
    render("vender.html", "vende-con-nosotros/index.html", page="vender")
    render("nosotros.html", "nosotros/index.html", page="nosotros")
    render("contacto.html", "contacto/index.html", page="contacto")
    render("blog.html", "blog/index.html", posts=posts, page="blog")
    for post in posts:
        render("blog-post.html", f"blog/{post['slug']}/index.html", post=post, page="blog")

    # archivos sueltos
    _write_extra(site, props)
    print(f"OK  {len(props)} propiedades  |  {len(posts)} posts  ->  {DIST}")


def _write_extra(site: dict, props: list[dict]) -> None:
    base = site.get("url", "https://www.maestriainmobiliaria.cl").rstrip("/")
    urls = ["/", "/propiedades/", "/vende-con-nosotros/", "/nosotros/", "/contacto/", "/blog/"]
    urls += [p["url"] for p in props]
    today = dt.date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{base}{u}</loc><lastmod>{today}</lastmod></url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    # CNAME solo cuando ya se decidio el dominio (site.yaml: deploy_cname) o via env.
    cname = os.environ.get("SITE_CNAME") or site.get("deploy_cname") or ""
    if cname.strip():
        (DIST / "CNAME").write_text(cname.strip() + "\n", encoding="utf-8")
    # 404
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True,
                          trim_blocks=True, lstrip_blocks=True)
        env.globals.update(site=site, anio=dt.date.today().year)
        (DIST / "404.html").write_text(env.get_template("404.html").render(page=""), encoding="utf-8")
    except Exception:
        pass


def serve(port: int = 8000) -> None:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(DIST), **kw)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"http://127.0.0.1:{port}  (Ctrl+C para detener)")
        httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    build()
    if args.serve:
        serve(args.port)
