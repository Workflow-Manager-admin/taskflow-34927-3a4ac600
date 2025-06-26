import React, { useState } from "react";

/**
 * PUBLIC_INTERFACE
 * Task Form for Add/Edit task modal.
 * Props:
 * - onSubmit: function(taskObj)
 * - initial: initial values {title, description, status, category, due_date}
 * - categories: Array<string>
 * - loading: boolean
 * - mode: "add" | "edit"
 */
function TaskForm({ onSubmit, initial = {}, categories, loading, mode }) {
  // Map both "name" and "title" from props for back/forward compatibility
  const [title, setTitle] = useState(initial.title || initial.name || "");
  const [description, setDescription] = useState(initial.description || "");
  // Status input is frontend string: "todo", "in_progress", "done"
  const [status, setStatus] = useState(
    (initial.status || "todo").toLowerCase()
  );
  const [category, setCategory] = useState(initial.category || "");
  const [dueDate, setDueDate] = useState(initial.due_date || "");
  const [error, setError] = useState("");

  // PUBLIC_INTERFACE
  function handleSubmit(e) {
    e.preventDefault();
    if (!title.trim() || !status) {
      setError("Task title and status are required");
      return;
    }
    setError("");
    // Pass name as alias for legacy, real backend uses title.
    const payload = {
      name: title,
      title: title,
      description,
      status,
      category,
    };
    if (dueDate) payload.due_date = dueDate;
    onSubmit(payload);
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div style={{ color: "#e53935", marginBottom: 10 }}>{error}</div>
      )}
      <div className="form-group">
        <label>Task Title</label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
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
      <div className="form-group">
        <label>Due Date (optional)</label>
        <input
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          disabled={loading}
        />
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
