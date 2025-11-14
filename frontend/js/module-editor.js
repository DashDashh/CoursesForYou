const API_BASE_URL = "http://localhost:5000/api";

function getAuthHeaders() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${user.id || ""}`,
  };
}

function getModuleIdFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("module_id");
}

function getCourseIdFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("course_id");
}

async function loadModuleData(moduleId) {
  try {
    console.log("Загружаем данные модуля ID:", moduleId);

    const response = await fetch(`${API_BASE_URL}/modules/${moduleId}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const moduleData = await response.json();
      console.log("Данные модуля:", moduleData);

      document.getElementById(
        "moduleNameTitle"
      ).textContent = `Модуль ${moduleData.number}: ${moduleData.name}`;

      await loadSteps(moduleId);
    } else {
      console.error("Ошибка загрузки данных модуля");
      alert("Ошибка загрузки данных модуля");
    }
  } catch (error) {
    console.error("Ошибка загрузки модуля:", error);
    alert("Ошибка соединения с сервером");
  }
}

async function loadSteps(moduleId) {
  try {
    console.log("Загружаем шаги для модуля:", moduleId);

    const response = await fetch(`${API_BASE_URL}/modules/${moduleId}/steps`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const data = await response.json();
      console.log("Получены данные шагов:", data);
      displaySteps(data);
    } else {
      console.error("Ошибка загрузки шагов");
      document.getElementById("stepsList").innerHTML =
        "<p>Ошибка загрузки шагов</p>";
    }
  } catch (error) {
    console.error("Ошибка загрузки шагов:", error);
    document.getElementById("stepsList").innerHTML = "<p>Ошибка соединения</p>";
  }
}

function displaySteps(data) {
  const stepsList = document.getElementById("stepsList");

  let steps = [];

  if (data.steps && Array.isArray(data.steps)) {
    steps = data.steps;
  } else if (Array.isArray(data)) {
    steps = data;
  } else if (data.module_steps && Array.isArray(data.module_steps)) {
    steps = data.module_steps;
  }

  console.log("Обработанные шаги для отображения:", steps);

  if (!steps || steps.length === 0) {
    stepsList.innerHTML = "<p>Шаги еще не добавлены</p>";
    return;
  }

  stepsList.innerHTML = steps
    .map((step) => {
      let stepType, content;

      if (step.step_type === "theory" || step.step_type === 1) {
        stepType = "theory";
        content =
          step.theory_text ||
          step.text ||
          step.theory?.text ||
          "Текст теории не указан";
      } else if (step.step_type === "task" || step.step_type === 2) {
        stepType = "task";
        content =
          step.task_question ||
          step.question ||
          step.task?.question ||
          "Вопрос не указан";
      } else {
        stepType = "unknown";
        content = "Содержание не указано";
      }

      if (content.length > 150) {
        content = content.substring(0, 150) + "...";
      }

      const stepTypeDisplay = stepType === "theory" ? "Теория" : "Задание";

      return `
          <div style="border: 1px solid #ccc; padding: 15px; margin: 10px 0; background: #f9f9f9;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <div style="flex-grow: 1;">
                <div style="font-weight: bold; margin-bottom: 8px;">
                  Шаг ${step.number}: ${stepTypeDisplay}
                </div>
                <div style="color: #666; font-size: 14px; line-height: 1.4; white-space: pre-wrap;">
                  ${content}
                </div>
              </div>
              <div>
                <button onclick="openEditStepModal(${step.id}, '${stepType}')">Редактировать</button>
              </div>
            </div>
          </div>
        `;
    })
    .join("");
}

function toggleStepFields() {
  const stepType = document.getElementById("stepType").value;
  const theoryFields = document.getElementById("theoryFields");
  const taskFields = document.getElementById("taskFields");

  theoryFields.style.display = "none";
  taskFields.style.display = "none";

  if (stepType === "theory") {
    theoryFields.style.display = "block";
  } else if (stepType === "task") {
    taskFields.style.display = "block";
  }
}

