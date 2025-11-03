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

function validatePassword(password) {
  const errors = [];

  if (password.length < 8) errors.push("не менее 8 символов");
  if (!/(?=.*[a-z])/.test(password)) errors.push("строчные буквы");
  if (!/(?=.*[A-Z])/.test(password)) errors.push("заглавные буквы");
  if (!/(?=.*\d)/.test(password)) errors.push("цифры");
  if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(password))
    errors.push("специальные символы");

  return errors;
}

async function register(login, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        login: login,
        password: password,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showMessage("Регистрация успешна! Перенаправляем...", false);
      setTimeout(() => {
        window.location.href = "login.html";
      }, 2000);
    } else {
      showMessage(data.error || "Ошибка регистрации", true);
    }
  } catch (error) {
    showMessage("Ошибка соединения с сервером", true);
  }
}

function initRegisterForm() {
  const form = document.getElementById("registerForm");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (!login || !password) {
      showMessage("Заполните все поля", true);
      return;
    }

    const passwordErrors = validatePassword(password);
    if (passwordErrors.length > 0) {
      showMessage(
        "Пароль должен содержать: " + passwordErrors.join(", "),
        true
      );
      return;
    }

    if (password !== confirmPassword) {
      showMessage("Пароли не совпадают", true);
      return;
    }

    await register(login, password);
  });
}

document.addEventListener("DOMContentLoaded", initRegisterForm);
