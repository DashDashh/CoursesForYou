// Получаем параметры из URL
const urlParams = new URLSearchParams(window.location.search);
const courseId = urlParams.get("course_id");
const moduleId = urlParams.get("module_id");
const currentStepId = urlParams.get("step_id");

let currentStepIndex = 0;
let steps = [];
let currentStepData = null;

// Базовый URL API
const API_BASE_URL = "https://127.0.0.1:5000/api";

// Функция для получения текущего пользователя
function getCurrentUser() {
  const userData = localStorage.getItem("user");
  return userData ? JSON.parse(userData) : null;
}

// Загрузка данных модуля
async function loadModuleData() {
  try {
    const response = await fetch(`${API_BASE_URL}/modules/${moduleId}`);
    if (!response.ok) throw new Error("Ошибка загрузки модуля");

    const module = await response.json();
    document.getElementById("moduleTitle").textContent =
      module.name || module.title;

    // Загружаем название курса
    const courseResponse = await fetch(`${API_BASE_URL}/course/${courseId}`);
    if (courseResponse.ok) {
      const course = await courseResponse.json();
      document.getElementById("courseName").textContent =
        course.name || course.title;
      document.getElementById(
        "backToCourse"
      ).href = `course.html?id=${courseId}`;
    }

    await loadSteps();
  } catch (error) {
    console.error("Ошибка загрузки модуля:", error);
    document.getElementById("moduleTitle").textContent =
      "Ошибка загрузки модуля";
  }
}

// Загрузка шагов модуля
async function loadSteps() {
  try {
    const response = await fetch(`${API_BASE_URL}/modules/${moduleId}/steps`);
    if (!response.ok) throw new Error("Ошибка загрузки шагов");

    const data = await response.json();
    steps = data.steps || data;

    if (steps.length === 0) {
      document.getElementById("stepsList").innerHTML =
        "<p>В модуле нет шагов</p>";
      return;
    }

    displayStepsNavigation();

    // Определяем текущий шаг
    let stepToLoad = 0;
    if (currentStepId) {
      stepToLoad = steps.findIndex((step) => step.id == currentStepId);
    }

    if (stepToLoad === -1) stepToLoad = 0;
    currentStepIndex = stepToLoad;

    await loadStepContent(currentStepIndex);
    updateNavigationButtons();
  } catch (error) {
    console.error("Ошибка загрузки шагов:", error);
    document.getElementById("stepsList").innerHTML =
      "<p>Ошибка загрузки шагов</p>";
  }
}

// Отображение навигации по шагам
function displayStepsNavigation() {
  const stepsList = document.getElementById("stepsList");
  stepsList.innerHTML = "";

  steps.forEach((step, index) => {
    const stepElement = document.createElement("div");
    stepElement.className = "step-nav-item";
    stepElement.innerHTML = `
            <button class="step-nav-btn" data-step-index="${index}" 
                    onclick="loadStepByIndex(${index})">
                Шаг ${step.number || index + 1}
                <span class="step-status" id="stepStatus${step.id}"></span>
            </button>
        `;
    stepsList.appendChild(stepElement);

    // Загружаем статус шага
    loadStepStatus(step.id);
  });
}

// Обновление отображения статуса шага
function updateStepStatusDisplay(stepId, status) {
  const statusElement = document.getElementById(`stepStatus${stepId}`);
  if (!statusElement) return;

  statusElement.className = "step-status";

  switch (status) {
    case "DONE":
      statusElement.classList.add("status-completed");
      statusElement.textContent = " ✓";
      break;
    case "UNCORRECT":
      statusElement.classList.add("status-wrong");
      statusElement.textContent = " ✗";
      break;
    case "NOT_BEGIN":
    default:
      statusElement.classList.add("status-not-started");
      statusElement.textContent = " ○";
  }
}