async function addStep(moduleId, stepData) {
  try {
    const response = await fetch(`${API_BASE_URL}/modules/${moduleId}/steps`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(stepData),
    });

    if (response.ok) {
      const result = await response.json();
      console.log("Шаг создан:", result);
      await loadSteps(moduleId);

      document.getElementById("addStepForm").reset();
      document.getElementById("theoryFields").style.display = "none";
      document.getElementById("taskFields").style.display = "none";

      alert("Шаг успешно добавлен!");

      return result;
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка создания шага");
    }
  } catch (error) {
    throw error;
  }
}

async function openEditStepModal(stepId, stepType) {
  try {
    const response = await fetch(`${API_BASE_URL}/steps/${stepId}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      const stepData = await response.json();
      console.log("Данные шага для редактирования:", stepData);

      document.getElementById("editStepId").value = stepId;
      document.getElementById("editStepNumber").value = stepData.number;

      document.getElementById("editTheoryFields").style.display = "none";
      document.getElementById("editTaskFields").style.display = "none";

      if (stepType === "theory") {
        document.getElementById("editTheoryFields").style.display = "block";
        const theoryText =
          stepData.theory_text || stepData.text || stepData.theory?.text || "";
        document.getElementById("editTheoryText").value = theoryText;
      } else if (stepType === "task") {
        document.getElementById("editTaskFields").style.display = "block";
        const taskQuestion =
          stepData.task_question ||
          stepData.question ||
          stepData.task?.question ||
          "";
        const correctAnswer =
          stepData.correct_answer ||
          stepData.answer ||
          stepData.task?.answer ||
          "";
        document.getElementById("editTaskQuestion").value = taskQuestion;
        document.getElementById("editCorrectAnswer").value = correctAnswer;
      }

      document.getElementById("editStepForm").dataset.stepType = stepType;

      document.getElementById("editStepModal").style.display = "block";
    } else {
      throw new Error("Ошибка загрузки данных шага");
    }
  } catch (error) {
    console.error("Ошибка открытия редактора шага:", error);
    alert("Ошибка загрузки данных шага");
  }
}

function closeEditStepModal() {
  document.getElementById("editStepModal").style.display = "none";
}

async function updateTheoryContent(stepId, theoryText) {
  try {
    const response = await fetch(`${API_BASE_URL}/theory/${stepId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        text: theoryText,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка обновления теории");
    }

    console.log("Теория успешно обновлена");
    return await response.json();
  } catch (error) {
    console.error("Ошибка обновления теории:", error);
    throw error;
  }
}

async function updateTaskContent(stepId, question, answer) {
  try {
    const response = await fetch(`${API_BASE_URL}/task/${stepId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        question: question,
        answer: answer,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка обновления задания");
    }

    console.log("Задание успешно обновлено");
    return await response.json();
  } catch (error) {
    console.error("Ошибка обновления задания:", error);
    throw error;
  }
}

async function saveStepChanges(stepId, stepData) {
  try {
    const stepType = document.getElementById("editStepForm").dataset.stepType;

    console.log("Сохранение изменений шага:", { stepId, stepType, stepData });

    const stepResponse = await fetch(`${API_BASE_URL}/steps/${stepId}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        number: stepData.number,
      }),
    });

    if (!stepResponse.ok) {
      const errorData = await stepResponse.json();
      throw new Error(errorData.error || "Ошибка обновления шага");
    }

    if (stepType === "theory") {
      await updateTheoryContent(stepId, stepData.theory_text);
    } else if (stepType === "task") {
      await updateTaskContent(
        stepId,
        stepData.task_question,
        stepData.correct_answer
      );
    }

    await loadSteps(getModuleIdFromURL());
    closeEditStepModal();
    alert("Изменения сохранены!");
  } catch (error) {
    console.error("Ошибка сохранения шага:", error);
    alert(error.message);
  }
}

async function deleteStep(stepId) {
  if (!confirm("Вы уверены, что хотите удалить этот шаг?")) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/steps/${stepId}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (response.ok) {
      console.log("Шаг удален");
      await loadSteps(getModuleIdFromURL());
      closeEditStepModal();
      alert("Шаг успешно удален!");
    } else {
      const errorData = await response.json();
      throw new Error(errorData.error || "Ошибка удаления шага");
    }
  } catch (error) {
    console.error("Ошибка удаления шага:", error);
    alert(error.message);
  }
}

