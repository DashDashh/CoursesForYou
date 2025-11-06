const API_BASE_URL = "http://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
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
                    <div style="text-align: center; padding: 40px;">
                        <h3>У вас пока нет курсов</h3>
                        <p>Выберите курс из каталога чтобы начать обучение</p>
                        <a href="catalog.html">
                            <button>Перейти в каталог</button>
                        </a>
                    </div>
                `;
        return;
      }

      myCoursesDiv.innerHTML = courses
        .map(
          (course) => `
                <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                    <h3>${course.title || course.name}</h3>
                    <p>${course.description || "Описание отсутствует"}</p>
                    <p><strong>Автор:</strong> ${
                      course.author || "Неизвестно"
                    }</p>
                    <p><strong>Прогресс:</strong> ${course.progress || 0}%</p>
                    <button onclick="openCourse(${
                      course.id
                    })">Продолжить обучение</button>
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
