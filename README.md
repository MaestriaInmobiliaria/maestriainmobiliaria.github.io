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

## Publicación (GitHub Pages)

El repo trae un workflow (`.github/workflows/deploy.yml`) que compila y publica en
cada `git push` a `main`.

Puesta en marcha (una vez):

1. Crear un repo en GitHub. Recomendado: nombrarlo `<usuario>.github.io` para que
   el sitio quede en la raíz (`https://<usuario>.github.io/`) y los enlaces
   absolutos funcionen sin dominio propio.
2. `git remote add origin https://github.com/<usuario>/<repo>.git`
3. `git push -u origin main`
4. En el repo: **Settings → Pages → Source: GitHub Actions**.
5. Esperar ~1 min. El enlace aparece en la pestaña **Actions** (job *deploy*) y en Settings → Pages.

Conectar el dominio propio (cuando se decida):

1. `data/site.yaml` → `deploy_cname: "www.maestriainmobiliaria.cl"`, commit y push.
2. En GoDaddy, crear el registro DNS que indica GitHub (CNAME `www` → `<usuario>.github.io`).
3. Settings → Pages → Custom domain.

## Zona de miembros (capacitación de agentes)

Página `/zona-miembros/` con los módulos del programa. Cada módulo se desbloquea
con una clave; la clave y el enlace real del contenido van **cifrados** (no en
texto plano). Es un candado blando: frena al visitante casual, no es seguridad
de nivel bancario.

Para activar un módulo:

1. Abre `tools/zona-encrypt.html` en el navegador (doble clic).
2. Escribe la clave que darás a los agentes y el enlace real del módulo.
3. Copia el `blob` que genera.
4. Pégalo en `data/zona_miembros.yaml`, en el campo `blob` de ese módulo.
5. `git commit` + `git push`.

`blob` vacío = el módulo se muestra como "Próximamente".
(Alternativa por consola: `python tools/zona_encrypt.py "clave" "https://enlace"`.)

## Pendientes de configuración

- `data/site.yaml`: redes sociales, `formspree_endpoint`.
- Fotos reales de equipo (`assets/img/equipo/`).
- Ajustes finos de contenido de propiedades.