async function loadStepContent(stepIndex) {
  if (stepIndex < 0 || stepIndex >= steps.length) return;

  const step = steps[stepIndex];
  currentStepData = step;

  document.getElementById("stepTitle").textContent = `Шаг ${
    step.number || stepIndex + 1
  }`;

  try {
    // Загружаем полные данные шага
    const stepResponse = await fetch(`${API_BASE_URL}/steps/${step.id}`);
    if (!stepResponse.ok) throw new Error("Ошибка загрузки данных шага");

    const stepData = await stepResponse.json();
    console.log("Step data:", stepData); // Для отладки

    // Определяем тип шага (step_type может быть числом или строкой)
    let stepType = stepData.step_type;
    console.log("Raw step type:", stepType, "Type:", typeof stepType);

    // Обрабатываем разные форматы step_type
    if (typeof stepType === "number") {
      // Если step_type - число, то 1 = TASK, 2 = THEORY (или наоборот)
      // Проверяем по наличию данных в объекте
      if (stepData.theory) {
        stepType = "theory";
      } else if (stepData.task) {
        stepType = "task";
      } else {
        // Если нет явных данных, используем эвристику
        stepType = stepType === 1 ? "task" : "theory";
      }
    } else if (typeof stepType === "string") {
      if (stepType.includes(".")) {
        stepType = stepType.split(".").pop().toLowerCase();
      } else {
        stepType = stepType.toLowerCase();
      }
    }

    console.log("Processed step type:", stepType);

    // Загружаем содержимое в зависимости от типа шага
    if (stepType === "theory") {
      await loadTheoryContent(step.id);
    } else if (stepType === "task") {
      await loadTaskContent(step.id);
    } else {
      document.getElementById(
        "stepBody"
      ).innerHTML = `<p>Неизвестный тип шага: ${stepData.step_type}</p>`;
    }

    // Обновляем статус текущего шага
    await loadStepStatus(step.id);
  } catch (error) {
    console.error("Ошибка загрузки содержимого шага:", error);
    document.getElementById("stepBody").innerHTML =
      "<p>Ошибка загрузки содержимого шага</p>";
  }
}

// Загрузка статуса шага
async function loadStepStatus(stepId) {
  try {
    const user = getCurrentUser();
    if (!user) {
      // Если пользователь не авторизован, показываем все шаги как не начатые
      updateStepStatusDisplay(stepId, "NOT_BEGIN");
      return;
    }

    // Получаем прогресс модуля и находим статус нужного шага
    const response = await fetch(
      `${API_BASE_URL}/user_progress/user/${user.id}/module/${moduleId}`
    );
    if (response.ok) {
      const moduleProgress = await response.json();
      console.log("Module progress:", moduleProgress); // Для отладки

      const stepProgress = moduleProgress.steps.find(
        (step) => step.step_id === stepId
      );

      if (stepProgress) {
        updateStepStatusDisplay(stepId, stepProgress.status);
      } else {
        updateStepStatusDisplay(stepId, "NOT_BEGIN");
      }
    } else {
      // Если ошибка, показываем как не начатый
      updateStepStatusDisplay(stepId, "NOT_BEGIN");
    }
  } catch (error) {
    console.error("Ошибка загрузки статуса шага:", error);
    updateStepStatusDisplay(stepId, "NOT_BEGIN");
  }
}

async function loadTheoryContent(stepId) {
  try {
    const response = await fetch(`${API_BASE_URL}/steps/${stepId}/theory`);
    if (!response.ok) throw new Error("Ошибка загрузки теории");

    const theory = await response.json();
    document.getElementById("stepBody").innerHTML = `
            <div class="theory-content">
                ${theory.text || theory.content}
            </div>
        `;

    // Кнопка для отметки прочтения
    const actions = document.getElementById("stepActions");
    actions.innerHTML = `
            <button onclick="markTheoryAsRead(${stepId})">Отметить как прочитанное</button>
        `;
  } catch (error) {
    console.error("Ошибка загрузки теории:", error);
    document.getElementById("stepBody").innerHTML =
      "<p>Ошибка загрузки теоретического материала</p>";
  }
}

async function loadTaskContent(stepId) {
  try {
    const response = await fetch(`${API_BASE_URL}/steps/${stepId}/task`);
    if (!response.ok) throw new Error("Ошибка загрузки задания");

    const task = await response.json();
    document.getElementById("stepBody").innerHTML = `
            <div class="task-content">
                <h4>Задание:</h4>
                <p>${task.question || task.content}</p>
                <div class="answer-input">
                    <input type="text" id="answerInput" placeholder="Введите ваш ответ">
                    <button onclick="checkAnswer(${stepId}, '${
      task.answer
    }')">Проверить</button>
                </div>
                <div id="answerResult"></div>
            </div>
        `;

    document.getElementById("stepActions").innerHTML = "";
  } catch (error) {
    console.error("Ошибка загрузки задания:", error);
    document.getElementById("stepBody").innerHTML =
      "<p>Ошибка загрузки задания</p>";
  }
}

