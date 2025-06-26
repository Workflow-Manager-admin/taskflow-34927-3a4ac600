# Taskflow Backend API – Endpoints and Schemas

This document provides a complete specification of all implemented API endpoints in `backend_api`, including route, HTTP method, request/response schemas, and a usage summary.

---

## Table of Contents
1. [Authentication Endpoints](#authentication-endpoints)
    - Register User
    - Login (Token)
    - Get Current User
2. [Category Endpoints](#category-endpoints)
    - List Categories
3. [Task Endpoints](#task-endpoints)
    - Create Task
    - List Tasks
    - Read Single Task
    - Update Task
    - Delete Task
4. [Health Check](#health-check)
5. [Schemas](#schemas)

---

## Authentication Endpoints

### 1. Register User
- **Route:** `/register`
- **Method:** `POST`
- **Tags:** `auth`
- **Request Body:** `UserRegister` (JSON)
    ```json
    {
      "username": "string (3-32 chars)",
      "password": "string (6+ chars)"
    }
    ```
- **Response:** `UserRegisterResponse`
    ```json
    {
      "message": "User registered successfully.",
      "username": "string"
    }
    ```
- **Status Codes:** `201` (Created), `400` (Invalid username/password or already exists)

---

### 2. Login (Token)
- **Route:** `/auth/token`
- **Method:** `POST`
- **Tags:** `auth`
- **Request Body:** Form fields (`application/x-www-form-urlencoded`)
    - `username`: string
    - `password`: string
- **Response:** `Token`
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```
- **Status Codes:** `200`, `401` (Incorrect credentials)

---

### 3. Get Current User
- **Route:** `/auth/me`
- **Method:** `GET`
- **Tags:** `auth`
- **Headers:** `Authorization: Bearer <JWT>`
- **Response:** `User`
    ```json
    {
      "username": "string",
      "full_name": "string",
      "disabled": false
    }
    ```
- **Status Codes:** `200`, `400` (if user is inactive), `401` (invalid token)

---

## Category Endpoints

### 4. List Categories
- **Route:** `/categories`
- **Method:** `GET`
- **Tags:** `tasks`
- **Headers:** `Authorization: Bearer <JWT>`
- **Response:** List of `Category`
    ```json
    [
      {
        "id": 1,
        "name": "Work"
      },
      {
        "id": 2,
        "name": "Personal"
      }
    ]
    ```
- **Status Codes:** `200`

---

## Task Endpoints

### 5. Create Task
- **Route:** `/tasks`
- **Method:** `POST`
- **Tags:** `tasks`
- **Headers:** `Authorization: Bearer <JWT>`
- **Request Body:** `TaskCreate` (JSON)
    ```json
    {
      "title": "string",
      "description": "string (optional)",
      "status": "TODO | IN_PROGRESS | DONE",
      "category": "string (optional)",
      "due_date": "ISO 8601 datetime (optional)"
    }
    ```
- **Response:** `Task`
    ```json
    {
      "id": 1,
      "title": "string",
      "description": "string (optional)",
      "status": "TODO | IN_PROGRESS | DONE",
      "category": "string (optional)",
      "due_date": "datetime (optional)",
      "created_at": "datetime"
    }
    ```
- **Status Codes:** `201` (Created)

---

### 6. List Tasks
- **Route:** `/tasks`
- **Method:** `GET`
- **Tags:** `tasks`
- **Headers:** `Authorization: Bearer <JWT>`
- **Query Params:**
    - `status`: string (optional, filter by task status)
    - `category`: string (optional, filter by category)
- **Response:** List of `Task`
    ```json
    [
      {
        "id": 1,
        "title": "...",
        "description": "...",
        "status": "...",
        "category": "...",
        "due_date": "...",
        "created_at": "..."
      }
    ]
    ```
- **Status Codes:** `200`

---

### 7. Read Single Task
- **Route:** `/tasks/{task_id}`
- **Method:** `GET`
- **Tags:** `tasks`
- **Headers:** `Authorization: Bearer <JWT>`
- **Response:** `Task`
- **Status Codes:** `200`, `404` (not found or not owned by user)

---

### 8. Update Task
- **Route:** `/tasks/{task_id}`
- **Method:** `PUT`
- **Tags:** `tasks`
- **Headers:** `Authorization: Bearer <JWT>`
- **Request Body:** `TaskUpdate` (JSON, all properties optional)
    ```json
    {
      "title": "string (optional)",
      "description": "string (optional)",
      "status": "TODO | IN_PROGRESS | DONE (optional)",
      "category": "string (optional)",
      "due_date": "datetime (optional)"
    }
    ```
- **Response:** `Task`
- **Status Codes:** `200`, `404` (not found or not owned by user)

---

### 9. Delete Task
- **Route:** `/tasks/{task_id}`
- **Method:** `DELETE`
- **Tags:** `tasks`
- **Headers:** `Authorization: Bearer <JWT>`
- **Response:**
    ```json
    {
      "detail": "Task deleted"
    }
    ```
- **Status Codes:** `200`, `404` (not found or not owned by user)

---

## Health Check

- **Route:** `/`
- **Method:** `GET`
- **Tags:** `health`
- **Response:**
    ```json
    {
      "message": "Healthy"
    }
    ```
- **Status Codes:** `200`

---

## Schemas

### UserRegister
| Field     | Type   | Required | Description                       |
|-----------|--------|----------|-----------------------------------|
| username  | string | Yes      | 3-32 chars, account username      |
| password  | string | Yes      | 6-128 chars, user password        |

### UserRegisterResponse
| Field    | Type   | Description                       |
|----------|--------|-----------------------------------|
| message  | string | Success message                   |
| username | string | Registered username               |

### Token
| Field        | Type   | Description                               |
|--------------|--------|-------------------------------------------|
| access_token | string | JWT access token                          |
| token_type   | string | Type of token (always "bearer")           |

### User
| Field     | Type    | Description                                |
|-----------|---------|--------------------------------------------|
| username  | string  | Username                                   |
| full_name | string  | Full name                                  |
| disabled  | boolean | User is disabled (optional)                |

### Category
| Field | Type | Description               |
|-------|------|--------------------------|
| id    | int  | Category ID              |
| name  | str  | Category name            |

### TaskBase (Used in TaskCreate)
| Field       | Type    | Required | Description                      |
|-------------|---------|----------|----------------------------------|
| title       | string  | Yes      | Title of the task                |
| description | string  | No       | Description of the task          |
| status      | string  | Yes      | TODO, IN_PROGRESS, or DONE       |
| category    | string  | No       | Category name                    |
| due_date    | string  | No       | ISO 8601 datetime string         |

### TaskCreate
Inherits from TaskBase.

### TaskUpdate
| Field       | Type    | Optional | Description                      |
|-------------|---------|----------|----------------------------------|
| title       | string  | Yes      | Title of the task                |
| description | string  | Yes      | Description of the task          |
| status      | string  | Yes      | TODO, IN_PROGRESS, or DONE       |
| category    | string  | Yes      | Category name                    |
| due_date    | string  | Yes      | ISO 8601 datetime string         |

### Task
| Field       | Type    | Description                     |
|-------------|---------|---------------------------------|
| id          | int     | Task ID                         |
| title       | string  | Title of the task               |
| description | string  | Description of the task         |
| status      | string  | TODO, IN_PROGRESS, or DONE      |
| category    | string  | Category name                   |
| due_date    | string  | Due date (ISO 8601, optional)   |
| created_at  | string  | Creation datetime (ISO 8601)    |

---

## Summary

This backend exposes RESTful endpoints to register, authenticate users, and perform CRUD operations on tasks, including filtering and categorization. All protected endpoints require a JWT Bearer token (issued by `/auth/token`). Requests and responses strictly follow the specified schemas above.

---

## Mermaid Diagram

```mermaid
flowchart TD
    subgraph Auth
        REG[/POST\/register/] --> TOK[/POST\/auth/token/]
        TOK --> ME[/GET\/auth/me/]
    end
    subgraph Categories
        CAT[/GET\/categories/] 
    end
    subgraph Tasks
        CREATE[/POST\/tasks/] --> LIST[/GET\/tasks/]
        LIST --> READ[/GET\/tasks/{task_id}/]
        READ --> UPDATE[/PUT\/tasks/{task_id}/]
        UPDATE --> DELETE[/DELETE\/tasks/{task_id}/]
    end
    HEALTH[/GET \//] 
    REG -.->|JWT| CREATE
    TOK -.->|JWT| CREATE
    TOK -.->|JWT| CAT
    TOK -.->|JWT| LIST
    TOK -.->|JWT| READ
    TOK -.->|JWT| UPDATE
    TOK -.->|JWT| DELETE
    TOK -.->|JWT| CAT
```

---

_Last Updated: Automatically generated from FastAPI source in `backend_api_workspace/backend_api/src/api/main.py`._
