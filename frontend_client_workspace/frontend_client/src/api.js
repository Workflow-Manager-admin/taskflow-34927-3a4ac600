//
// API utility file for communicating with FastAPI backend at https://vscode-internal-57-qa.qa01.cloud.kavia.ai:3001
//

const API_BASE_URL = "https://vscode-internal-57-qa.qa01.cloud.kavia.ai:3001";

// PUBLIC_INTERFACE
/** Helper to get the token from localStorage */
export function getAuthToken() {
  return localStorage.getItem("token");
}

/**
 * PUBLIC_INTERFACE
 * Core API request wrapper for JSON APIs with error handling.
 * Supports custom headers, form, and JSON payload.
 */
async function apiRequest(
  endpoint,
  { method = "GET", data, auth = false, form = false } = {}
) {
  let headers = {};
  let body;

  // Set headers and serialization
  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    if (data) {
      body = new URLSearchParams();
      Object.entries(data).forEach(([k, v]) =>
        body.append(k, v != null ? v : "")
      );
    }
  } else {
    headers["Content-Type"] = "application/json";
    if (data) {
      body = JSON.stringify(data);
    }
  }

  // Bearer token
  if (auth) {
    const token = getAuthToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const opts = {
    method,
    headers,
  };
  if (body) opts.body = body;

  const resp = await fetch(API_BASE_URL + endpoint, opts);

  // No Content, return null
  if (resp.status === 204) return null;

  // Try JSON parse
  let json;
  try {
    json = await resp.json();
  } catch (err) {
    throw new Error("Backend returned malformed response");
  }
  if (!resp.ok) {
    throw new Error(json.detail || "API error");
  }
  return json;
}

// PUBLIC_INTERFACE
/** 
 * Log in a user.
 * - Endpoint: POST /auth/token
 * - Content-Type: application/x-www-form-urlencoded
 * - Body: { username, password }
 * - Response: { access_token, token_type }
 */
export async function loginUser(username, password) {
  return apiRequest("/auth/token", {
    method: "POST",
    data: { username, password },
    form: true, // send as form-encoded
  });
}

// PUBLIC_INTERFACE
/**
 * Register a user. POST to /register.
 */
export async function registerUser(username, password) {
  return apiRequest("/register", {
    method: "POST",
    data: { username, password },
  });
}

// PUBLIC_INTERFACE
/**
 * Get current user info.
 * Endpoint: GET /auth/me (was /users/me).
 */
export async function getCurrentUser() {
  return apiRequest("/auth/me", { auth: true });
}

// PUBLIC_INTERFACE
/**
 * List all tasks, optionally filtered by category/status.
 * Query params: status, category (use backend format).
 */
export async function getTasks(category = null, status = null) {
  let endpoint = "/tasks";
  const params = [];
  if (category) params.push("category=" + encodeURIComponent(category));
  if (status) params.push("status=" + encodeURIComponent(status));
  if (params.length) endpoint += "?" + params.join("&");
  return apiRequest(endpoint, { auth: true });
}

// PUBLIC_INTERFACE
/**
 * Get list of categories (array of objects {id,name}).
 * Returns: [{id, name}]
 */
export async function getCategories() {
  // Backend returns array of {id, name}, frontend adapts to extract names.
  const cats = await apiRequest("/categories", { auth: true });
  return Array.isArray(cats) ? cats.map((c) => c.name) : [];
}

// PUBLIC_INTERFACE
/**
 * Create a task.
 * - Fields: {title, description, status, category, due_date}
 * - status must be uppercase: TODO, IN_PROGRESS, DONE
 * - title, not name.
 */
export async function createTask(task) {
  // Coerce frontend data to backend schema
  const payload = {
    title: task.name !== undefined ? task.name : task.title || "",
    description: task.description || "",
    status:
      (task.status || "")
        .replace(/ /g, "_")
        .toUpperCase(), // convert "in_progress" or "todo" → "IN_PROGRESS"
    category: task.category || "",
  };
  if (task.due_date) payload.due_date = task.due_date;
  return apiRequest("/tasks", { method: "POST", data: payload, auth: true });
}

// PUBLIC_INTERFACE
/**
 * Update a task.
 * - Same mapping as createTask.
 */
export async function updateTask(taskId, updates) {
  const payload = {};
  if (updates.name !== undefined || updates.title !== undefined)
    payload.title = updates.name !== undefined ? updates.name : updates.title;
  if (updates.description !== undefined) payload.description = updates.description;
  if (updates.status !== undefined)
    payload.status = updates.status.replace(/ /g, "_").toUpperCase();
  if (updates.category !== undefined) payload.category = updates.category;
  if (updates.due_date !== undefined) payload.due_date = updates.due_date;

  return apiRequest(`/tasks/${taskId}`, {
    method: "PUT",
    data: payload,
    auth: true,
  });
}

// PUBLIC_INTERFACE
export async function deleteTask(taskId) {
  return apiRequest(`/tasks/${taskId}`, { method: "DELETE", auth: true });
}
