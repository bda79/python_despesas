document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("searchInput");

  if (!input) return;

  const table =
    document.querySelector(".despesas-table") ||
    document.querySelector(".resumo-table");

  if (!table) return;

  const rows = table.querySelectorAll("tbody tr");
  const resultCount = document.getElementById("resultCount");
  const suggestionsBox = document.getElementById("suggestions");

  const categorias = [
    ...new Set(
      Array.from(rows)
        .map((r) => r.children[2]?.innerText.trim())
        .filter(Boolean),
    ),
  ];

  function filterTable(value) {
    value = value.toLowerCase();
    if (!value) {
      rows.forEach((row) => {
        row.style.display = "";
      });

      if (resultCount) {
        resultCount.innerText = "";
      }

      return;
    }

    let visible = 0;

    rows.forEach((row) => {
      const searchableText = Array.from(row.cells)
        .slice(0, 6) // ignora a coluna Ações
        .map((cell) => cell.innerText.toLowerCase())
        .join(" ");

      const match = searchableText.includes(value);

      row.style.display = match ? "" : "none";

      if (match) visible++;
    });

    if (resultCount) {
      resultCount.innerText = `${visible} resultado(s)`;
    }
  }

  function showSuggestions(value) {
    if (!suggestionsBox) return;

    if (!value) {
      suggestionsBox.innerHTML = "";
      return;
    }

    const filtered = categorias.filter((c) =>
      c.toLowerCase().includes(value.toLowerCase()),
    );

    suggestionsBox.innerHTML = filtered
      .map((c) => `<div class="suggestion-item">${c}</div>`)
      .join("");

    document.querySelectorAll(".suggestion-item").forEach((item) => {
      item.addEventListener("click", () => {
        input.value = item.innerText;

        filterTable(item.innerText);

        suggestionsBox.innerHTML = "";
      });
    });
  }

  input.addEventListener("input", function () {
    const value = this.value;

    filterTable(value);

    showSuggestions(value);
  });
});
