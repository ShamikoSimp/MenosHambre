const params = new URLSearchParams(window.location.search);
  const tipo = params.get("tipo");

  const formUsuario = document.getElementById("formUsuario");
  const formOrganizacion = document.getElementById("formOrganizacion");

  if (tipo === "usuario") {
    formUsuario.classList.remove("hidden");
  } else if (tipo === "organizacion") {
    formOrganizacion.classList.remove("hidden");
  }