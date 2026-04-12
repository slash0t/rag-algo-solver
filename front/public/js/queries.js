let currentPage = 1;
let currentQueryId = null;
let pollingTimer = null;

function initQueries() {
  loadHistory();
  showState("empty");
}

// --- State management ---

function showState(state) {
  ["empty", "create", "processing", "result"].forEach((s) => {
    const el = document.getElementById(`state-${s}`);
    if (el) el.classList.toggle("hidden", s !== state);
  });
}

// --- History ---

async function loadHistory(page) {
  if (page !== undefined) currentPage = page;

  const container = document.getElementById("query-history");
  const pagination = document.getElementById("pagination");

  try {
    const data = await api.getQueries(currentPage);
    const items = data.items || [];

    if (items.length === 0) {
      container.innerHTML =
        '<div class="query-list-empty">Запросов пока нет</div>';
      pagination.innerHTML = "";
      return;
    }

    container.innerHTML = items.map((q) => queryItemHTML(q)).join("");

    container.querySelectorAll(".query-item").forEach((el) => {
      el.addEventListener("click", () => selectQuery(el.dataset.id));
    });

    // Pagination
    const totalPages = Math.ceil(data.total / data.size);
    if (totalPages > 1) {
      let html = "";
      for (let i = 1; i <= totalPages; i++) {
        html += `<button class="${i === currentPage ? "active" : ""}" onclick="loadHistory(${i})">${i}</button>`;
      }
      pagination.innerHTML = html;
    } else {
      pagination.innerHTML = "";
    }
  } catch {
    container.innerHTML =
      '<div class="query-list-empty">Ошибка загрузки</div>';
  }
}

function queryItemHTML(q) {
  const status = getQueryStatus(q);
  const date = new Date(q.created_at).toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
  const active = q.id === currentQueryId ? " active" : "";
  const text = escapeHTML(q.text || "").substring(0, 100);

  return `
    <div class="query-item${active}" data-id="${q.id}">
      <div class="query-item-text">${text}</div>
      <div class="query-item-meta">
        <span class="query-status ${status}"></span>
        <span>${date}</span>
      </div>
    </div>`;
}

function getQueryStatus(q) {
  if (q.response_text) return "completed";
  if (q.responded_at) return "completed";
  return "processing";
}

// --- Select query ---

async function selectQuery(id) {
  currentQueryId = id;
  stopPolling();

  // Update active in sidebar
  document.querySelectorAll(".query-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === id);
  });

  try {
    const query = await api.getQuery(id);

    if (query.response_text) {
      showResult(query);
    } else {
      showProcessing(query);
      startPolling(id);
    }
  } catch (err) {
    showState("empty");
  }
}

function showProcessing(query) {
  document.getElementById("processing-text").textContent = query.text;
  showState("processing");
}

async function showResult(query) {
  document.getElementById("result-query-text").textContent = query.text;
  document.getElementById("result-response-text").textContent =
    query.response_text || "Ответ пока не получен";

  const createdAt = new Date(query.created_at).toLocaleString("ru-RU");
  document.getElementById("result-created").textContent =
    `Создан: ${createdAt}`;

  if (query.responded_at) {
    const respondedAt = new Date(query.responded_at).toLocaleString("ru-RU");
    document.getElementById("result-responded").textContent =
      `Ответ: ${respondedAt}`;
  } else {
    document.getElementById("result-responded").textContent = "";
  }

  // Load similar tasks
  try {
    const tasks = await api.getSimilarTasks(query.id);
    const section = document.getElementById("similar-tasks-section");
    const list = document.getElementById("similar-tasks-list");

    if (tasks && tasks.length > 0) {
      list.innerHTML = tasks
        .map(
          (t) => `
        <div class="similar-task-item">
          <span class="task-title">${escapeHTML(t.title)}</span>
          <span class="task-links">
            ${t.task_url ? `<a href="${escapeHTML(t.task_url)}" target="_blank">Задача</a>` : ""}
            ${t.solution_url ? `<a href="${escapeHTML(t.solution_url)}" target="_blank">Решение</a>` : ""}
          </span>
        </div>`,
        )
        .join("");
      section.classList.remove("hidden");
    } else {
      section.classList.add("hidden");
    }
  } catch {
    document.getElementById("similar-tasks-section").classList.add("hidden");
  }

  showState("result");
}

// --- Polling ---

function startPolling(id) {
  pollingTimer = setInterval(async () => {
    try {
      const query = await api.getQuery(id);
      if (query.response_text) {
        stopPolling();
        showResult(query);
        loadHistory();
      }
    } catch {
      stopPolling();
    }
  }, 3000);
}

function stopPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }
}

// --- New query ---

document.getElementById("new-query-btn").addEventListener("click", () => {
  currentQueryId = null;
  stopPolling();
  document.querySelectorAll(".query-item").forEach((el) => {
    el.classList.remove("active");
  });
  document.getElementById("query-text").value = "";
  document.getElementById("query-create-error").textContent = "";
  showState("create");
});

document.getElementById("query-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errorEl = document.getElementById("query-create-error");
  errorEl.textContent = "";

  const text = document.getElementById("query-text").value.trim();
  if (!text) return;

  try {
    const result = await api.createQuery(text);
    currentQueryId = result.id;
    await loadHistory();
    showProcessing(result);
    startPolling(result.id);
  } catch (err) {
    errorEl.textContent = err.message;
  }
});

// --- Utils ---

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
