/* Maestría Inmobiliaria — interacciones mínimas */
(function () {
  "use strict";

  // --- rotación de la imagen del header (cada 5 s, con fundido) ---
  var heroBgs = document.getElementById("heroBgs");
  if (heroBgs) {
    var heroList = [];
    try { heroList = JSON.parse(heroBgs.dataset.hero || "[]"); } catch (e) { heroList = []; }
    var heroLayers = heroBgs.querySelectorAll(".hero-bg");
    var sinMovimiento = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (heroList.length > 1 && heroLayers.length === 2 && !sinMovimiento) {
      var heroIdx = parseInt(heroBgs.dataset.heroIdx || "0", 10);
      var capaActiva = heroLayers[0].classList.contains("is-on") ? 0 : 1;
      setInterval(function () {
        heroIdx = (heroIdx + 1) % heroList.length;
        var sig = 1 - capaActiva;
        var el = heroLayers[sig];
        el.style.backgroundImage = "url('" + heroList[heroIdx] + "')";
        el.style.animation = "none";
        void el.offsetWidth;            // reinicia el zoom lento
        el.style.animation = "";
        el.classList.add("is-on");
        heroLayers[capaActiva].classList.remove("is-on");
        capaActiva = sig;
      }, 5000);
    }
  }

  // --- menú móvil ---
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // --- galería ficha de propiedad ---
  var fotoMain = document.getElementById("fotoMain");
  var thumbs = Array.prototype.slice.call(document.querySelectorAll(".prop-thumb"));
  if (fotoMain && thumbs.length) {
    var srcs = thumbs.map(function (t) { return t.dataset.src; });
    var contador = document.getElementById("fotoContador");
    var idx = 0;

    function mostrar(i) {
      idx = (i % srcs.length + srcs.length) % srcs.length;
      fotoMain.src = srcs[idx];
      thumbs.forEach(function (x, j) { x.classList.toggle("is-active", j === idx); });
      if (contador) contador.textContent = (idx + 1) + " / " + srcs.length;
    }

    thumbs.forEach(function (t, i) {
      t.addEventListener("click", function () { mostrar(i); });
    });

    var prev = document.getElementById("fotoPrev");
    var next = document.getElementById("fotoNext");
    if (prev) prev.addEventListener("click", function () { mostrar(idx - 1); });
    if (next) next.addEventListener("click", function () { mostrar(idx + 1); });

    document.addEventListener("keydown", function (e) {
      if (e.target && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
      if (e.key === "ArrowLeft") mostrar(idx - 1);
      else if (e.key === "ArrowRight") mostrar(idx + 1);
    });
  }

  // --- filtros del listado ---
  var form = document.getElementById("filtros");
  var lista = document.getElementById("listaProps");
  if (form && lista) {
    var items = Array.prototype.slice.call(lista.querySelectorAll(".prop-item"));
    var contador = document.getElementById("resultados");
    var vacio = document.getElementById("sinResultados");

    function aplicar() {
      var f = new FormData(form);
      var op = f.get("operacion") || "";
      var tipo = f.get("tipo") || "";
      var comuna = f.get("comuna") || "";
      var dorm = parseInt(f.get("dormitorios") || "0", 10);
      var visibles = 0;

      items.forEach(function (it) {
        var ok =
          (!op || it.dataset.operacion === op) &&
          (!tipo || it.dataset.tipo === tipo) &&
          (!comuna || it.dataset.comuna === comuna) &&
          (!dorm || parseInt(it.dataset.dormitorios, 10) >= dorm);
        it.hidden = !ok;
        if (ok) visibles++;
      });

      if (contador) {
        contador.textContent = visibles + (visibles === 1 ? " propiedad" : " propiedades");
      }
      if (vacio) vacio.hidden = visibles !== 0;
    }

    form.addEventListener("change", aplicar);
    form.addEventListener("reset", function () { setTimeout(aplicar, 0); });
  }

  // --- prefijar propiedad en el formulario de contacto ---
  var params = new URLSearchParams(location.search);
  var campoProp = document.getElementById("campoPropiedad");
  var mensaje = document.querySelector('#formContacto [name="mensaje"]');
  if (params.get("propiedad")) {
    if (campoProp) campoProp.value = params.get("propiedad");
    if (mensaje && !mensaje.value) {
      mensaje.value = "Hola, me interesa la propiedad código " + params.get("propiedad") + ". ";
    }
  }

  // --- envío del formulario vía fetch si hay endpoint ---
  var fc = document.getElementById("formContacto");
  if (fc && fc.getAttribute("action")) {
    fc.addEventListener("submit", function (e) {
      e.preventDefault();
      var nota = document.getElementById("formNota");
      var btn = fc.querySelector('button[type="submit"]');
      btn.disabled = true;
      fetch(fc.action, { method: "POST", body: new FormData(fc), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (nota) {
            nota.hidden = false;
            nota.textContent = r.ok
              ? "¡Gracias! Recibimos tu mensaje y te contactaremos pronto."
              : "Hubo un problema al enviar. Escríbenos directo por correo, por favor.";
          }
          if (r.ok) fc.reset();
        })
        .catch(function () {
          if (nota) { nota.hidden = false; nota.textContent = "No se pudo enviar. Intenta por correo."; }
        })
        .finally(function () { btn.disabled = false; });
    });
  }

  // --- sombra del header al hacer scroll ---
  var header = document.getElementById("siteHeader");
  if (header) {
    var onScroll = function () {
      header.style.boxShadow = window.scrollY > 10 ? "0 10px 30px -20px rgba(0,0,0,.5)" : "none";
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // --- zona de miembros: desbloqueo de módulos por clave ---
  var zmGrid = document.getElementById("zmGrid");
  if (zmGrid && window.crypto && window.crypto.subtle) {
    (function () {
      var enc = new TextEncoder();
      var dec = new TextDecoder();

      function b64d(s) {
        var bin = atob(s), out = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
        return out;
      }
      function cat() {
        var total = 0, i;
        for (i = 0; i < arguments.length; i++) total += arguments[i].length;
        var out = new Uint8Array(total), o = 0;
        for (i = 0; i < arguments.length; i++) { out.set(arguments[i], o); o += arguments[i].length; }
        return out;
      }
      function eq(a, b) {
        if (a.length !== b.length) return false;
        var d = 0;
        for (var i = 0; i < a.length; i++) d |= a[i] ^ b[i];
        return d === 0;
      }
      function sha256(bytes) {
        return crypto.subtle.digest("SHA-256", bytes).then(function (b) { return new Uint8Array(b); });
      }
      function pbkdf2(pw, salt, iters) {
        return crypto.subtle.importKey("raw", enc.encode(pw), "PBKDF2", false, ["deriveBits"])
          .then(function (km) {
            return crypto.subtle.deriveBits(
              { name: "PBKDF2", salt: salt, iterations: iters, hash: "SHA-256" }, km, 256);
          }).then(function (b) { return new Uint8Array(b); });
      }
      function hmac(key, msg) {
        return crypto.subtle.importKey("raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"])
          .then(function (k) { return crypto.subtle.sign("HMAC", k, msg); })
          .then(function (b) { return new Uint8Array(b); });
      }
      function keystream(key, len) {
        var out = new Uint8Array(0), ctr = 0;
        function next() {
          if (out.length >= len) return Promise.resolve(out.slice(0, len));
          var c = new Uint8Array(4);
          new DataView(c.buffer).setUint32(0, ctr++, false);
          return sha256(cat(key, c)).then(function (blk) { out = cat(out, blk); return next(); });
        }
        return next();
      }
      // blob = base64( salt[16] | iters[4 BE] | tag[16] | ciphertext )   pt = "M1|" + url
      function descifrar(pw, blobB64) {
        var blob = b64d(blobB64);
        var salt = blob.slice(0, 16);
        var iters = new DataView(blob.buffer, blob.byteOffset).getUint32(16, false);
        var tag = blob.slice(20, 36);
        var ct = blob.slice(36);
        return pbkdf2(pw, salt, iters).then(function (key) {
          return hmac(key, ct).then(function (t) {
            if (!eq(tag, t.slice(0, 16))) throw new Error("clave");
            return keystream(key, ct.length).then(function (ks) {
              var pt = new Uint8Array(ct.length);
              for (var i = 0; i < ct.length; i++) pt[i] = ct[i] ^ ks[i];
              var txt = dec.decode(pt);
              if (txt.indexOf("M1|") !== 0) throw new Error("clave");
              return txt.slice(3);
            });
          });
        });
      }

      var cards = Array.prototype.slice.call(zmGrid.querySelectorAll(".zm-card"));
      var prog = document.getElementById("zmProgreso");

      function actualizarProgreso() {
        var conClave = cards.filter(function (c) { return c.dataset.blob; });
        var abiertos = conClave.filter(function (c) { return c.dataset.estado === "abierto"; });
        if (prog && conClave.length) {
          prog.hidden = false;
          prog.textContent = "Tu avance: " + abiertos.length + " de " + conClave.length + " módulos";
        }
      }
      function setEstado(card, estado, url) {
        card.dataset.estado = estado;
        card.classList.toggle("is-abierto", estado === "abierto");
        card.classList.toggle("is-pronto", estado === "pronto");
        var link = card.querySelector(".zm-link");
        if (url && link) link.href = url;
        actualizarProgreso();
      }

      cards.forEach(function (card) {
        var id = card.dataset.id;
        var blob = card.dataset.blob;
        var form = card.querySelector(".zm-unlock");
        var err = card.querySelector(".zm-error");
        var lockBtn = card.querySelector(".zm-lock-again");
        var lsKey = "zm_" + id;

        if (!blob) { setEstado(card, "pronto"); return; }

        var guardado = null;
        try { guardado = localStorage.getItem(lsKey); } catch (e) {}
        if (guardado && /^https?:\/\//.test(guardado)) {
          setEstado(card, "abierto", guardado);
        } else {
          setEstado(card, "bloqueado");
        }

        if (form) {
          form.addEventListener("submit", function (e) {
            e.preventDefault();
            if (err) err.hidden = true;
            var btn = form.querySelector("button");
            var pw = form.clave.value.trim();
            if (!pw) return;
            btn.disabled = true;
            descifrar(pw, blob).then(function (url) {
              try { localStorage.setItem(lsKey, url); } catch (e2) {}
              setEstado(card, "abierto", url);
            }).catch(function () {
              if (err) err.hidden = false;
            }).then(function () { btn.disabled = false; });
          });
        }
        if (lockBtn) {
          lockBtn.addEventListener("click", function () {
            try { localStorage.removeItem(lsKey); } catch (e) {}
            if (form) form.reset();
            setEstado(card, "bloqueado");
          });
        }
      });

      actualizarProgreso();
    })();
  }

  // --- efectos visuales "IA": formas 3D flotantes, destellos, tilt, reveal ---
  var sinMovimientoUI = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var esPantallaChica = window.matchMedia && window.matchMedia("(max-width: 640px)").matches;

  // formas 3D flotantes + destellos, inyectadas en hero / page-hero
  if (!sinMovimientoUI && !esPantallaChica) {
    var contenedoresGlow = Array.prototype.slice.call(document.querySelectorAll(".hero, .page-hero"));
    var formas = [
      { cls: "float-shape-ring", size: 132, top: "10%", left: "5%", dur: "21s" },
      { cls: "float-shape-orb", size: 44, top: "70%", left: "90%", dur: "15s" },
      { cls: "float-shape-diamond", size: 30, top: "18%", left: "93%", dur: "18s" }
    ];
    var chispas = [
      { top: "22%", left: "14%" }, { top: "34%", left: "80%" }, { top: "58%", left: "8%" },
      { top: "66%", left: "70%" }, { top: "14%", left: "60%" }, { top: "80%", left: "40%" },
      { top: "45%", left: "94%" }, { top: "12%", left: "30%" }
    ];
    contenedoresGlow.forEach(function (sec) {
      formas.forEach(function (f, i) {
        var span = document.createElement("span");
        span.className = "float-shape " + f.cls;
        span.style.width = f.size + "px";
        span.style.height = f.size + "px";
        span.style.top = f.top;
        span.style.left = f.left;
        span.style.setProperty("--dur", f.dur);
        span.style.animationDelay = (i * -3.5) + "s";
        span.setAttribute("aria-hidden", "true");
        sec.appendChild(span);
      });
      chispas.forEach(function (c, i) {
        var s = document.createElement("span");
        s.className = "spark";
        s.style.top = c.top;
        s.style.left = c.left;
        s.style.animationDelay = (i * -0.6) + "s";
        s.setAttribute("aria-hidden", "true");
        sec.appendChild(s);
      });
    });
  }

  // tilt 3D suave al mover el mouse (solo con puntero fino, sin animación reducida)
  var tienePunteroFino = window.matchMedia && window.matchMedia("(pointer: fine)").matches;
  if (tienePunteroFino && !sinMovimientoUI) {
    var tiltEls = Array.prototype.slice.call(
      document.querySelectorAll(".card-prop, .pilar, .lp-photo, .equipo .agente img, .prop-foto-main img")
    );
    tiltEls.forEach(function (el) {
      el.classList.add("tilt-el");
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        el.style.setProperty("--tiltX", (py * -7).toFixed(2) + "deg");
        el.style.setProperty("--tiltY", (px * 7).toFixed(2) + "deg");
      });
      el.addEventListener("mouseleave", function () {
        el.style.setProperty("--tiltX", "0deg");
        el.style.setProperty("--tiltY", "0deg");
      });
    });
  }

  // reveal suave de secciones al entrar en pantalla
  if (!sinMovimientoUI && "IntersectionObserver" in window) {
    var revelables = Array.prototype.slice.call(
      document.querySelectorAll(".section .section-head, .card-prop, .pilar, .agente")
    );
    revelables.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
    revelables.forEach(function (el) { io.observe(el); });
  }
})();
