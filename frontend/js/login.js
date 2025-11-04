const API_BASE_URL = "http://localhost:5000/api/auth";

function showMessage(message, isError = false) {
  let messageDiv = document.getElementById("message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.id = "message";
    document.querySelector("form").appendChild(messageDiv);
  }

  messageDiv.textContent = message;
  messageDiv.style.color = isError ? "red" : "green";
}

async function loginUser(username, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        login: username,
        password: password,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showMessage("Вход выполнен успешно! Перенаправляем...", false);

      localStorage.setItem("user", JSON.stringify(data.user));

      window.location.href = "profile.html";
    } else {
      showMessage(data.error || "Ошибка входа", true);
    }
  } catch (error) {
    showMessage("Ошибка соединения с сервером", true);
  }
}

function initLoginForm() {
  const form = document.getElementById("loginForm");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
      showMessage("Заполните все поля", true);
      return;
    }

    await loginUser(username, password);
  });
}

document.addEventListener("DOMContentLoaded", initLoginForm);
