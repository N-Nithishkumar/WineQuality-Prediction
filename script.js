document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("wine-form");
  const predictBtn = document.getElementById("predict-btn");
  const btnText = document.getElementById("btn-text");
  const loader = document.getElementById("loader");

  const scoreNumber = document.getElementById("score-number");
  const subResultText = document.getElementById("sub-result-text");
  const labelBadge = document.getElementById("label-badge");
  const scoreStars = document.getElementById("score-stars");
  const scoreLevelText = document.getElementById("score-level-text");

  const historyBody = document.getElementById("history-modal-body");

  const fieldIds = [
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
  ];

  function getFormData() {
    const data = {};
    fieldIds.forEach((id) => {
      const el = document.getElementById(id);
      data[id] = el.value.trim();
    });
    return data;
  }

  function anyEmpty(data) {
    return Object.values(data).some((v) => v === "");
  }

  function setLoading(isLoading) {
    if (isLoading) {
      predictBtn.disabled = true;
      loader.classList.remove("d-none");
      btnText.textContent = "Predicting...";
    } else {
      predictBtn.disabled = false;
      loader.classList.add("d-none");
      btnText.textContent = "Predict Quality";
    }
  }

  function qualityToStars(quality) {
    // Map 0–10 to 0–5 stars
    const stars = Math.max(0, Math.min(5, Math.round((quality / 10) * 5)));
    let out = "";
    for (let i = 0; i < 5; i++) {
      out += i < stars ? "★" : "☆";
    }
    return out;
  }

  function labelDescription(label) {
    const l = label.toLowerCase();
    if (l === "low") {
      return "Quality is predicted to be on the lower side. The wine may taste sharper or less balanced.";
    } else if (l === "medium") {
      return "This wine is predicted to be of average quality, reasonably balanced and drinkable.";
    } else if (l === "high") {
      return "Great news! This wine is predicted to be high quality with well-balanced characteristics.";
    }
    return "Prediction label not available.";
  }

  function niceLevelText(label) {
    const l = label.toLowerCase();
    if (l === "low") return "Predicted as Low quality";
    if (l === "medium") return "Predicted as Medium quality";
    if (l === "high") return "Predicted as High quality";
    return "Prediction available";
  }

  function updateResultPanel(predQuality, label) {
    scoreNumber.textContent = predQuality.toFixed(1);
    scoreStars.textContent = qualityToStars(predQuality);
    scoreLevelText.textContent = niceLevelText(label);

    subResultText.textContent = labelDescription(label);
    labelBadge.textContent = label;

    labelBadge.classList.remove("label-low", "label-medium", "label-high");
    if (label.toLowerCase() === "low") {
      labelBadge.classList.add("label-low");
    } else if (label.toLowerCase() === "medium") {
      labelBadge.classList.add("label-medium");
    } else if (label.toLowerCase() === "high") {
      labelBadge.classList.add("label-high");
    }
  }

  function renderHistory(rows) {
    historyBody.innerHTML = "";
    if (!rows || rows.length === 0) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 8;
      td.className = "text-center text-muted";
      td.textContent = "No prediction history yet.";
      tr.appendChild(td);
      historyBody.appendChild(tr);
      return;
    }

    rows.forEach((r) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.created_at}</td>
        <td>${r.predicted_quality?.toFixed(2)}</td>
        <td>${r.quality_label}</td>
        <td>${r.alcohol?.toFixed(2)}</td>
        <td>${r.ph?.toFixed(2)}</td>
        <td>${r.fixed_acidity?.toFixed(2)}</td>
        <td>${r.volatile_acidity?.toFixed(3)}</td>
        <td>${r.sulphates?.toFixed(2)}</td>
      `;
      historyBody.appendChild(tr);
    });
  }

  async function loadHistory() {
    try {
      const res = await fetch("/history");
      if (!res.ok) return;
      const data = await res.json();
      renderHistory(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = getFormData();
    if (anyEmpty(payload)) {
      alert("Please fill in all fields before predicting.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        const msg = data.error || "Prediction failed. Please try again.";
        alert(msg);
        return;
      }

      updateResultPanel(data.predicted_quality, data.quality_label);
      await loadHistory();
    } catch (err) {
      console.error(err);
      alert("Something went wrong while calling the server.");
    } finally {
      setLoading(false);
    }
  });

  // Load history whenever the modal is opened
  const historyModal = document.getElementById("historyModal");
  if (historyModal) {
    historyModal.addEventListener("shown.bs.modal", () => {
      loadHistory();
    });
  }
});
-----------
