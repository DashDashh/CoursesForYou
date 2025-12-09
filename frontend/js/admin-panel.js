const API_BASE_URL = "http://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

function checkAdminAuth() {
  const userData = localStorage.getItem("user");
  if (!userData) {
    window.location.href = "login.html";
    return false;
  }

  const user = JSON.parse(userData);
  if (user.role !== 1) {
    window.location.href = "profile.html";
    return false;
  }

  return true;
}

function logout() {
  localStorage.removeItem("user");
  window.location.href = "login.html";
}

function showSection(sectionId) {
  document.getElementById("themes-section").style.display = "none";
  document.getElementById("users-section").style.display = "none";
  document.getElementById("courses-section").style.display = "none";

  document.getElementById(sectionId + "-section").style.display = "block";

  switch (sectionId) {
    case "themes":
      loadThemes();
      break;
    case "users":
      loadUsers();
      break;
    case "courses":
      loadStats();
      break;
  }
}

async function loadThemes() {
  try {
    console.log("Loading themes from:", `${API_BASE_URL}/themes`);

    const response = await fetch(`${API_BASE_URL}/themes`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    console.log("Response status:", response.status);

    const themesList = document.getElementById("themesList");

    if (response.ok) {
      const data = await response.json();
      console.log("Themes data:", data);

      const themes = data.themes;

      if (!themes || themes.length === 0) {
        themesList.innerHTML = "<p>Темы пока не добавлены</p>";
        return;
      }

      themesList.innerHTML = themes
        .map(
          (theme) => `
          <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0;">
            <strong>${theme.name}</strong>
            <span style="float: right; color: #666; font-size: 14px;">
              ID: ${theme.id}
            </span>
          </div>
        `
        )
        .join("");
    } else {
      const errorText = await response.text();
      console.error("Error response:", errorText);
      themesList.innerHTML = "<p>Ошибка загрузки тем</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки тем:", error);
    document.getElementById("themesList").innerHTML =
      "<p>Ошибка соединения</p>";
  }
}

async function addTheme() {
  const themeName = document.getElementById("themeName").value.trim();

  if (!themeName) {
    alert("Введите название темы");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/themes`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        name: themeName,
      }),
    });

    if (response.ok) {
      alert("Тема успешно добавлена");
      document.getElementById("themeName").value = "";
      loadThemes();
    } else {
      const errorData = await response.json();
      alert("Ошибка: " + (errorData.error || "Не удалось добавить тему"));
    }
  } catch (error) {
    console.error("Ошибка добавления темы:", error);
    alert("Ошибка соединения с сервером");
  }
}

async function loadUsers() {
  try {
    console.log("=== DEBUG: loadUsers called ===");

    const url = `${API_BASE_URL}/users/all`;
    console.log("Fetching URL:", url);

    const headers = getAuthHeaders();
    console.log("Headers:", headers);

    const response = await fetch(url, {
      method: "GET",
      headers: headers,
    });

    console.log("Response status:", response.status);
    console.log("Response headers:", response.headers);

    const usersList = document.getElementById("usersList");

    if (response.ok) {
      const users = await response.json();
      console.log("Users data received:", users);

      if (users.length === 0) {
        usersList.innerHTML = "<p>Пользователи не найдены</p>";
        return;
      }

      displayUsers(users);
    } else {
      console.error("Response not OK, status:", response.status);
      const errorText = await response.text();
      console.error("Error response text:", errorText);
      usersList.innerHTML = `<p>Ошибка загрузки пользователей: ${response.status}</p>`;
    }
  } catch (error) {
    console.error("Exception in loadUsers:", error);
    console.error("Error stack:", error.stack);
    document.getElementById(
      "usersList"
    ).innerHTML = `<p>Ошибка соединения: ${error.message}</p>`;
  }
}

function displayUsers(users) {
  const usersList = document.getElementById("usersList");

  usersList.innerHTML = users
    .map(
      (user) => `
      <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0;">
        <div>
          <strong>Логин:</strong> 
          <a href="user-profile.html?id=${
            user.id
          }" style="color: #0066cc; text-decoration: none; font-weight: normal;">
            ${user.login}
          </a>
          <span style="float: right; color: ${
            user.role === 1 ? "red" : "blue"
          }">
            ${user.role === 1 ? "Админ" : "Пользователь"}
          </span>
        </div>
        <div>
          <strong>ID:</strong> ${user.id}
          <strong style="margin-left: 20px;">Дата регистрации:</strong> ${
            user.register_date
              ? new Date(user.register_date).toLocaleDateString()
              : "Нет данных"
          }
        </div>
        <div style="margin-top: 10px;">
          <button onclick="deleteUser(${
            user.id
          })" style="background: red; color: white; border: none; padding: 5px 10px;">
            Удалить
          </button>
        </div>
      </div>
    `
    )
    .join("");
}

async function deleteUser(userId) {
  if (
    !confirm(
      "Вы уверены, что хотите удалить пользователя? Это действие нельзя отменить."
    )
  )
    return;

  try {
    const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      alert("Пользователь успешно удален");
      loadUsers();
    } else {
      const errorData = await response.json();
      alert(
        "Ошибка: " + (errorData.error || "Не удалось удалить пользователя")
      );
    }
  } catch (error) {
    console.error("Ошибка удаления пользователя:", error);
    alert("Ошибка соединения с сервером");
  }
}

// Статистика
async function loadStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/stats`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const statsDiv = document.getElementById("stats");

    if (response.ok) {
      const stats = await response.json();
      statsDiv.innerHTML = `
        <div>
          <p><strong>Всего пользователей:</strong> ${stats.total_users || 0}</p>
          <p><strong>Всего курсов:</strong> ${stats.total_courses || 0}</p>
          <p><strong>Заблокированных пользователей:</strong> ${
            stats.banned_users || 0
          }</p>
          <p><strong>Всего отзывов:</strong> ${stats.total_reviews || 0}</p>
        </div>
      `;
    } else {
      statsDiv.innerHTML = "<p>Ошибка загрузки статистики</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки статистики:", error);
    document.getElementById("stats").innerHTML = "<p>Ошибка соединения</p>";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!checkAdminAuth()) return;

  showSection("themes");
});
