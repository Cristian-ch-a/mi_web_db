const lista = document.getElementById("lista");
const form = document.getElementById("form");
const msg = document.getElementById("msg");

async function cargar() {
  const res = await fetch("/api/usuarios");
  const data = await res.json();
  lista.innerHTML = "";

  data.forEach(u => {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `<b>#${u.id}</b> ${u.nombre}<br><small>${u.email}</small>`;
    lista.appendChild(div);
  });
}

function setMsg(texto, ok=true) {
  msg.textContent = texto;
  msg.className = "msg " + (ok ? "ok" : "err");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const email = document.getElementById("email").value.trim();

  const res = await fetch("/api/usuarios", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, email })
  });

  const r = await res.json();
  if (!res.ok) {
    setMsg(r.error || "Error", false);
    return;
  }

  form.reset();
  setMsg("Guardado ✅", true);
  cargar();
});

cargar();
