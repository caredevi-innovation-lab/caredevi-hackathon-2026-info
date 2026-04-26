const data = JSON.parse(localStorage.getItem("nutritionUser"));
const results = document.getElementById("results");

let calories = 0;
let protein = 0;
let carbs = 0;
let fat = 0;
let score = 100;
let waterLiters = 0;

if (!data) {
  results.innerHTML = `
    <p>No data found. Please fill out the form first.</p>
    <button onclick="goBack()">Go to Form</button>
  `;
} else {
  const weight = Number(data.weight);
  const height = Number(data.height);
  const age = Number(data.age);
  const activity = Number(data.activity);

  let bmr =
    data.gender === "male"
      ? 10 * weight + 6.25 * height - 5 * age + 5
      : 10 * weight + 6.25 * height - 5 * age - 161;

  calories = Math.round(bmr * activity);

  let goalMessage = "";

  if (data.goal === "lose") {
    calories -= 300;
    goalMessage = "You are in a slight calorie deficit to support weight loss.";
  } else if (data.goal === "gain") {
    calories += 300;
    goalMessage = "Extra calories are added to support muscle gain and recovery.";
  } else {
    goalMessage = "Calories are set to maintain your current body weight.";
  }

  protein = Math.round(weight * 1.8);
  fat = Math.round((calories * 0.25) / 9);
  carbs = Math.round((calories - (protein * 4 + fat * 9)) / 4);

  waterLiters = ((weight * 35) / 1000).toFixed(1);

  // health score
  if (calories < 1400) score -= 25;
  if (protein < weight * 1.2) score -= 25;
  if (fat < 30) score -= 10;
  if (score < 0) score = 0;

  let scoreMessage =
    score >= 80 ? "Good balance"
    : score >= 60 ? "Needs improvement"
    : "Low balance";

  let riskText = "";

  if (calories < 1400) {
    riskText += "⚠️ Low calorie intake may reduce energy.<br>";
  }

  if (protein < weight * 1.2) {
    riskText += "⚠️ Low protein may affect recovery.<br>";
  }

  if (riskText === "") {
    riskText = "✅ Your plan looks balanced.";
  }

  results.innerHTML = `
    <div class="score-box">
      <h2>⭐ Health Score: ${score}/100</h2>
      <p>${scoreMessage}</p>
    </div>

    <div class="result-box">
      <h2>🔥 ${calories} Calories/day</h2>
      <p>${goalMessage}</p>

      <p><strong>💪 Protein:</strong> ${protein}g</p>
      <p><strong>🍚 Carbs:</strong> ${carbs}g</p>
      <p><strong>🥑 Fat:</strong> ${fat}g</p>
    </div>

    <div class="risk-box">
      <h3>⚠️ Risk Insight</h3>
      <p>${riskText}</p>
    </div>

    <div class="water-box">
      <h3>💧 Water Goal</h3>
      <p>${waterLiters} liters per day recommended.</p>
    </div>

    <div class="explain-box">
      <h3>🧠 Decision Explanation</h3>
      <p>${goalMessage}</p>
    </div>

    <div class="culture-box">
      <h3>🌍 Culturally Adaptive Nutrition</h3>
      <p>
        FuelMate adapts to different dietary styles like South Asian,
        East Asian, African, and Western meals.
      </p>
    </div>
  `;

  createChart();
}

// chart
function createChart() {
  const chartElement = document.getElementById("macroChart");

  if (!chartElement) return;

  new Chart(chartElement, {
    type: "doughnut",
    data: {
      labels: ["Protein", "Carbs", "Fat"],
      datasets: [
        {
          data: [protein, carbs, fat]
        }
      ]
    }
  });
}

// navigation
function goBack() {
  window.location.href = "form.html";
}
function findFoodNearMe() {
  const choice = document.getElementById("eatOutChoice").value;
  const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(choice)}`;
  window.open(mapsUrl, "_blank");
}