function goBackToCourse() {
  const courseId = getCourseIdFromURL();
  window.location.href = `course-editor.html?id=${courseId}`;
}

function initForm() {
  const moduleId = getModuleIdFromURL();
  const courseId = getCourseIdFromURL();

  if (!moduleId || !courseId) {
    alert("Неверные параметры URL");
    window.location.href = "teaching.html";
    return;
  }

  loadModuleData(moduleId);

  document
    .getElementById("stepType")
    .addEventListener("change", toggleStepFields);

  document
    .getElementById("addStepForm")
    .addEventListener("submit", async function (e) {
      e.preventDefault();

      const stepType = document.getElementById("stepType").value;
      const stepNumber = document.getElementById("stepNumber").value;

      if (!stepType) {
        alert("Выберите тип шага");
        return;
      }

      const stepData = {
        step_type: stepType,
        number: parseInt(stepNumber),
        module_id: parseInt(moduleId),
      };

      if (stepType === "theory") {
        const theoryText = document.getElementById("theoryText").value.trim();
        if (!theoryText) {
          alert("Введите текст теории");
          return;
        }
        stepData.theory_text = theoryText;
      } else if (stepType === "task") {
        const taskQuestion = document
          .getElementById("taskQuestion")
          .value.trim();
        const correctAnswer = document
          .getElementById("correctAnswer")
          .value.trim();

        if (!taskQuestion) {
          alert("Введите вопрос задания");
          return;
        }
        if (!correctAnswer) {
          alert("Введите правильный ответ");
          return;
        }

        stepData.task_question = taskQuestion;
        stepData.correct_answer = correctAnswer;
      }

      const submitBtn = document.getElementById("submitStepButton");
      const originalText = submitBtn.textContent;
      submitBtn.textContent = "Создание...";
      submitBtn.disabled = true;

      try {
        await addStep(moduleId, stepData);
      } catch (error) {
        console.error("Ошибка добавления шага:", error);
        alert(error.message);
      } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
      }
    });

  document
    .getElementById("editStepForm")
    .addEventListener("submit", async function (e) {
      e.preventDefault();

      const stepId = document.getElementById("editStepId").value;
      const stepNumber = document.getElementById("editStepNumber").value;
      const stepType = document.getElementById("editStepForm").dataset.stepType;

      const stepData = {
        number: parseInt(stepNumber),
      };

      if (stepType === "theory") {
        const theoryText = document
          .getElementById("editTheoryText")
          .value.trim();
        if (!theoryText) {
          alert("Введите текст теории");
          return;
        }
        stepData.theory_text = theoryText;
      } else if (stepType === "task") {
        const taskQuestion = document
          .getElementById("editTaskQuestion")
          .value.trim();
        const correctAnswer = document
          .getElementById("editCorrectAnswer")
          .value.trim();

        if (!taskQuestion) {
          alert("Введите вопрос задания");
          return;
        }
        if (!correctAnswer) {
          alert("Введите правильный ответ");
          return;
        }

        stepData.task_question = taskQuestion;
        stepData.correct_answer = correctAnswer;
      }

      try {
        await saveStepChanges(stepId, stepData);
      } catch (error) {
        console.error("Ошибка сохранения изменений:", error);
        alert(error.message);
      }
    });

  document
    .getElementById("cancelEditButton")
    .addEventListener("click", closeEditStepModal);

  document
    .getElementById("deleteStepButton")
    .addEventListener("click", function () {
      const stepId = document.getElementById("editStepId").value;
      deleteStep(stepId);
    });

  document
    .getElementById("backButton")
    .addEventListener("click", goBackToCourse);

  document
    .getElementById("editStepModal")
    .addEventListener("click", function (e) {
      if (e.target === this) {
        closeEditStepModal();
      }
    });
}

function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

async function initModuleEditor() {
  checkAuth();
  initForm();
}

document.addEventListener("DOMContentLoaded", initModuleEditor);
