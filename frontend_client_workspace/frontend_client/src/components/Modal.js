import React from "react";

/**
 * PUBLIC_INTERFACE
 * Modal dialog and overlay.
 * Props:
 * - open: boolean
 * - title: string
 * - onClose: function
 * - children: content
 */
function Modal({ open, title, onClose, children }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose} aria-label="Close">&times;</button>
        <div className="modal-title">{title}</div>
        {children}
      </div>
    </div>
  );
}

export default Modal;
