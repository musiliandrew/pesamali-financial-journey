import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";

function authHeader() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
  return token ? { Authorization: `Bearer ${token}` } : {} as Record<string, string>;
}

export function useAdminQuestions() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/admin/qa/questions`, { headers: { ...authHeader() } });
      if (!res.ok) throw new Error((await res.json()).detail || `Failed: ${res.status}`);
      const data = await res.json();
      setItems(data);
    } catch (e:any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const create = useCallback(async (payload: { profession?: string; question: string; options: string[]; correct_option: number; explanation?: string; difficulty?: number; }) => {
    const res = await fetch(`${API_BASE}/admin/qa/questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error((await res.json()).detail || `Failed: ${res.status}`);
    await load();
  }, [load]);

  const remove = useCallback(async (id: string) => {
    const res = await fetch(`${API_BASE}/admin/qa/questions/${id}`, {
      method: 'DELETE',
      headers: { ...authHeader() },
    });
    if (!res.ok) throw new Error((await res.json()).detail || `Failed: ${res.status}`);
    await load();
  }, [load]);

  return { items, loading, error, reload: load, create, remove };
}
