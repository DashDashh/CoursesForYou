function checkAuth() {
  const user = localStorage.getItem("user");
  if (!user) {
    window.location.href = "login.html";
  }
}

function initTeaching() {
  checkAuth();
}

document.addEventListener("DOMContentLoaded", initTeaching);
