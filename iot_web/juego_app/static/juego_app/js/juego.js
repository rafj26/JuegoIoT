// Atajos de teclado y contador de alertas marcadas en la pantalla de ronda
(function () {
  var form = document.getElementById("form-decision");
  if (!form) { return; }
  var casillas = form.querySelectorAll("input[name=alertas]");
  var contador = document.getElementById("contador");

  function actualizar() {
    var marcadas = 0;
    casillas.forEach(function (c) {
      var estado = c.nextElementSibling.querySelector(".estado-alerta");
      estado.textContent = c.checked ? "ATENDER" : "IGNORAR";
      if (c.checked) { marcadas += 1; }
    });
    contador.textContent = marcadas + (marcadas === 1 ? " alerta marcada" : " alertas marcadas");
  }

  casillas.forEach(function (c) { c.addEventListener("change", actualizar); });

  document.addEventListener("keydown", function (e) {
    if (e.target.tagName === "INPUT" && e.target.type === "text") { return; }
    var numero = parseInt(e.key, 10);
    if (numero >= 1 && numero <= casillas.length) {
      casillas[numero - 1].checked = !casillas[numero - 1].checked;
      actualizar();
    } else if (e.key === "Enter") {
      e.preventDefault();
      form.requestSubmit();
    }
  });
  actualizar();
})();
