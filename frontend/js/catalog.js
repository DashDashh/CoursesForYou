const API_BASE_URL = "https://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

async function loadAllCourses() {
  try {
    const response = await fetch(`${API_BASE_URL}/courses`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const allCoursesDiv = document.getElementById("allCourses");

    if (response.ok) {
      const courses = await response.json();

      if (courses.length === 0) {
        allCoursesDiv.innerHTML = "<p>Курсы пока отсутствуют</p>";
        return;
      }

      allCoursesDiv.innerHTML = courses
        .map(
          (course) => `
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3>${course.title || course.name}</h3>
                <p>${course.description || "Описание отсутствует"}</p>
                <p><strong>Автор:</strong> 
                  <a href="user-profile.html?id=${
                    course.id_teacher
                  }" style="color: #007bff; text-decoration: none;">
                    ${course.author_display || course.author || "Неизвестно"}
                  </a>
                </p>
                <p><strong>Рейтинг:</strong> ${
                  course.rating || "нет оценок"
                }</p>
                <p><strong>Студентов:</strong> ${course.students_count || 0}</p>
                <button onclick="enrollInCourse(${
                  course.id
                })">Записаться на курс</button>
            </div>
        `
        )
        .join("");
    } else {
      allCoursesDiv.innerHTML = "<p>Ошибка загрузки каталога курсов</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки всех курсов:", error);
    document.getElementById("allCourses").innerHTML =
      "<p>Ошибка соединения с сервером</p>";
  }
}

async function searchCourses() {
  const searchTerm = document.getElementById("searchInput").value.trim();

  if (!searchTerm) {
    loadAllCourses();
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/courses/search?q=${encodeURIComponent(searchTerm)}`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );

    const allCoursesDiv = document.getElementById("allCourses");

    if (response.ok) {
      const courses = await response.json();

      if (courses.length === 0) {
        allCoursesDiv.innerHTML = "<p>Курсы по вашему запросу не найдены</p>";
        return;
      }

      allCoursesDiv.innerHTML = courses
        .map(
          (course) => `
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3>${course.title || course.name}</h3>
                <p>${course.description || "Описание отсутствует"}</p>
                <p><strong>Автор:</strong> 
                  <a href="user-profile.html?id=${
                    course.id_teacher
                  }" style="color: #007bff; text-decoration: none;">
                    ${course.author_display || course.author || "Неизвестно"}
                  </a>
                </p>
                <p><strong>Рейтинг:</strong> ${
                  course.rating || "нет оценок"
                }</p>
                <button onclick="enrollInCourse(${
                  course.id
                })">Записаться на курс</button>
            </div>
        `
        )
        .join("");
    } else {
      allCoursesDiv.innerHTML = "<p>Ошибка поиска курсов</p>";
    }
  } catch (error) {
    console.error("Ошибка поиска:", error);
    document.getElementById("allCourses").innerHTML =
      "<p>Ошибка соединения с сервером</p>";
  }
}

async function enrollInCourse(courseId) {
  try {
    console.log("Пытаемся записаться на курс ID:", courseId);

    const user = JSON.parse(localStorage.getItem("user") || "{}");
    console.log("Текущий пользователь:", user);

    const response = await fetch(`${API_BASE_URL}/enroll`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        course_id: courseId,
      }),
    });

    console.log("Статус ответа:", response.status);
    console.log("OK?", response.ok);

    if (response.ok) {
      const data = await response.json();
      console.log("Успешная запись:", data);
      alert("Вы успешно записались на курс!");

      if (confirm("Перейти к вашим курсам?")) {
        window.location.href = "my-courses.html";
      }
    } else {
      const data = await response.json();
      console.error("Ошибка записи:", data);
      alert(data.error || "Ошибка записи на курс");
    }
  } catch (error) {
    console.error("Ошибка соединения:", error);
    alert("Ошибка соединения с сервером");
  }
}

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  checkAuth();
  loadAllCourses();
});
