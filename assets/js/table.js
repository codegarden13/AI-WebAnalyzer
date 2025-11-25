export function updateTable(pattern, lines) {
  const tbody = document.querySelector("#resultTable tbody");
  tbody.innerHTML = "";

  if (!pattern || pattern.trim() === "") return;

  let regex;
  try {
    regex = new RegExp(pattern, "i");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="2">❌ Ungültiger Regex</td></tr>`;
    return;
  }

  lines.forEach((line, i) => {
    if (regex.test(line)) {
      const tr = document.createElement("tr");

      const tdLine = document.createElement("td");
      tdLine.textContent = i + 1;

      const tdText = document.createElement("td");
      tdText.textContent = line;

      tr.appendChild(tdLine);
      tr.appendChild(tdText);
      tbody.appendChild(tr);
    }
  });
}