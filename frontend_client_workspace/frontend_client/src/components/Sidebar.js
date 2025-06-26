import React from "react";

/**
 * PUBLIC_INTERFACE
 * App sidebar for categories.
 * Props:
 * - categories: Array<string>
 * - selected: category string or null
 * - onSelect: function(category)
 */
function Sidebar({ categories, selected, onSelect }) {
  return (
    <aside className="sidebar">
      <h3 style={{fontWeight:"600",marginBottom:13,color:"var(--primary)",fontSize:15}}>Categories</h3>
      <ul className="category-list">
        <li>
          <button
            className={`category-item${!selected ? " selected" : ""}`}
            onClick={() => onSelect(null)}
          >
            All Tasks
          </button>
        </li>
        {categories.map((cat) => (
          <li key={cat}>
            <button
              className={`category-item${selected === cat ? " selected" : ""}`}
              onClick={() => onSelect(cat)}
            >
              {cat}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

export default Sidebar;
