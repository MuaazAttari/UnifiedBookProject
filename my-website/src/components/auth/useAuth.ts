// src/components/auth/useAuth.ts
export function useAuth() {
  return {
    user: null,          // future: actual user
    isAuthenticated: false,
    login: () => alert("Login clicked (wire later)"),
    logout: () => alert("Logout clicked"),
  };
}
