import { useState, useCallback } from "react";

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";

export function useAuth() {
  const [token, setToken] = useState<string | null>(
    typeof window !== "undefined" ? localStorage.getItem("jwt") : null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveToken = useCallback((t: string | null) => {
    if (typeof window === "undefined") return;
    if (t) localStorage.setItem("jwt", t);
    else localStorage.removeItem("jwt");
    setToken(t);
  }, []);

  const register = useCallback(async (username: string, password: string, email?: string, profession?: string) => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email, profession }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Register failed");
      const data = await res.json();
      saveToken(data.token);
      return data;
    } catch (e: any) {
      setError(e.message || String(e));
      throw e;
    } finally {
      setLoading(false);
    }
  }, [saveToken]);

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
      const data = await res.json();
      saveToken(data.token);
      return data;
    } catch (e: any) {
      setError(e.message || String(e));
      throw e;
    } finally {
      setLoading(false);
    }
  }, [saveToken]);

  const logout = useCallback(() => {
    saveToken(null);
  }, [saveToken]);

  return { token, loading, error, register, login, logout };
}
