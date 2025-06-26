import React, { useState, useEffect } from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import TaskList from "./components/TaskList";
import Modal from "./components/Modal";
import TaskForm from "./components/TaskForm";
import AuthForm from "./components/AuthForm";

import {
  loginUser,
  registerUser,
  getCurrentUser,
  getTasks,
  getCategories,
  createTask,
  updateTask,
  deleteTask,
} from "./api";

// PUBLIC_INTERFACE
function App() {
  const [theme] = useState("light"); // theme switching planned; only light for now.
  // Authentication & User
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  // Sidebar and Categories
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  // Tasks & Data
  const [tasks, setTasks] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(false);

  // Modals
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [taskModalLoading, setTaskModalLoading] = useState(false);

  // Status/Error
  const [globalError, setGlobalError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Set page theme (light only; can be extended)
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // On mount, check existing login (token in localStorage)
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      getCurrentUser()
        .then((user) => {
          setUser(user);
        })
        .catch(() => {
          localStorage.removeItem("token");
          setUser(null);
        });
    }
  }, []);

  // Load tasks and categories when auth and category change
  useEffect(() => {
    if (user) {
      fetchTasks();
      fetchCategories();
    }
  // eslint-disable-next-line
  }, [user, selectedCategory]);

  // PUBLIC_INTERFACE
  async function handleLogin(username, password) {
    setAuthLoading(true);
    setAuthError("");
    try {
      const result = await loginUser(username, password);
      localStorage.setItem("token", result.access_token);
      const userObj = await getCurrentUser();
      setUser(userObj);
    } catch (err) {
      setAuthError(err.message || "Login failed");
    }
    setAuthLoading(false);
  }

  // PUBLIC_INTERFACE
  async function handleRegister(username, password) {
    setAuthLoading(true);
    setAuthError("");
    try {
      await registerUser(username, password);
      // Auto-login after register
      const loginRes = await loginUser(username, password);
      localStorage.setItem("token", loginRes.access_token);
      const userObj = await getCurrentUser();
      setUser(userObj);
    } catch (err) {
      setAuthError(err.message || "Registration failed");
    }
    setAuthLoading(false);
  }

  // PUBLIC_INTERFACE
  function handleLogout() {
    setUser(null);
    localStorage.removeItem("token");
    setTasks([]);
    setCategories([]);
    setSelectedCategory(null);
    setSuccessMsg("");
  }

  // PUBLIC_INTERFACE
  async function fetchTasks() {
    setLoadingTasks(true);
    setGlobalError("");
    try {
      const data = await getTasks(selectedCategory);
      setTasks(data);
    } catch (e) {
      setGlobalError(e.message ?? "Could not fetch tasks.");
      setTasks([]);
    }
    setLoadingTasks(false);
  }

  // PUBLIC_INTERFACE
  async function fetchCategories() {
    try {
      const cats = await getCategories();
      setCategories(cats);
    } catch (e) {
      setCategories([]);
    }
  }

  // PUBLIC_INTERFACE
  function openCreateTask() {
    setEditTask(null);
    setShowTaskModal(true);
  }
  // PUBLIC_INTERFACE
  function openEditTask(task) {
    setEditTask(task);
    setShowTaskModal(true);
  }

  // PUBLIC_INTERFACE
  function closeTaskModal() {
    setEditTask(null);
    setShowTaskModal(false);
    setTaskModalLoading(false);
  }

  // PUBLIC_INTERFACE
  async function handleTaskFormSubmit(taskObj) {
    setTaskModalLoading(true);
    setGlobalError("");
    try {
      if (editTask) {
        await updateTask(editTask.id, taskObj);
        setSuccessMsg("Task updated!");
      } else {
        await createTask(taskObj);
        setSuccessMsg("Task created!");
      }
      closeTaskModal();
      fetchTasks();
      fetchCategories();
    } catch (e) {
      setGlobalError(e.message ?? "Failed to save task.");
    }
    setTaskModalLoading(false);
  }

  // PUBLIC_INTERFACE
  async function handleDeleteTask(task) {
    if (!window.confirm("Delete this task?")) return;
    try {
      await deleteTask(task.id);
      setSuccessMsg("Task deleted!");
      fetchTasks();
      fetchCategories();
    } catch (e) {
      setGlobalError(e.message ?? "Could not delete task.");
    }
  }

  // UI: Modal + status reset
  useEffect(() => {
    if (successMsg) {
      const timeout = setTimeout(() => setSuccessMsg(""), 2000);
      return () => clearTimeout(timeout);
    }
  }, [successMsg]);

  // --- UI Render ---
  if (!user) {
    // Show login/register form
    return (
      <div className="App">
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "var(--bg-primary)",
          }}
        >
          <div
            style={{
              minWidth: 300,
              maxWidth: 340,
              width: "100%",
              background: "var(--bg-secondary)",
              borderRadius: 18,
              boxShadow: "0 4px 25px #0001",
              padding: "2.5rem 2rem",
            }}
          >
            <div
              style={{
                textAlign: "center",
                fontWeight: 700,
                fontSize: "1.45rem",
                color: "var(--primary)",
                marginBottom: 16,
                letterSpacing: "0.01em",
              }}
            >
              TaskFlow
            </div>
            <AuthForm
              mode={authMode}
              onSubmit={
                authMode === "login" ? handleLogin : handleRegister
              }
              loading={authLoading}
              error={authError}
              toggleMode={() =>
                setAuthMode(authMode === "login" ? "register" : "login")
              }
            />
            <div style={{textAlign:"center",marginTop:"25px",fontSize:"0.94em",color:"#96770088"}}>
              Modern minimal task manager
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Navbar user={user} onLogout={handleLogout} />
      <div className="layout">
        <Sidebar
          categories={categories}
          selected={selectedCategory}
          onSelect={setSelectedCategory}
        />
        <main className="main-content">
          <div style={{display:"flex",justifyContent:"space-between",alignItems:'flex-start',flexWrap:"wrap"}}>
            <h1 style={{margin:"0 0 12px 0",fontWeight:700,fontSize:"1.32em"}}>My Tasks {selectedCategory ? `– ${selectedCategory}` : ""}</h1>
            <button
              className="btn btn-accent"
              style={{marginLeft:"auto"}}
              onClick={openCreateTask}
              title="Add Task"
            >
              + Add Task
            </button>
          </div>
          {successMsg && (
            <div
              style={{
                color: "var(--primary)",
                background: "#e5f7ff",
                borderLeft: "5px solid var(--primary)",
                marginBottom: "1.2em",
                padding: "0.9em 1.2em",
                borderRadius: 7,
                fontWeight: "500",
              }}
            >
              {successMsg}
            </div>
          )}
          {globalError && (
            <div
              style={{
                color: "#b71c1c",
                background: "#ffeaea",
                borderLeft: "4px solid #e53935",
                marginBottom: 20,
                padding: "0.8em 1.1em",
                borderRadius: 7,
                fontWeight: "500",
              }}
            >
              {globalError}
            </div>
          )}
          {loadingTasks ? (
            <div style={{ color: "var(--primary)", marginTop: 26, textAlign: "center" }}>
              Loading tasks...
            </div>
          ) : (
            <TaskList
              tasks={tasks}
              onEdit={openEditTask}
              onDelete={handleDeleteTask}
            />
          )}

          <Modal
            open={showTaskModal}
            title={editTask ? "Edit Task" : "Add Task"}
            onClose={closeTaskModal}
          >
            <TaskForm
              mode={editTask ? "edit" : "add"}
              initial={editTask || {}}
              categories={categories}
              loading={taskModalLoading}
              onSubmit={handleTaskFormSubmit}
            />
          </Modal>
        </main>
      </div>

      <button
        className="add-task-fab"
        onClick={openCreateTask}
        title="Add Task"
        aria-label="Add Task"
      >
        +
      </button>
    </div>
  );
}

export default App;
