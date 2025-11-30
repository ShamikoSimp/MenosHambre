const params = new URLSearchParams(window.location.search);
    const usuario = params.get("usuario"); // 'normal' o 'organizacion'
    const tipo = params.get("tipo"); // 'olla' o 'comedor'

    // Mostrar campos según el tipo de usuario
    if (usuario === "normal") {
      document.getElementById("usuario-normal").classList.remove("hidden");
    } else if (usuario === "organizacion") {
      document.getElementById("organizacion").classList.remove("hidden");
    }

    // Mostrar campos según el tipo de publicación
    if (tipo === "olla") {
      document.getElementById("olla-comun").classList.remove("hidden");
    } else if (tipo === "comedor") {
      document.getElementById("comedor-solidario").classList.remove("hidden");
    }