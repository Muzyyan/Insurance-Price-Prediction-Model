const API_BASE = "http://localhost:8000";
const form = document.getElementById("predict-form");
const submitBtn = document.getElementById("submit-btn");
const btnLabel = submitBtn.querySelector(".btn-label");
const btnSpinner = submitBtn.querySelector(".btn-spinner");
const errorMsg = document.getElementById("error-msg");

const resultEmpty = document.getElementById("result-empty");
const resultContent = document.getElementById("result-content");
const resultAmount = document.getElementById("result-amount");
const tagBmi = document.getElementById("tag-bmi");
const resultBreakdown = document.getElementById("result-breakdown");

const bmiInput = document.getElementById("bmi");
const bmiHint = document.getElementById("bmi-hint");

// ---- Segmented controls (sex / smoker) ----
document.querySelectorAll(".segmented").forEach((group) => {
  group.addEventListener("click", (e) => {
    const btn = e.target.closest(".seg-btn");
    if (!btn) return;
    group.querySelectorAll(".seg-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  });
});

function getSegmentedValue(name) {
  const group = document.querySelector(`.segmented[data-name="${name}"]`);
  return group.querySelector(".seg-btn.active").dataset.value;
}

// ---- Live BMI category hint ----
function bmiCategory(bmi) {
  if (bmi < 18.5) return "Underweight";
  if (bmi < 24.9) return "Normal";
  if (bmi < 29.9) return "Overweight";
  return "Obese";
}

function updateBmiHint() {
  const val = parseFloat(bmiInput.value);
  bmiHint.textContent = Number.isFinite(val) && val > 0 ? `— ${bmiCategory(val)}` : "";
}
bmiInput.addEventListener("input", updateBmiHint);
updateBmiHint();

// ---- Form submit ----
function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  btnSpinner.hidden = !isLoading;
  btnLabel.textContent = isLoading ? "Calculating…" : "Predict Charge";
}

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.hidden = false;
}

function hideError() {
  errorMsg.hidden = true;
  errorMsg.textContent = "";
}

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(amount);
}

function renderResult(data) {
  resultEmpty.hidden = true;
  resultContent.hidden = false;

  resultAmount.textContent = formatCurrency(data.predicted_charge);
  tagBmi.textContent = `BMI: ${data.bmi_category}`;

  const rows = [
    ["Age", data.inputs.age],
    ["Sex", data.inputs.sex],
    ["BMI", data.inputs.bmi],
    ["Children", data.inputs.children],
    ["Smoker", data.inputs.smoker],
    ["Region", data.inputs.region],
  ];

  resultBreakdown.innerHTML = rows
    .map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`)
    .join("");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();

  const payload = {
    age: Number(document.getElementById("age").value),
    sex: getSegmentedValue("sex"),
    bmi: Number(document.getElementById("bmi").value),
    children: Number(document.getElementById("children").value),
    smoker: getSegmentedValue("smoker"),
    region: document.getElementById("region").value,
  };

  setLoading(true);
  try {
    const res = await fetch(`${API_BASE}/api/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      const detail = errBody.detail
        ? Array.isArray(errBody.detail)
          ? errBody.detail.map((d) => d.msg).join("; ")
          : errBody.detail
        : `Request failed (${res.status})`;
      throw new Error(detail);
    }

    const data = await res.json();
    renderResult(data);
  } catch (err) {
    showError(err.message || "Something went wrong. Please try again.");
  } finally {
    setLoading(false);
  }
});
