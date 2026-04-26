const form = document.getElementById("nutritionForm");

if (form) {
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const feet = Number(document.getElementById("feet").value);
    const inches = Number(document.getElementById("inches").value);

    const height = (feet * 12 + inches) * 2.54;

    const data = {
      age: document.getElementById("age").value,
      height,
      weight: document.getElementById("weight").value,
      gender: document.getElementById("gender").value,
      goal: document.getElementById("goal").value,
      activity: document.getElementById("activity").value
    };

    localStorage.setItem("nutritionUser", JSON.stringify(data));
    window.location.href = "result.html";
  });
}