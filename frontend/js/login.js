const API_BASE_URL = "https://localhost:5000/api/auth";

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
    console.log("Login response:", data); // Добавим для отладки

    if (response.ok) {
      showMessage("Вход выполнен успешно! Перенаправляем...", false);

      // Сохраняем данные пользователя
      localStorage.setItem("user", JSON.stringify(data.user));

      // Определяем куда перенаправлять по роли
      setTimeout(() => {
        redirectByRole(data.user);
      }, 1000);
    } else {
      showMessage(data.error || "Ошибка входа", true);
    }
  } catch (error) {
    console.error("Login error:", error);
    showMessage("Ошибка соединения с сервером", true);
  }
}

// Функция для перенаправления по роли
function redirectByRole(user) {
  console.log("User role:", user.role); // Для отладки

  // Проверяем оба варианта: 'admin' и 'ADMIN'
  if (user.role === "admin" || user.role === 1) {
    console.log("Redirecting to admin panel");
    window.location.href = "admin-panel.html";
  } else {
    console.log("Redirecting to user profile");
    window.location.href = "profile.html";
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

// Проверяем, не авторизован ли пользователь уже
function checkExistingAuth() {
  const userData = localStorage.getItem("user");
  if (userData) {
    try {
      const user = JSON.parse(userData);
      console.log("Existing user role:", user.role); // Для отладки
      redirectByRole(user);
    } catch (e) {
      console.error("Error parsing user data:", e);
      localStorage.removeItem("user");
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  checkExistingAuth();
  initLoginForm();
});
