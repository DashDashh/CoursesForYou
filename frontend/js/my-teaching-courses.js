const API_BASE_URL = "https://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

async function loadTeachingCourses() {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    console.log("Загружаем курсы для преподавателя ID:", user.id);
    console.log(
      "URL запроса:",
      `${API_BASE_URL}/courses?teacher_id=${user.id}`
    );

    const response = await fetch(
      `${API_BASE_URL}/courses?teacher_id=${user.id}`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );

    const coursesDiv = document.getElementById("teachingCourses");

    console.log("Статус ответа:", response.status);

    if (response.ok) {
      const courses = await response.json();
      console.log("Получены курсы:", courses);

      const myCourses = courses.filter(
        (course) => course.id_teacher == user.id
      );
      console.log("Мои курсы после фильтрации:", myCourses);

      if (myCourses.length === 0) {
        coursesDiv.innerHTML = `
                    <div>
                        <h3>У вас пока нет курсов для преподавания</h3>
                        <p>Создайте свой первый курс!</p>
                        <a href="course-editor.html">
                            <button>Создать курс</button>
                        </a>
                    </div>
                `;
        return;
      }

      coursesDiv.innerHTML = myCourses
        .map(
          (course) => `
                <div>
                    <h3>${course.name || course.title || "Без названия"}</h3>
                    <p>${course.description || "Описание отсутствует"}</p>
                    <p><strong>Уровень:</strong> ${getLevelName(
                      course.level
                    )}</p>
                    <p><strong>Студентов:</strong> ${
                      course.students_count || 0
                    }</p>
                    <p><strong>Рейтинг:</strong> ${
                      course.rating || "нет оценок"
                    }</p>
                    <div>
                        <a href="course-editor.html?id=${course.id}">
                            <button>Редактировать курс</button>
                        </a>
                    </div>
                </div>
            `
        )
        .join("");
    } else {
      const errorText = await response.text();
      console.error("Ошибка загрузки курсов:", errorText);
      coursesDiv.innerHTML = "<p>Ошибка загрузки курсов</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки курсов:", error);
    document.getElementById("teachingCourses").innerHTML = `
            <div>
                <p>Ошибка соединения с сервером</p>
                <p>Убедитесь, что сервер запущен</p>
            </div>
        `;
  }
}

function getLevelName(level) {
  const levels = {
    1: "Начинающий",
    2: "Продолжающий",
    3: "Средний",
    4: "Продвинутый",
    5: "Эксперт",
  };
  return levels[level] || "Неизвестно";
}

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

async function initTeachingCourses() {
  checkAuth();
  await loadTeachingCourses();
}

document.addEventListener("DOMContentLoaded", initTeachingCourses);
