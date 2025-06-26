import React from "react";

/**
 * PUBLIC_INTERFACE
 * Top navigation bar with branding and user/logout functionality.
 * Props:
 * - user: {username: string} or null
 * - onLogout: () => void
 */
function Navbar({ user, onLogout }) {
  return (
    <nav className="navbar">
      <span className="navbar-title">TaskFlow</span>
      <span className="navbar-user">
        {user ? (
          <>
            {user.username}
            <button className="navbar-logout" onClick={onLogout}>
              Logout
            </button>
          </>
        ) : null}
      </span>
    </nav>
  );
}

export default Navbar;