// Проверка ответа
async function checkAnswer(stepId, correctAnswer) {
  const answerInput = document.getElementById("answerInput");
  const userAnswer = answerInput.value.trim();
  const resultDiv = document.getElementById("answerResult");

  if (!userAnswer) {
    resultDiv.innerHTML = '<p style="color: orange;">Введите ответ</p>';
    return;
  }

  try {
    const user = getCurrentUser();
    if (!user) {
      alert("Для выполнения задания необходимо войти в систему");
      return;
    }

    // Простая проверка ответа на фронтенде
    const isCorrect = userAnswer.toLowerCase() === correctAnswer.toLowerCase();

    if (isCorrect) {
      resultDiv.innerHTML = '<p style="color: green;">✓ Правильно!</p>';
      await updateStepProgress(stepId, "DONE");
    } else {
      resultDiv.innerHTML =
        '<p style="color: red;">✗ Неправильно. Попробуйте еще раз.</p>';
      await updateStepProgress(stepId, "UNCORRECT");
    }

    // Обновляем статус шага
    await loadStepStatus(stepId);
  } catch (error) {
    console.error("Ошибка проверки ответа:", error);
    resultDiv.innerHTML = '<p style="color: red;">Ошибка проверки ответа</p>';
  }
}

// Отметить теорию как прочитанную
async function markTheoryAsRead(stepId) {
  try {
    const user = getCurrentUser();
    if (!user) {
      alert("Для отметки прочтения необходимо войти в систему");
      return;
    }

    await updateStepProgress(stepId, "DONE");
    await loadStepStatus(stepId);

    document.getElementById("stepActions").innerHTML =
      '<p style="color: green;">✓ Теория отмечена как прочитанная</p>';
  } catch (error) {
    console.error("Ошибка отметки теории:", error);
    alert("Ошибка при отметке теории");
  }
}

// Обновление прогресса шага
async function updateStepProgress(stepId, status) {
  try {
    const user = getCurrentUser();
    if (!user) return;

    const response = await fetch(
      `${API_BASE_URL}/user_progress/user/${user.id}/step/${stepId}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          status: status,
        }),
      }
    );

    if (!response.ok) {
      console.error("Ошибка обновления прогресса");
    }
  } catch (error) {
    console.error("Ошибка обновления прогресса:", error);
  }
}

// Навигация
function loadStepByIndex(index) {
  currentStepIndex = index;
  loadStepContent(currentStepIndex);
  updateNavigationButtons();
  updateURL();
}

function goToPreviousStep() {
  if (currentStepIndex > 0) {
    currentStepIndex--;
    loadStepContent(currentStepIndex);
    updateNavigationButtons();
    updateURL();
  }
}

function goToNextStep() {
  if (currentStepIndex < steps.length - 1) {
    currentStepIndex++;
    loadStepContent(currentStepIndex);
    updateNavigationButtons();
    updateURL();
  }
}

function updateNavigationButtons() {
  document.getElementById("prevStep").disabled = currentStepIndex === 0;
  document.getElementById("nextStep").disabled =
    currentStepIndex === steps.length - 1;
}

function updateURL() {
  const newUrl = `module.html?course_id=${courseId}&module_id=${moduleId}&step_id=${steps[currentStepIndex].id}`;
  window.history.replaceState({}, "", newUrl);
}

// Инициализация
document.addEventListener("DOMContentLoaded", () => {
  if (!courseId || !moduleId) {
    alert("Курс или модуль не найден");
    window.location.href = "my-courses.html";
    return;
  }

  // Назначаем обработчики кнопок навигации
  document
    .getElementById("prevStep")
    .addEventListener("click", goToPreviousStep);
  document.getElementById("nextStep").addEventListener("click", goToNextStep);

  loadModuleData();
});
