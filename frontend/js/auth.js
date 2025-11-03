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

async function register(login, password) {
  try {
    const response = await fetch("${API_BASE_URL}/register", {
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
      showMessage("Регистрация успешна!", false);

      localStorage.setItem(
        "user",
        JSON.stringify({
          id: data.user_id,
          login: data.login,
        })
      );

      setTimeout(() => {
        window.location.href = "login.html";
      }, 2000);
    } else {
      showMessage(data.error || "Ошибка регистрации", true);
    }
  } catch (error) {
    console.error("Error:", error);
    showMessage("Ошибка соединения с сервером", true);
  }
}

function initRegisterForm() {
  const form = document.getElementById("registerForm");

  if (!form) {
    console.error("Форма регистрации не найдена");
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (!login || !password) {
      showMessage("Заполните все поля", true);
      return;
    }

    if (password.length < 6) {
      showMessage("Пароль должен быть не менее 6 символов", true);
      return;
    }

    if (password != confirmPassword) {
      showMessage("Пароли не совпали", true);
      return;
    }

    await register(login, password);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  initRegisterForm();
});
