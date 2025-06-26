//
 // API utility file for communicating with FastAPI backend at https://vscode-internal-57-qa.qa01.cloud.kavia.ai:3001
 //

const API_BASE_URL = "https://vscode-internal-57-qa.qa01.cloud.kavia.ai:3001";

/** Helper to get the token from localStorage */
export function getAuthToken() {
  return localStorage.getItem("token");
}

/** API request wrapper with proper headers and error handling */
async function apiRequest(endpoint, { method = "GET", data, auth = false } = {}) {
  const headers = {
    "Content-Type": "application/json",
  };
  if (auth) {
    const token = getAuthToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }
  const opts = {
    method,
    headers,
  };
  if (data) {
    opts.body = JSON.stringify(data);
  }
  const resp = await fetch(API_BASE_URL + endpoint, opts);
  if (resp.status === 204) return null; // No Content
  const json = await resp.json();
  if (!resp.ok) {
    // FastAPI typically sends {"detail": ...}
    throw new Error(json.detail || "API error");
  }
  return json;
}

// PUBLIC_INTERFACE
export async function loginUser(username, password) {
  // FastAPI: typically POST /login or /token
  return apiRequest("/auth/login", {
    method: "POST",
    data: { username, password },
  });
}

// PUBLIC_INTERFACE
export async function registerUser(username, password) {
  return apiRequest("/auth/register", {
    method: "POST",
    data: { username, password },
  });
}

// PUBLIC_INTERFACE
export async function getCurrentUser() {
  return apiRequest("/users/me", { auth: true });
}

// PUBLIC_INTERFACE
export async function getTasks(category = null) {
  let endpoint = "/tasks";
  if (category) {
    endpoint += "?category=" + encodeURIComponent(category);
  }
  return apiRequest(endpoint, { auth: true });
}

// PUBLIC_INTERFACE
export async function getCategories() {
  // Assume /categories returns all category names
  return apiRequest("/categories", { auth: true });
}

// PUBLIC_INTERFACE
export async function createTask(task) {
  return apiRequest("/tasks", { method: "POST", data: task, auth: true });
}

// PUBLIC_INTERFACE
export async function updateTask(taskId, updates) {
  return apiRequest(`/tasks/${taskId}`, { method: "PUT", data: updates, auth: true });
}

// PUBLIC_INTERFACE
export async function deleteTask(taskId) {
  return apiRequest(`/tasks/${taskId}`, { method: "DELETE", auth: true });
}
