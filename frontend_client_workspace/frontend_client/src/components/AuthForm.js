import React, { useState } from "react";

/**
 * PUBLIC_INTERFACE
 * AuthForm for login and register.
 * Props:
 * - mode: "login" or "register"
 * - onSubmit: function(username, password)
 * - loading: boolean
 * - error: message string
 * - toggleMode: function to switch login/register
 */
function AuthForm({ mode, onSubmit, loading, error, toggleMode }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  // PUBLIC_INTERFACE
  function handleSubmit(e) {
    e.preventDefault();
    onSubmit(username, password);
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={{ textAlign: "center", fontWeight: 600 }}>
        {mode === "login" ? "Login" : "Register"}
      </h2>
      <div className="form-group">
        <label>Username</label>
        <input
          autoFocus
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={loading}
          autoComplete="username"
          maxLength={32}
        />
      </div>
      <div className="form-group" style={{ marginBottom: 18 }}>
        <label>Password</label>
        <input
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loading}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          type="password"
          minLength={4}
          maxLength={64}
        />
      </div>
      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
      </button>
      <div style={{ textAlign: "center", marginTop: 17 }}>
        {mode === "login" ? (
          <span>
            New user?{" "}
            <button
              type="button"
              onClick={toggleMode}
              style={{ background: "none", border: "none", color: "var(--primary)", textDecoration: "underline", cursor: "pointer", fontSize: "1em" }}
            >
              Register
            </button>
          </span>
        ) : (
          <span>
            Have an account?{" "}
            <button
              type="button"
              onClick={toggleMode}
              style={{ background: "none", border: "none", color: "var(--primary)", textDecoration: "underline", cursor: "pointer", fontSize: "1em" }}
            >
              Login
            </button>
          </span>
        )}
      </div>
      {error && (
        <div style={{ color: "#e53935", marginTop: 17, fontWeight: 500, textAlign: "center" }}>
          {error}
        </div>
      )}
    </form>
  );
}

export default AuthForm;
