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

// Загрузка прогресса курса
async function loadCourseProgress() {
  try {
    const user = getCurrentUser();
    if (!user) {
      // Если пользователь не авторизован, скрываем или показываем базовую информацию
      document.getElementById("courseProgress").style.display = "none";
      return;
    }

    const response = await fetch(
      `${API_BASE_URL}/user_progress/user/${user.id}/course/${courseId}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const progress = await response.json();
    console.log("Course progress:", progress);

    // Обновляем прогресс-бар
    const progressElement = document.getElementById("courseProgress");
    const progressFill = document.getElementById("progressFill");
    const progressText = document.getElementById("progressText");

    if (progressFill) {
      progressFill.style.width = `${progress.progress_percentage || 0}%`;
    }

    if (progressText) {
      progressText.textContent = `Прогресс: ${progress.completed_steps || 0}/${
        progress.total_steps || 0
      } шагов (${progress.progress_percentage || 0}%)`;
    } else {
      // Создаем элемент для отображения прогресса, если его нет
      const progressInfo = document.createElement("div");
      progressInfo.id = "progressText";
      progressInfo.className = "progress-info";
      progressInfo.textContent = `Прогресс: ${progress.completed_steps || 0}/${
        progress.total_steps || 0
      } шагов (${progress.progress_percentage || 0}%)`;

      const progressContainer =
        document.getElementById("courseProgress") ||
        document.querySelector(".course-info");
      if (progressContainer) {
        progressContainer.appendChild(progressInfo);
      }
    }
  } catch (error) {
    console.error("Ошибка загрузки прогресса курса:", error);
    // Скрываем прогресс при ошибке
    document.getElementById("courseProgress").style.display = "none";
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

    // Загружаем прогресс после загрузки основных данных
    await loadCourseProgress();
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

    // Загружаем прогресс для каждого модуля
    const user = getCurrentUser();
    let moduleProgressData = [];

    if (user) {
      try {
        // Получаем прогресс по всем модулям курса
        for (const module of modules) {
          const progressResponse = await fetch(
            `${API_BASE_URL}/user_progress/user/${user.id}/module/${module.id}`
          );
          if (progressResponse.ok) {
            const moduleProgress = await progressResponse.json();
            moduleProgressData[module.id] = moduleProgress;
          }
        }
      } catch (error) {
        console.error("Ошибка загрузки прогресса модулей:", error);
      }
    }

    modules.forEach((module) => {
      const moduleElement = document.createElement("div");
      moduleElement.className = "module-item";
      moduleElement.onclick = () => openModule(module.id);

      // Получаем прогресс модуля
      const moduleProgress = moduleProgressData[module.id];
      const completedSteps = moduleProgress?.completed_steps || 0;
      const totalSteps = moduleProgress?.total_steps || 0;

      let statusText = "Не начато";
      let statusClass = "status-not-started";

      if (totalSteps > 0) {
        if (completedSteps === totalSteps) {
          statusText = `Завершено (${completedSteps}/${totalSteps})`;
          statusClass = "status-completed";
        } else if (completedSteps > 0) {
          statusText = `В процессе (${completedSteps}/${totalSteps})`;
          statusClass = "status-in-progress";
        } else {
          statusText = `Не начато (0/${totalSteps})`;
        }
      }

      moduleElement.innerHTML = `
        <div class="module-header">
          <div class="module-title">
            Модуль ${module.number || module.order_number}: ${
        module.name || module.title
      }
          </div>
          <div class="module-status ${statusClass}">${statusText}</div>
        </div>
        ${
          totalSteps > 0
            ? `
        <div class="module-progress">
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${
              (completedSteps / totalSteps) * 100
            }%"></div>
          </div>
        </div>
        `
            : ""
        }
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
