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
})();
