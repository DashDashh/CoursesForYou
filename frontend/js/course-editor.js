const API_BASE_URL = "http://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

function getCourseIdFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("id");
}

function isEditMode() {
  return getCourseIdFromURL() !== null;
}

async function loadCourseData(courseId) {
  try {
    console.log("Загружаем данные курса ID:", courseId);

    const response = await fetch(`${API_BASE_URL}/course/${courseId}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const courseData = await response.json();
      console.log("Данные курса:", courseData);

      document.getElementById("courseName").value = courseData.name || "";
      document.getElementById("courseDescription").value =
        courseData.description || "";
      document.getElementById("courseTheme").value = courseData.theme_id || "";
      document.getElementById("courseLevel").value = courseData.level || "1";

      // Показываем секцию модулей и загружаем их
      document.getElementById("modulesSection").style.display = "block";
      await loadModules(courseId);

      updateCounters();
    } else {
      console.error("Ошибка загрузки данных курса");
      alert("Ошибка загрузки данных курса");
    }
  } catch (error) {
    console.error("Ошибка загрузки курса:", error);
    alert("Ошибка соединения с сервером");
  }
}

// Загрузка модулей курса
async function loadModules(courseId) {
  try {
    console.log("Загружаем модули для курса:", courseId);

    const response = await fetch(
      `${API_BASE_URL}/courses/${courseId}/modules`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );

    if (response.ok) {
      const data = await response.json();
      console.log("Получены данные модулей:", data);
      displayModules(data);
    } else {
      console.error("Ошибка загрузки модулей");
      document.getElementById("modulesList").innerHTML =
        "<p>Ошибка загрузки модулей</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки модулей:", error);
    document.getElementById("modulesList").innerHTML =
      "<p>Ошибка соединения</p>";
  }
}

function displayModules(data) {
  const modulesList = document.getElementById("modulesList");

  let modules = [];

  if (data.modules && Array.isArray(data.modules)) {
    modules = data.modules;
  } else if (Array.isArray(data)) {
    modules = data;
  } else if (data.course_modules && Array.isArray(data.course_modules)) {
    modules = data.course_modules;
  }

  console.log("Обработанные модули для отображения:", modules);

  if (!modules || modules.length === 0) {
    modulesList.innerHTML = "<p>Модули еще не добавлены</p>";
    return;
  }

  modulesList.innerHTML = modules
    .map(
      (module) => `
    <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
      <div>
        <strong>Модуль ${module.number}: ${module.name}</strong>
      </div>
      <div>ID: ${module.id}</div>
      <div>
        <button onclick="openModuleEditor(${module.id})">Редактировать</button>
        <button onclick="deleteModule(${module.id})">Удалить</button>
      </div>
    </div>
  `
    )
    .join("");
}

async function addModule(courseId, moduleData) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/courses/${courseId}/modules`,
      {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(moduleData),
      }
    );

    if (response.ok) {
      const result = await response.json();
      console.log("Модуль создан:", result);
      await loadModules(courseId);

      document.getElementById("addModuleForm").reset();
      alert("Модуль успешно добавлен!");

      return result;
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка создания модуля");
    }
  } catch (error) {
    throw error;
  }
}

async function deleteModule(moduleId) {
  if (
    !confirm(
      "Вы уверены, что хотите удалить этот модуль? Все шаги внутри модуля также будут удалены."
    )
  ) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/modules/${moduleId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      console.log("Модуль удален");
      await loadModules(getCourseIdFromURL());
      alert("Модуль успешно удален!");
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка удаления модуля");
    }
  } catch (error) {
    console.error("Ошибка удаления модуля:", error);
    alert(error.message);
  }
}

function openModuleEditor(moduleId) {
  window.location.href = `module-editor.html?course_id=${getCourseIdFromURL()}&module_id=${moduleId}`;
}

async function loadThemes() {
  try {
    console.log("Загружаем список тем...");

    const response = await fetch(`${API_BASE_URL}/themes`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const themeSelect = document.getElementById("courseTheme");

    console.log("Статус ответа тем:", response.status);

    if (response.ok) {
      const data = await response.json();
      console.log("Получены темы:", data);

      themeSelect.innerHTML = '<option value="">Выберите тему</option>';

      let themes = [];
      if (data.themes) {
        themes = data.themes;
      } else if (Array.isArray(data)) {
        themes = data;
      }

      console.log("Обработанные темы:", themes);

      if (themes.length === 0) {
        themeSelect.innerHTML = '<option value="">Темы не найдены</option>';
        console.warn("Темы не найдены в базе данных");
        return;
      }

      themes.forEach((theme) => {
        const option = document.createElement("option");
        option.value = theme.id;
        option.textContent = theme.name;
        themeSelect.appendChild(option);
      });

      console.log("Темы успешно загружены");
    } else {
      const errorText = await response.text();
      console.error("Ошибка загрузки тем:", errorText);
      themeSelect.innerHTML = '<option value="">Ошибка загрузки тем</option>';
    }
  } catch (error) {
    console.error("Ошибка загрузки тем:", error);
    themeSelect.innerHTML = '<option value="">Ошибка соединения</option>';
  }
}

async function createCourse(courseData) {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    console.log("Создаем курс:", courseData);

    const response = await fetch(`${API_BASE_URL}/courses`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        name: courseData.name,
        description: courseData.description,
        theme_id: courseData.theme_id,
        level: courseData.level,
        id_teacher: user.id,
      }),
    });

    console.log("Статус создания курса:", response.status);

    if (response.ok) {
      const result = await response.json();
      console.log("Курс создан:", result);
      alert("Курс успешно создан!");

      window.location.href = `course-editor.html?id=${result.id}`;
      return result;
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка создания курса");
    }
  } catch (error) {
    throw error;
  }
}

