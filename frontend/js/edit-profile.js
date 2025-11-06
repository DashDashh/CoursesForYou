const API_BASE_URL = "http://localhost:5000/api/auth";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

function showMessage(message, isError = false, formId = null) {
  let messageDiv = document.getElementById("message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.id = "message";
    document.body.insertBefore(messageDiv, document.body.firstChild);
  }

  messageDiv.textContent = message;
  messageDiv.style.color = isError ? "red" : "green";
  messageDiv.style.padding = "10px";
  messageDiv.style.margin = "10px 0";
  messageDiv.style.border = isError ? "1px solid red" : "1px solid green";

  if (formId) {
    const form = document.getElementById(formId);
    if (form) {
      form.insertBefore(messageDiv, form.firstChild);
    }
  }
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

async function loadProfileData() {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    const response = await fetch(`${API_BASE_URL}/user_profile`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const data = await response.json();

      if (data.about) {
        document.getElementById("about").value = data.about;
      }

      if (data.avatar_path) {
        document.getElementById("avatarPath").value = data.avatar_path;
      }
    } else {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      if (user.about) {
        document.getElementById("about").value = user.about;
      }
      if (user.avatar_path) {
        document.getElementById("avatarPath").value = user.avatar_path;
      }
    }
  } catch (error) {
    console.log("Ошибка загрузки профиля:", error);
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (user.about) {
      document.getElementById("about").value = user.about;
    }
    if (user.avatar_path) {
      document.getElementById("avatarPath").value = user.avatar_path;
    }
  }
}

async function updateProfile(about) {
  try {
    const response = await fetch(`${API_BASE_URL}/update_profile`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        about: about,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showMessage("Информация успешно обновлена", false, "profileForm");
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      user.about = about;
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      showMessage(data.error || "Ошибка обновления", true, "profileForm");
    }
  } catch (error) {
    showMessage("Ошибка соединения с сервером", true, "profileForm");
  }
}

async function changePassword(currentPassword, newPassword) {
  try {
    const response = await fetch(`${API_BASE_URL}/change_password`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showMessage("Пароль успешно изменен", false, "passwordForm");
      document.getElementById("passwordForm").reset();
    } else {
      showMessage(data.error || "Ошибка смены пароля", true, "passwordForm");
    }
  } catch (error) {
    showMessage("Ошибка соединения с сервером", true, "passwordForm");
  }
}

async function updateAvatar(avatarPath) {
  try {
    const response = await fetch(`${API_BASE_URL}/update_profile`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        avatar_path: avatarPath,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showMessage("Аватар успешно обновлен", false, "avatarForm");
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      user.avatar_path = avatarPath;
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      showMessage(
        data.error || "Ошибка обновления аватара",
        true,
        "avatarForm"
      );
    }
  } catch (error) {
    showMessage("Ошибка соединения с сервером", true, "avatarForm");
  }
}

function initForms() {
  const profileForm = document.getElementById("profileForm");
  if (profileForm) {
    profileForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const about = document.getElementById("about").value;
      await updateProfile(about);
    });
  }

  const passwordForm = document.getElementById("passwordForm");
  if (passwordForm) {
    passwordForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const currentPassword = document.getElementById("currentPassword").value;
      const newPassword = document.getElementById("newPassword").value;
      const confirmPassword = document.getElementById("confirmPassword").value;

      if (!currentPassword || !newPassword || !confirmPassword) {
        showMessage("Заполните все поля", true, "passwordForm");
        return;
      }

      if (newPassword !== confirmPassword) {
        showMessage("Новые пароли не совпадают", true, "passwordForm");
        return;
      }

      const passwordErrors = validatePassword(newPassword);
      if (passwordErrors.length > 0) {
        showMessage(
          "Пароль должен содержать: " + passwordErrors.join(", "),
          true,
          "passwordForm"
        );
        return;
      }

      await changePassword(currentPassword, newPassword);
    });
  }

  const avatarForm = document.getElementById("avatarForm");
  if (avatarForm) {
    avatarForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const avatarPath = document.getElementById("avatarPath").value;
      await updateAvatar(avatarPath);
    });
  }
}

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  } else {
    console.log("Пользователь авторизован:", JSON.parse(user));
  }
}

document.addEventListener("DOMContentLoaded", function () {
  checkAuth();
  initForms();
  loadProfileData();
});
