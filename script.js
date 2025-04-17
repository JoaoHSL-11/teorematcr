let count = 1;

function addCongruence() {
  count++;
  const div = document.createElement("div");
  div.className = "congruence";
  div.id = `congruence-${count}`;
  div.innerHTML = `Congruência ${count}: <input type="number" placeholder="a" /> x ≡ <input type="number" placeholder="b" /> (mod <input type="number" placeholder="m" />)`;
  document.getElementById("congruences").appendChild(div);
}

function removeCongruence() {
  if (count > 1) {
    document.getElementById(`congruence-${count}`).remove();
    count--;
  }
}

function calculate() {
  const congruences = [];
  document.querySelectorAll(".congruence").forEach((el) => {
    const inputs = el.querySelectorAll("input");
    const a = parseInt(inputs[0].value);
    const b = parseInt(inputs[1].value);
    const m = parseInt(inputs[2].value);
    if (!isNaN(a) && !isNaN(b) && !isNaN(m)) {
      congruences.push({ a, b, m });
    }
  });

  fetch("http://localhost:5000/resolver", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ congruences }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.x !== undefined) {
        document.getElementById("output").innerText = "Solução: x ≡ " + data.x + " (mod " + data.mod + ")";
      } else {
        document.getElementById("output").innerText = "Erro: " + data.error;
      }
    })
    .catch((error) => {
      document.getElementById("output").innerText = "Erro ao conectar com o servidor Python.";
    });
}
