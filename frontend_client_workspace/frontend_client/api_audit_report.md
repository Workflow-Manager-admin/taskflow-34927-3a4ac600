# API Audit Report – Frontend vs. backend_api_endpoints.md

## Summary

This audit reviews all API usage in `src/api.js` and frontend components, and cross-references it with `backend_api_endpoints.md`. Discrepancies, mismatches, or potential contract violations are reported below for correction.

---

## Authentication Endpoints

### 1. Register User

- **Backend:**  
  - Route: `/register`
  - Method: POST
  - JSON body: `{ username, password }`
  - Response: `{ message, username }`
- **Frontend (registerUser):**
  - Route: `/register`
  - Method: POST
  - JSON body: `{ username, password }`
  - **Response Assumptions:** Treated as success if no error.
- **Result:** ✅ Match (no significant issue)

---

### 2. Login (Token)

- **Backend:**  
  - Route: `/auth/token`
  - Method: POST
  - Form data: `username`, `password`
  - Response: `{ access_token, token_type }`
- **Frontend (loginUser):**
  - Route: `/login`
  - Method: POST
  - JSON: `{ username, password }`
  - **Mismatch:**
    - Wrong endpoint: should be `/auth/token`
    - Wrong method: backend expects `application/x-www-form-urlencoded` not JSON
- **Resolution Required:**  
  - Change endpoint to `/auth/token`
  - Change request to send as URL-encoded form data
  - Adjust usage as necessary

---

### 3. Get Current User

- **Backend:**  
  - Route: `/auth/me`
  - Method: GET, Bearer token required
  - Response: `{ username, full_name, disabled }`
- **Frontend (getCurrentUser):**
  - Route: `/users/me`
  - Method: GET, Bearer token set
  - **Mismatch:** Wrong endpoint: should be `/auth/me`
- **Resolution Required:**  
  - Change endpoint to `/auth/me`

---

## Category Endpoints

### List Categories

- **Backend:**  
  - Route: `/categories`
  - Method: GET, Bearer token required
  - Response: `[{"id", "name"}]`
- **Frontend (getCategories):**
  - Route: `/categories`
  - Method: GET, Bearer token set
  - **Parsed as:** list of category strings, assumed from backend example
  - **Mismatch:** Frontend expects array of category strings, but backend returns array of objects (`{id, name}`)
- **Resolution Required:**  
  - Update frontend to expect array of objects, and extract/handle `name` values as needed

---

## Task Endpoints

### Create Task

- **Backend:**  
  - Route: `/tasks`
  - Method: POST, Bearer token required
  - JSON body: `{ title, description, status, category, due_date }`
- **Frontend (createTask):**
  - Route: `/tasks`
  - Method: POST, Bearer token set
  - JSON body: `{ name, description, status, category }`
  - **Mismatches:**  
    - Field name: uses `name` (frontend) vs `title` (backend)
    - Status values: (front uses `todo`, `in_progress`, `done`; backend expects `TODO`, `IN_PROGRESS`, `DONE` — uppercase only)
    - Missing support for `due_date`
- **Resolution Required:**  
  - Change body field from `name` to `title`
  - Ensure status is sent in uppercase on all requests
  - Optionally add `due_date` support

---

### List Tasks

- **Backend:**  
  - Route: `/tasks`
  - Method: GET, Bearer token required
  - Query params: `status`, `category` (matching backend convention)
  - Response: list of task objects
- **Frontend (getTasks):**
  - Route: `/tasks?category=...`
  - Method: GET, Bearer token set
  - **Mismatch:** No filtering by status; `category` param assumed, but backend expects either param by backend definition
- **Resolution:** Acceptable (the frontend currently only uses `category`, but must ensure param names and values case/meaning match backend)

---

### Update Task

- **Backend:**  
  - Route: `/tasks/{task_id}`
  - Method: PUT, Bearer token required
  - JSON body: any of `{ title, description, status, category, due_date }`
- **Frontend (updateTask):**
  - Route: `/tasks/{id}`
  - Method: PUT, Bearer token set
  - JSON body: `{ name, description, status, category }`
  - **Mismatches:**  
    - Same as create: field `name` should be `title`
    - Status value should match backend enum (uppercase)
- **Resolution Required:**  
  - Change body field from `name` to `title`
  - Ensure status value is `TODO`, `IN_PROGRESS`, or `DONE`

---

### Delete Task

- **Backend:**  
  - Route: `/tasks/{task_id}`
  - Method: DELETE, Bearer token required
- **Frontend (deleteTask):**
  - Route: `/tasks/{id}`
  - Method: DELETE, Bearer token set
  - **Result:** ✅ Match

---

## Additional Notes

- Frontend status enum: maps values `todo`, `in_progress`, `done` (JS) → backend expects `TODO`, `IN_PROGRESS`, `DONE` (uppercase, underscores)
- `due_date` is not handled anywhere on the frontend
- All protected endpoints require Bearer token, which the frontend correctly provides

---

## Summary Table

| Area         | Mismatch? | Notes |
|--------------|-----------|-------|
| Register     |    ❌     | OK    |
| Login        |    ✅     | Endpoint/method/content-type is wrong |
| Get User     |    ✅     | Endpoint wrong |
| Categories   |    ✅     | Response shape mismatch (see details) |
| Create Task  |    ✅     | Field(s) mismatch: 'name' vs 'title', status convention |
| Update Task  |    ✅     | Field(s) mismatch: 'name' vs 'title', status convention |
| Delete Task  |    ❌     | OK    |

---

**Corrections Required (in code):**
1. loginUser: Change to `/auth/token` with form-encoded body
2. getCurrentUser: Change to `/auth/me`
3. getCategories: Adapt to expect array of objects, use `.name`
4. createTask/updateTask: Change sent field `name` → `title`; send status as backend expects (uppercase with underscores)
5. All task CRUD: consider supporting `due_date`

---

_This audit covers code in `src/api.js` and assumes all component API calls route through these functions. If direct fetch() or axios calls exist in components, further review is warranted._

