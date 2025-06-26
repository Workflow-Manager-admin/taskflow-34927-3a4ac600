import React, { useState } from "react";

/**
 * PUBLIC_INTERFACE
 * Task Form for Add/Edit task modal.
 * Props:
 * - onSubmit: function(taskObj)
 * - initial: initial values {name, description, status, category}
 * - categories: Array<string>
 * - loading: boolean
 * - mode: "add" | "edit"
 */
function TaskForm({ onSubmit, initial = {}, categories, loading, mode }) {
  const [name, setName] = useState(initial.name || "");
  const [description, setDescription] = useState(initial.description || "");
  const [status, setStatus] = useState(initial.status || "todo");
  const [category, setCategory] = useState(initial.category || "");
  const [error, setError] = useState("");

  // PUBLIC_INTERFACE
  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim() || !status) {
      setError("Task name and status are required");
      return;
    }
    setError("");
    onSubmit({ name, description, status, category });
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div style={{ color: "#e53935", marginBottom: 10 }}>{error}</div>
      )}
      <div className="form-group">
        <label>Task Name</label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={60}
          required
          disabled={loading}
        />
      </div>
      <div className="form-group">
        <label>Description</label>
        <textarea
          rows={2}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={250}
          disabled={loading}
        />
      </div>
      <div className="form-group">
        <label>Status</label>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          required
          disabled={loading}
        >
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
        </select>
      </div>
      <div className="form-group">
        <label>Category</label>
        <input
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          list="categories"
          placeholder="Type or select"
          disabled={loading}
        />
        <datalist id="categories">
          {categories.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </datalist>
      </div>
      <div className="modal-actions">
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading
            ? mode === "add"
              ? "Adding..."
              : "Saving..."
            : mode === "add"
            ? "Add Task"
            : "Save Changes"}
        </button>
      </div>
    </form>
  );
}

export default TaskForm;
