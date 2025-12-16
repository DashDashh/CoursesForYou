const API_BASE_URL = "https://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

async function loadUserProfile() {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    if (user.id) {
      showUserData(user);
    }

    const response = await fetch(`${API_BASE_URL}/auth/user_profile`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const profileData = await response.json();
      showUserData(profileData);
    } else {
      showUserData(user);
    }
  } catch (error) {
    console.error("Ошибка загрузки профиля:", error);
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    showUserData(user);
  }
}

function showUserData(userData) {
  const userDataDiv = document.getElementById("userData");

  const avatarHtml = userData.avatar_path
    ? `<img src="${userData.avatar_path}" alt="Аватар" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd;">`
    : `<div style="width: 150px; height: 150px; border-radius: 50%; background: #ddd; display: flex; align-items: center; justify-content: center; border: 2px solid #ccc;">
             <span style="color: #666;">Нет аватара</span>
           </div>`;

  const login = userData.login || "Не указан";

  const about = userData.about || "Информация о себе не указана";

  const registerDate = userData.register_date
    ? new Date(userData.register_date).toLocaleDateString("ru-RU")
    : new Date().toLocaleDateString("ru-RU");

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

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

async function initProfile() {
  checkAuth();
  await loadUserProfile();
}

document.addEventListener("DOMContentLoaded", initProfile);
