// src/components/auth/AuthButton.tsx
import React from "react";
import { useAuth } from "./useAuth";

export default function AuthButton() {
  const { isAuthenticated, login, logout } = useAuth();

  return (
    <button
      onClick={isAuthenticated ? logout : login}
      style={{
        position: "fixed",
        top: 16,
        right: 16,
        zIndex: 9999,
        padding: "6px 12px",
      }}
    >
      {isAuthenticated ? "Logout" : "Login"}
    </button>
  );
}