async function updateCourse(courseId, courseData) {
  try {
    console.log("Обновляем курс:", courseId, courseData);

    const response = await fetch(`${API_BASE_URL}/course/${courseId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        name: courseData.name,
        description: courseData.description,
        theme_id: courseData.theme_id,
        level: courseData.level,
      }),
    });

    console.log("Статус обновления курса:", response.status);
    console.log("Content-Type:", response.headers.get("content-type"));

    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error("Сервер вернул не JSON:", text.substring(0, 200));
      throw new Error(
        `Сервер вернул ошибку: ${response.status} ${response.statusText}`
      );
    }

    if (response.ok) {
      const result = await response.json();
      console.log("Курс обновлен:", result);
      alert("Курс успешно обновлен!");
      return result;
    } else {
      try {
        const errorData = await response.json();
        throw new Error(errorData.error || "Ошибка обновления курса");
      } catch (jsonError) {
        const errorText = await response.text();
        throw new Error(
          `Ошибка ${response.status}: ${errorText.substring(0, 100)}`
        );
      }
    }
  } catch (error) {
    throw error;
  }
}

function updateCounters() {
  const nameInput = document.getElementById("courseName");
  const descriptionInput = document.getElementById("courseDescription");
  const nameCounter = document.getElementById("nameCounter");
  const descriptionCounter = document.getElementById("descriptionCounter");

  nameCounter.textContent = `${nameInput.value.length}/20`;
  descriptionCounter.textContent = `${descriptionInput.value.length}/255`;
}

function initForm() {
  const form = document.getElementById("courseEditorForm");
  const courseId = getCourseIdFromURL();

  if (isEditMode()) {
    document.getElementById("pageTitle").textContent = "Редактирование курса";
    document.getElementById("submitButton").textContent = "Сохранить изменения";
    document.getElementById("backButton").href = "my-teaching-courses.html";

    loadCourseData(courseId);
  }

  document
    .getElementById("courseName")
    .addEventListener("input", updateCounters);
  document
    .getElementById("courseDescription")
    .addEventListener("input", updateCounters);

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const courseName = document.getElementById("courseName").value.trim();
    const courseDescription = document
      .getElementById("courseDescription")
      .value.trim();
    const courseTheme = document.getElementById("courseTheme").value;
    const courseLevel = document.getElementById("courseLevel").value;

    console.log("Данные формы:", {
      courseName,
      courseDescription,
      courseTheme,
      courseLevel,
    });

    if (!courseName) {
      alert("Введите название курса");
      return;
    }

    if (!courseTheme) {
      alert("Выберите тему курса");
      return;
    }

    if (courseName.length > 20) {
      alert("Название курса не должно превышать 20 символов");
      return;
    }

    if (courseDescription.length > 255) {
      alert("Описание курса не должно превышать 255 символов");
      return;
    }

    const courseData = {
      name: courseName,
      description: courseDescription,
      theme_id: parseInt(courseTheme),
      level: parseInt(courseLevel),
    };

    const submitBtn = document.getElementById("submitButton");
    const originalText = submitBtn.textContent;
    submitBtn.textContent = "Сохранение...";
    submitBtn.disabled = true;

    try {
      if (isEditMode()) {
        await updateCourse(courseId, courseData);
      } else {
        await createCourse(courseData);
      }
    } catch (error) {
      console.error("Ошибка сохранения курса:", error);
      alert(error.message);
    } finally {
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  });

  document
    .getElementById("addModuleForm")
    .addEventListener("submit", async function (e) {
      e.preventDefault();

      if (!isEditMode()) {
        alert("Сначала сохраните курс, чтобы добавлять модули");
        return;
      }

      const moduleName = document.getElementById("moduleName").value.trim();
      const moduleNumber = document.getElementById("moduleNumber").value;

      if (!moduleName) {
        alert("Введите название модуля");
        return;
      }

      const moduleData = {
        name: moduleName,
        number: parseInt(moduleNumber),
        course_id: parseInt(getCourseIdFromURL()),
      };

      try {
        await addModule(getCourseIdFromURL(), moduleData);
      } catch (error) {
        console.error("Ошибка добавления модуля:", error);
        alert(error.message);
      }
    });

  document
    .getElementById("cancelButton")
    .addEventListener("click", function () {
      if (isEditMode()) {
        window.location.href = "my-teaching-courses.html";
      } else {
        window.location.href = "teaching.html";
      }
    });
}

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

async function initCourseEditor() {
  checkAuth();
  await loadThemes();
  initForm();
  updateCounters();
}

document.addEventListener("DOMContentLoaded", initCourseEditor);
