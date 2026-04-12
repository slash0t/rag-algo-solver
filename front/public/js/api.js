const api = (() => {
  const TOKEN_KEY = "rag_token";
  const USERNAME_KEY = "rag_username";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }

  function setUsername(username) {
    localStorage.setItem(USERNAME_KEY, username);
  }

  function getUsername() {
    return localStorage.getItem(USERNAME_KEY);
  }

  function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USERNAME_KEY);
  }

  function isAuthenticated() {
    return !!getToken();
  }

  async function request(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const opts = { method, headers };
    if (body) {
      opts.body = JSON.stringify(body);
    }

    const res = await fetch(path, opts);

    if (res.status === 401) {
      clearAuth();
      window.location.reload();
      throw new Error("Сессия истекла");
    }

    if (res.status === 204) {
      return null;
    }

    const data = await res.json();

    if (!res.ok) {
      const msg =
        data.detail && typeof data.detail === "string"
          ? data.detail
          : "Ошибка запроса";
      throw new Error(msg);
    }

    return data;
  }

  async function login(username, password) {
    const data = await request("POST", "/api/auth/login", {
      username,
      password,
    });
    setToken(data.access_token);
    setUsername(username);
    return data;
  }

  async function register(username, password) {
    return request("POST", "/api/auth/register", { username, password });
  }

  async function createQuery(text) {
    return request("POST", "/api/queries", { text });
  }

  async function getQueries(page = 1, size = 15) {
    return request("GET", `/api/queries?page=${page}&size=${size}`);
  }

  async function getQuery(id) {
    return request("GET", `/api/queries/${id}`);
  }

  async function getSimilarTasks(queryId) {
    return request("GET", `/api/queries/${queryId}/similar-tasks`);
  }

  return {
    getToken,
    getUsername,
    clearAuth,
    isAuthenticated,
    login,
    register,
    createQuery,
    getQueries,
    getQuery,
    getSimilarTasks,
  };
})();
