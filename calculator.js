const data = JSON.parse(localStorage.getItem("nutritionUser"));
const results = document.getElementById("results");

let calories, protein, carbs, fat;

if (data) {
  const weight = Number(data.weight);
  const height = Number(data.height);
  const age = Number(data.age);
  const activity = Number(data.activity);

  let bmr =
    data.gender === "male"
      ? 10 * weight + 6.25 * height - 5 * age + 5
      : 10 * weight + 6.25 * height - 5 * age - 161;

  calories = Math.round(bmr * activity);

  if (data.goal === "lose") calories -= 300;
  if (data.goal === "gain") calories += 300;

  protein = Math.round(weight * 1.8);
  fat = Math.round((calories * 0.25) / 9);
  carbs = Math.round((calories - (protein * 4 + fat * 9)) / 4);

  results.innerHTML = `
    <p>🔥 Calories: ${calories}</p>
    <p>💪 Protein: ${protein}g</p>
    <p>🍞 Carbs: ${carbs}g</p>
    <p>🥑 Fat: ${fat}g</p>
  `;

  new Chart(document.getElementById("macroChart"), {
    type: "doughnut",
    data: {
      labels: ["Protein", "Carbs", "Fat"],
      datasets: [{
        data: [protein, carbs, fat]
      }]
    }
  });
}

function eatNow(type) {
  const box = document.getElementById("eatSuggestion");

  if (type === "hungry") {
    box.innerHTML = "🍛 Dal bhat + eggs is a great balanced meal.";
  }

  if (type === "workout") {
    box.innerHTML = "💪 Banana + milk or chicken + rice helps recovery.";
  }

  if (type === "energy") {
    box.innerHTML = "⚡ Banana, yogurt, or peanuts for quick energy.";
  }
}

function goBack() {
  window.location.href = "form.html";
}

function mealReminder() {
  const hour = new Date().getHours();
  const box = document.getElementById("mealReminder");

  if (hour < 10) box.innerHTML = "🌅 Breakfast time!";
  else if (hour < 15) box.innerHTML = "🍛 Lunch time!";
  else if (hour < 21) box.innerHTML = "🌙 Dinner time!";
  else box.innerHTML = "🍌 Light snack time.";
}

mealReminder();