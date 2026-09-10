# Sitio web — Maestría Inmobiliaria

Sitio estático generado con Python + Jinja2. Sin Node, sin base de datos.
El resultado (`dist/`) es HTML plano que se publica en cualquier hosting estático
(Vercel, Netlify, Cloudflare Pages, GitHub Pages).

## Requisitos

```
python -m pip install -r requirements.txt
```

## Comandos

```
python build.py            # genera dist/
python build.py --serve    # genera y levanta http://127.0.0.1:8000
```

## Estructura

| Carpeta | Qué contiene |
|---|---|
| `data/site.yaml` | Configuración global: navegación, contacto, redes, zonas |
| `data/agentes.yaml` | Equipo de agentes |
| `data/propiedades/*.yaml` | Una ficha por propiedad (ver `_ejemplo.yaml`) |
| `data/propiedades/_fotos/<slug>/` | Fotos de cada propiedad |
| `templates/` | Plantillas Jinja2 |
| `assets/` | CSS, JS e imágenes (logo, favicons) |
| `content/blog/*.md` | Artículos del blog (Markdown con frontmatter) |
| `dist/` | Salida generada (no se versiona) |

## Agregar una propiedad

1. Copiar `data/propiedades/_ejemplo.yaml` a `data/propiedades/<slug>.yaml`.
2. Poner las fotos en `data/propiedades/_fotos/<slug>/`.
3. `python build.py`.

## Pendientes de configuración

- `data/site.yaml`: teléfono, WhatsApp, redes sociales, `formspree_endpoint`.
- Reemplazar imágenes placeholder (`assets/img/hero.jpg`, fotos de equipo, fotos de propiedades).
- Conectar dominio `www.maestriainmobiliaria.cl` (DNS en GoDaddy) al hosting elegido.
