// Change this if your backend runs somewhere other than localhost:8000
const API_BASE = "http://localhost:8000";

const state = {
  token: localStorage.getItem("token") || null,
  user: null, // { id, email, is_admin } once fetched from /me
  books: [],
};

// ---------- DOM refs ----------
const authArea = document.getElementById("auth-area");
const authPanel = document.getElementById("auth-panel");
const errorBanner = document.getElementById("error-banner");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const tabButtons = document.querySelectorAll(".tab-btn");
const bookList = document.getElementById("book-list");
const searchInput = document.getElementById("search-input");
const addBookToggle = document.getElementById("add-book-toggle");
const addBookPanel = document.getElementById("add-book-panel");
const addBookForm = document.getElementById("add-book-form");
const addBookCancel = document.getElementById("add-book-cancel");
const editModal = document.getElementById("edit-modal");
const editBookForm = document.getElementById("edit-book-form");
const editBookCancel = document.getElementById("edit-book-cancel");

// ---------- API helper ----------
// Wraps fetch: adds the Authorization header when we have a token,
// parses JSON, and throws a readable Error on failure so callers
// can show error.message in the UI.
async function apiFetch(path, { method = "GET", body, form = false } = {}) {
  const headers = {};
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;

  let payload = body;
  if (body && !form) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${path}`, { method, headers, body: payload });

  if (res.status === 204) return null;

  let data = null;
  try {
    data = await res.json();
  } catch {
    // no JSON body, that's fine for some responses
  }

  if (!res.ok) {
    if (res.status === 401) logout();
    const message = (data && data.detail) || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
}

function clearError() {
  errorBanner.hidden = true;
  errorBanner.textContent = "";
}

// ---------- Auth ----------
function setToken(token) {
  state.token = token;
  if (token) localStorage.setItem("token", token);
  else localStorage.removeItem("token");
}

async function loadCurrentUser() {
  if (!state.token) {
    state.user = null;
    return;
  }
  try {
    state.user = await apiFetch("/me");
  } catch {
    state.user = null;
    setToken(null);
  }
}

function logout() {
  setToken(null);
  state.user = null;
  render();
}

async function login(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);

  const res = await fetch(`${API_BASE}/token`, { method: "POST", body: form });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error((data && data.detail) || "Could not log in");

  setToken(data.access_token);
  await loadCurrentUser();
}

async function register(email, password) {
  await apiFetch("/register", { method: "POST", body: { email, password } });
}

// ---------- Books ----------
async function loadBooks() {
  state.books = await apiFetch("/books");
}

async function addBook({ title, author, isbn }) {
  await apiFetch("/books", { method: "POST", body: { title, author, isbn } });
}

async function updateBook(id, { title, author, isbn }) {
  await apiFetch(`/books/${id}`, { method: "PUT", body: { title, author, isbn } });
}

async function deleteBook(id) {
  await apiFetch(`/books/${id}`, { method: "DELETE" });
}

async function checkoutBook(id) {
  await apiFetch(`/books/${id}/checkout`, { method: "POST" });
}

async function returnBook(id) {
  await apiFetch(`/books/${id}/return`, { method: "POST" });
}

// ---------- Rendering ----------
function renderAuthArea() {
  if (state.user) {
    authArea.innerHTML = `
      <span class="who">Signed in as <strong>${escapeHtml(state.user.email)}</strong></span>
      ${state.user.is_admin ? '<span class="admin-badge">Admin</span>' : ""}
      <button class="link-btn" id="logout-btn">Log out</button>
    `;
    document.getElementById("logout-btn").addEventListener("click", logout);
    authPanel.hidden = true;
  } else {
    authArea.innerHTML = `<button class="secondary" id="show-auth-btn">Log in / Register</button>`;
    document.getElementById("show-auth-btn").addEventListener("click", () => {
      authPanel.hidden = !authPanel.hidden;
    });
  }
  addBookToggle.hidden = !state.user?.is_admin;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderBooks() {
  const query = searchInput.value.trim().toLowerCase();
  const visible = state.books.filter(
    (b) => b.title.toLowerCase().includes(query) || b.author.toLowerCase().includes(query)
  );

  if (visible.length === 0) {
    bookList.innerHTML = `<p class="empty-state">No books match "${escapeHtml(query)}".</p>`;
    return;
  }

  bookList.innerHTML = visible
    .map((book) => {
      const statusClass = book.is_available ? "available" : "checked-out";
      const statusLabel = book.is_available ? "Available" : "Checked out";

      const actions = [];
      if (state.user) {
        actions.push(
          book.is_available
            ? `<button data-action="checkout" data-id="${book.id}">Check out</button>`
            : `<button data-action="return" data-id="${book.id}">Return</button>`
        );
      }
      if (state.user?.is_admin) {
        actions.push(`<button class="secondary" data-action="edit" data-id="${book.id}">Edit</button>`);
        actions.push(`<button class="danger" data-action="delete" data-id="${book.id}">Delete</button>`);
      }

      return `
        <div class="book-row">
          <div class="book-info">
            <h3>${escapeHtml(book.title)}</h3>
            <p class="byline">${escapeHtml(book.author)} · ISBN ${escapeHtml(book.isbn)}</p>
            <span class="status ${statusClass}">${statusLabel}</span>
          </div>
          <div class="book-actions">${actions.join("")}</div>
        </div>
      `;
    })
    .join("");
}

function render() {
  renderAuthArea();
  renderBooks();
}

// ---------- Event wiring ----------
tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("is-active"));
    btn.classList.add("is-active");
    const isLogin = btn.dataset.tab === "login";
    loginForm.hidden = !isLogin;
    registerForm.hidden = isLogin;
  });
});

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  const form = new FormData(loginForm);
  try {
    await login(form.get("email"), form.get("password"));
    authPanel.hidden = true;
    loginForm.reset();
    render();
  } catch (err) {
    showError(err.message);
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  const form = new FormData(registerForm);
  try {
    await register(form.get("email"), form.get("password"));
    registerForm.reset();
    // Log the user straight in after registering
    await login(form.get("email"), form.get("password"));
    authPanel.hidden = true;
    render();
  } catch (err) {
    showError(err.message);
  }
});

searchInput.addEventListener("input", renderBooks);

addBookToggle.addEventListener("click", () => {
  addBookPanel.hidden = !addBookPanel.hidden;
});
addBookCancel.addEventListener("click", () => {
  addBookPanel.hidden = true;
  addBookForm.reset();
});

addBookForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  const form = new FormData(addBookForm);
  try {
    await addBook({ title: form.get("title"), author: form.get("author"), isbn: form.get("isbn") });
    addBookForm.reset();
    addBookPanel.hidden = true;
    await refreshBooks();
  } catch (err) {
    showError(err.message);
  }
});

editBookCancel.addEventListener("click", () => {
  editModal.hidden = true;
});

editBookForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  const form = new FormData(editBookForm);
  const id = form.get("id");
  try {
    await updateBook(id, { title: form.get("title"), author: form.get("author"), isbn: form.get("isbn") });
    editModal.hidden = true;
    await refreshBooks();
  } catch (err) {
    showError(err.message);
  }
});

// Delegated handler for the dynamically rendered book action buttons
bookList.addEventListener("click", async (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  clearError();
  const { action, id } = btn.dataset;

  try {
    if (action === "checkout") {
      await checkoutBook(id);
      await refreshBooks();
    } else if (action === "return") {
      await returnBook(id);
      await refreshBooks();
    } else if (action === "delete") {
      if (confirm("Remove this book from the catalog?")) {
        await deleteBook(id);
        await refreshBooks();
      }
    } else if (action === "edit") {
      const book = state.books.find((b) => String(b.id) === String(id));
      if (!book) return;
      editBookForm.elements.id.value = book.id;
      editBookForm.elements.title.value = book.title;
      editBookForm.elements.author.value = book.author;
      editBookForm.elements.isbn.value = book.isbn;
      editModal.hidden = false;
    }
  } catch (err) {
    showError(err.message);
  }
});

async function refreshBooks() {
  await loadBooks();
  renderBooks();
}

// ---------- Boot ----------
(async function init() {
  await loadCurrentUser();
  render();
  try {
    await refreshBooks();
  } catch (err) {
    showError(err.message);
  }
})();
