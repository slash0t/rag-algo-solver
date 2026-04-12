(() => {
  const authPage = document.getElementById("auth-page");
  const appPage = document.getElementById("app-page");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const showRegisterLink = document.getElementById("show-register");
  const showLoginLink = document.getElementById("show-login");
  const loginError = document.getElementById("login-error");
  const registerError = document.getElementById("register-error");
  const logoutBtn = document.getElementById("logout-btn");
  const usernameDisplay = document.getElementById("username-display");

  function showAuth() {
    authPage.classList.remove("hidden");
    appPage.classList.add("hidden");
  }

  function showApp() {
    authPage.classList.add("hidden");
    appPage.classList.remove("hidden");
    usernameDisplay.textContent = api.getUsername() || "";
  }

  // Init
  if (api.isAuthenticated()) {
    showApp();
    if (typeof initQueries === "function") initQueries();
  } else {
    showAuth();
  }

  // Toggle forms
  showRegisterLink.addEventListener("click", (e) => {
    e.preventDefault();
    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
    loginError.textContent = "";
  });

  showLoginLink.addEventListener("click", (e) => {
    e.preventDefault();
    registerForm.classList.add("hidden");
    loginForm.classList.remove("hidden");
    registerError.textContent = "";
  });

  // Login
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    loginError.textContent = "";
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;

    try {
      await api.login(username, password);
      showApp();
      if (typeof initQueries === "function") initQueries();
    } catch (err) {
      loginError.textContent = err.message;
    }
  });

  // Register
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    registerError.textContent = "";
    const username = document.getElementById("reg-username").value.trim();
    const password = document.getElementById("reg-password").value;
    const confirm = document.getElementById("reg-password-confirm").value;

    if (password !== confirm) {
      registerError.textContent = "Пароли не совпадают";
      return;
    }

    try {
      await api.register(username, password);
      await api.login(username, password);
      showApp();
      if (typeof initQueries === "function") initQueries();
    } catch (err) {
      registerError.textContent = err.message;
    }
  });

  // Logout
  logoutBtn.addEventListener("click", () => {
    api.clearAuth();
    showAuth();
  });
})();
