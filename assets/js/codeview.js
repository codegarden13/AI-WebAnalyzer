// codeview.js
let cssLines = [];

export async function loadCodeLines() {
  const r = await fetch("./combined.lines.json");
  cssLines = (await r.json()).lines;
}

export function showMatches(regex) {
  const tbody = document.querySelector("#resultTable tbody");
  tbody.innerHTML = "";

  if (!regex || !cssLines.length) return;

  const re = new RegExp(regex, "i");

  const matches = cssLines.filter(line => re.test(line.text));

  matches.forEach(line => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td style="color:#aaa">${line.num}</td>
      <td>${highlight(line.text, re)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function highlight(text, re) {
  return text.replace(re, m => `<span style="color:#0bf">${m}</span>`);
}