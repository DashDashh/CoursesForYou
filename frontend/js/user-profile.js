const API_BASE_URL = "https://localhost:5000/api";

// Получаем параметры из URL
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get("id");
const userLogin = urlParams.get("login");

async function loadUserProfile() {
  try {
    let userData;

    if (userId) {
      // Загружаем по ID
      userData = await loadUserById(userId);
    } else if (userLogin) {
      // Загружаем по логину
      userData = await loadUserByLogin(userLogin);
    } else {
      document.getElementById("userData").innerHTML =
        "<p>Пользователь не указан</p>";
      return;
    }

    if (userData) {
      showUserData(userData);
    } else {
      document.getElementById("userData").innerHTML =
        "<p>Пользователь не найден</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки профиля:", error);
    document.getElementById("userData").innerHTML =
      "<p>Ошибка загрузки профиля</p>";
  }
}

async function loadUserById(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`);
    if (response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error("Ошибка загрузки пользователя по ID:", error);
    return null;
  }
}

async function loadUserByLogin(login) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/users/search?login=${encodeURIComponent(login)}`
    );
    if (response.ok) {
      const users = await response.json();
      return users.length > 0 ? users[0] : null;
    }
    return null;
  } catch (error) {
    console.error("Ошибка загрузки пользователя по логину:", error);
    return null;
  }
}

function showUserData(userData) {
  const userDataDiv = document.getElementById("userData");

  const avatarHtml = userData.avatar_path
    ? `<img src="${userData.avatar_path}" alt="Аватар" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd;">`
    : `<div style="width: 150px; height: 150px; border-radius: 50%; background: #ddd; display: flex; align-items: center; justify-content: center; border: 2px solid #ccc;">
             <span style="color: #666;">Нет аватара</span>
           </div>`;

  const login = (userData.login || "Не указан").replace("@", "");
  const about = userData.about || "Информация о себе не указана";
  const registerDate = userData.register_date
    ? new Date(userData.register_date).toLocaleDateString("ru-RU")
    : "Неизвестно";

  userDataDiv.innerHTML = `
        <div style="max-width: 500px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; text-align: center;">
            <div style="margin-bottom: 20px;">
                ${avatarHtml}
            </div>
            
            <div style="text-align: left; margin-top: 20px;">
                <div style="margin-bottom: 15px;">
                    <strong>Логин:</strong>
                    <div style="padding: 8px; background: #f5f5f5; border-radius: 5px; margin-top: 5px;">
                        ${login}
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <strong>О себе:</strong>
                    <div style="padding: 8px; background: #f5f5f5; border-radius: 5px; margin-top: 5px; min-height: 60px;">
                        ${about}
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <strong>Дата регистрации:</strong>
                    <div style="padding: 8px; background: #f5f5f5; border-radius: 5px; margin-top: 5px;">
                        ${registerDate}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function goBack() {
  window.history.back();
}

document.addEventListener("DOMContentLoaded", loadUserProfile);
