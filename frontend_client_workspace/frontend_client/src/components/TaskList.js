import React from "react";

/**
 * PUBLIC_INTERFACE
 * Task list/table and actions.
 * Props:
 * - tasks: Array of tasks
 * - onEdit: function(task)
 * - onDelete: function(task)
 */
function TaskList({ tasks, onEdit, onDelete }) {
  // Status color classes
  // Accepts backend status as "TODO", "IN_PROGRESS", "DONE" → maps for CSS and user display
  const statusClass = (status) => {
    const s = (status || "").toLowerCase();
    if (s === "done") return "status-pill done";
    if (s === "in_progress" || s === "in progress" || s === "inprogress")
      return "status-pill inprogress";
    return "status-pill todo";
  };

  return (
    <table className="task-list-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Description</th>
          <th>Status</th>
          <th>Category</th>
          <th style={{ width: "110px" }}>Actions</th>
        </tr>
      </thead>
      <tbody>
        {tasks.map((t) => (
          <tr key={t.id}>
            <td>{t.title ?? t.name}</td>
            <td>{t.description}</td>
            <td>
              <span className={statusClass(t.status)}>
                {/* Show status as pretty string, e.g. "IN_PROGRESS" → "IN PROGRESS" */}
                {String(t.status || "")
                  .replace(/_/g, " ")
                  .toUpperCase()}
              </span>
            </td>
            <td>{t.category}</td>
            <td>
              <div className="action-btn-group">
                <button
                  className="action-btn edit"
                  onClick={() => onEdit(t)}
                  title="Edit"
                >
                  ✎
                </button>
                <button
                  className="action-btn delete"
                  onClick={() => onDelete(t)}
                  title="Delete"
                >
                  🗑
                </button>
              </div>
            </td>
          </tr>
        ))}
        {tasks.length === 0 && (
          <tr>
            <td colSpan={5} style={{ textAlign: "center", color: "#bbb" }}>
              No tasks to show.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

export default TaskList;
