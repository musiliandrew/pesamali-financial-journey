import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";

function authHeader() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
  return token ? { Authorization: `Bearer ${token}` } : {} as Record<string, string>;
}

export function useShopItems() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/shop/items`);
        if (!res.ok) throw new Error(`Failed: ${res.status}`);
        const json = await res.json();
        if (mounted) setItems(json);
      } catch (e: any) {
        if (mounted) setError(e.message || String(e));
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  return { items, loading, error };
}

export function usePurchaseItem() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const purchase = useCallback(async (itemId: string) => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/shop/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader() },
        body: JSON.stringify({ itemId })
      });
      if (!res.ok) throw new Error((await res.json()).detail || `Failed: ${res.status}`);
      return await res.json();
    } catch (e: any) {
      setError(e.message || String(e));
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { purchase, loading, error };
}
