const API_BASE_URL = "https://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

// Функция для форматирования логина (убирает @ в начале)
function formatLogin(login) {
  if (!login) return "Неизвестно";
  return login.replace(/^@/, "");
}

// Функция для получения прогресса курса
async function getCourseProgress(courseId) {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (!user.id) return 0;

    const response = await fetch(
      `${API_BASE_URL}/user_progress/user/${user.id}/course/${courseId}`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );

    if (response.ok) {
      const progress = await response.json();
      return progress.progress_percentage || 0;
    } else {
      return 0;
    }
  } catch (error) {
    console.error(`Ошибка загрузки прогресса для курса ${courseId}:`, error);
    return 0;
  }
}

async function loadMyCourses() {
  try {
    const response = await fetch(`${API_BASE_URL}/my_courses`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const myCoursesDiv = document.getElementById("myCourses");

    if (response.ok) {
      const courses = await response.json();

      if (courses.length === 0) {
        myCoursesDiv.innerHTML = `
          <div>
            <h3>У вас пока нет курсов</h3>
            <p>Выберите курс из каталога чтобы начать обучение</p>
            <a href="catalog.html">
              <button>Перейти в каталог</button>
            </a>
          </div>
        `;
        return;
      }

      // Загружаем прогресс для каждого курса
      const coursesWithProgress = await Promise.all(
        courses.map(async (course) => {
          const progress = await getCourseProgress(course.id);
          return {
            ...course,
            progress: progress,
          };
        })
      );

      myCoursesDiv.innerHTML = coursesWithProgress
        .map(
          (course) => `
          <div>
            <h3>${course.title || course.name}</h3>
            <p>${course.description || "Описание отсутствует"}</p>
            <p>
              <strong>Автор:</strong> 
              <a href="user-profile.html?id=${
                course.id_teacher || course.teacher_id
              }" style="color: #007bff; text-decoration: none;">
                ${formatLogin(
                  course.author_display || course.author || "Неизвестно"
                )}
              </a>
            </p>
            <p><strong>Прогресс:</strong> ${course.progress}%</p>
            <button onclick="openCourse(${course.id})">
              ${
                course.progress === 0
                  ? "Начать обучение"
                  : "Продолжить обучение"
              }
            </button>
          </div>
        `
        )
        .join("");
    } else {
      myCoursesDiv.innerHTML = "<p>Ошибка загрузки ваших курсов</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки моих курсов:", error);
    document.getElementById("myCourses").innerHTML =
      "<p>Ошибка соединения с сервером</p>";
  }
}

function openCourse(courseId) {
  window.location.href = `course.html?id=${courseId}`;
}

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  checkAuth();
  loadMyCourses();
});
