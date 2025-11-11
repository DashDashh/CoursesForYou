const urlParams = new URLSearchParams(window.location.search);
const courseId = urlParams.get("id");

const API_BASE_URL = "http://127.0.0.1:5000/api";

function getCurrentUser() {
  const userData = localStorage.getItem("user");
  if (userData) {
    try {
      return JSON.parse(userData);
    } catch (e) {
      console.error("Error parsing user data:", e);
      return null;
    }
  }
  return null;
}

function checkAuth() {
  const user = getCurrentUser();
  if (!user) {
    alert("Для выполнения этого действия необходимо войти в систему");
    window.location.href = "login.html";
    return false;
  }
  return true;
}

async function submitComment() {
  if (!checkAuth()) {
    return;
  }

  const commentText = document.getElementById("commentText").value.trim();

  if (!commentText) {
    alert("Пожалуйста, введите текст отзыва");
    return;
  }

  try {
    const currentUser = getCurrentUser();
    console.log("Current user:", currentUser);

    if (!currentUser || !currentUser.id) {
      alert("Ошибка: пользователь не найден. Пожалуйста, войдите заново.");
      localStorage.removeItem("user");
      window.location.href = "login.html";
      return;
    }

    const response = await fetch(`${API_BASE_URL}/reviews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: currentUser.id,
        course_id: parseInt(courseId),
        text: commentText,
      }),
    });

    if (response.ok) {
      const result = await response.json();
      document.getElementById("commentText").value = "";
      loadComments();
      alert("Отзыв успешно добавлен!");
    } else {
      const errorData = await response.json();
      alert(`Ошибка при отправке отзыва: ${errorData.error}`);
    }
  } catch (error) {
    console.error("Ошибка отправки комментария:", error);
    alert("Ошибка при отправке отзыва");
  }
}

async function loadCourseData() {
  try {
    const response = await fetch(`${API_BASE_URL}/course/${courseId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const course = await response.json();

    document.getElementById("courseTitle").textContent =
      course.name || course.title;
    document.getElementById("courseInstructor").textContent = `Преподаватель: ${
      course.teacher?.login_display ||
      course.teacher?.login ||
      "Неизвестный преподаватель"
    }`;
    document.getElementById(
      "courseLevel"
    ).textContent = `Уровень: ${course.level}`;
    document.getElementById("courseTheme").textContent = `Тема: ${
      course.theme?.name || course.theme_name || "Без темы"
    }`;
    document.getElementById("courseDescription").textContent =
      course.description || "Описание отсутствует";
  } catch (error) {
    console.error("Ошибка загрузки данных курса:", error);
    document.getElementById("courseTitle").textContent =
      "Ошибка загрузки курса";
    document.getElementById("courseDescription").textContent =
      "Не удалось загрузить информацию о курсе";
  }
}

async function loadModules() {
  try {
    const response = await fetch(`${API_BASE_URL}/courses/${courseId}/modules`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const modules = data.modules || data;

    const moduleList = document.getElementById("moduleList");
    moduleList.innerHTML = "";

    if (modules.length === 0) {
      moduleList.innerHTML = "<p>В этом курсе пока нет модулей</p>";
      return;
    }

    modules.forEach((module) => {
      const moduleElement = document.createElement("div");
      moduleElement.className = "module-item";
      moduleElement.onclick = () => openModule(module.id);

      const statusText = getStatusText(module.status);

      moduleElement.innerHTML = `
                <div class="module-header">
                    <div class="module-title">
                        Модуль ${module.number || module.order_number}: ${
        module.name || module.title
      }
                    </div>
                    <div class="module-status">${statusText}</div>
                </div>
            `;

      moduleList.appendChild(moduleElement);
    });
  } catch (error) {
    console.error("Ошибка загрузки модулей:", error);
    document.getElementById("moduleList").innerHTML =
      "<p>Ошибка загрузки модулей</p>";
  }
}

async function loadComments() {
  try {
    const response = await fetch(`${API_BASE_URL}/reviews/course/${courseId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    const comments = data.reviews || data;

    const commentsList = document.getElementById("commentsList");
    commentsList.innerHTML = "";

    if (comments.length === 0) {
      commentsList.innerHTML = "<p>Пока нет отзывов. Будьте первым!</p>";
      return;
    }

    comments.forEach((comment) => {
      const commentElement = document.createElement("div");
      commentElement.className = "comment-item";

      commentElement.innerHTML = `
                <div class="comment-header">
                    <span class="comment-author">${
                      comment.username || `Пользователь ${comment.user_id}`
                    }</span>
                    <span class="comment-date">${new Date(
                      comment.date || comment.created_at
                    ).toLocaleDateString()}</span>
                </div>
                <div class="comment-text">${comment.text}</div>
            `;

      commentsList.appendChild(commentElement);
    });
  } catch (error) {
    console.error("Ошибка загрузки комментариев:", error);
    document.getElementById("commentsList").innerHTML =
      "<p>Ошибка загрузки отзывов</p>";
  }
}

async function submitComment() {
  if (!checkAuth()) {
    return;
  }

  const commentText = document.getElementById("commentText").value.trim();

  if (!commentText) {
    alert("Пожалуйста, введите текст отзыва");
    return;
  }

  try {
    const currentUser = getCurrentUser();
    console.log("Current user:", currentUser);

    if (!currentUser || !currentUser.id) {
      alert("Ошибка: пользователь не найден. Пожалуйста, войдите заново.");
      localStorage.removeItem("user");
      window.location.href = "login.html";
      return;
    }

    const response = await fetch(`${API_BASE_URL}/reviews`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: currentUser.id,
        course_id: parseInt(courseId),
        text: commentText,
      }),
    });

    if (response.ok) {
      const result = await response.json();
      document.getElementById("commentText").value = "";
      loadComments();
      alert("Отзыв успешно добавлен!");
    } else {
      const errorData = await response.json();
      alert(`Ошибка при отправке отзыва: ${errorData.error}`);
    }
  } catch (error) {
    console.error("Ошибка отправки комментария:", error);
    alert("Ошибка при отправке отзыва");
  }
}

function openModule(moduleId) {
  window.location.href = `module.html?course_id=${courseId}&module_id=${moduleId}`;
}

function getStatusText(status) {
  switch (status) {
    case "completed":
      return "Завершено";
    case "in_progress":
      return "В процессе";
    default:
      return "Не начато";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (!courseId) {
    alert("Курс не найден");
    window.location.href = "my-courses.html";
    return;
  }

  loadCourseData();
  loadModules();
  loadComments();
});
