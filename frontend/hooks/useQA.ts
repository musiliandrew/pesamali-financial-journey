import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";

export function useSendChallenge() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = useCallback(async (toUserId: string, profession?: string) => {
    setLoading(true); setError(null);
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
      const res = await fetch(`${API_BASE}/qa/challenge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ toUserId, profession }),
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

  return { send, loading, error };
}

export function useChallenges(initialPage = 1, initialPageSize = 20) {
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [meta, setMeta] = useState<{ page: number; page_size: number; total: number } | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
        const res = await fetch(`${API_BASE}/qa/challenges?page=${page}&page_size=${pageSize}`, {
          headers: {
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });
        if (!res.ok) throw new Error((await res.json()).detail || `Failed: ${res.status}`);
        const json = await res.json();
        if (mounted) {
          setEntries(json.entries || []);
          setMeta(json.meta || null);
        }
      } catch (e: any) {
        if (mounted) setError(e.message || String(e));
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [page, pageSize]);

  return { entries, loading, error, meta, page, pageSize, setPage, setPageSize };
}

export function useSubmitAnswer() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(async (challengeId: string, selectedOption: number) => {
    setLoading(true); setError(null);
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
      const res = await fetch(`${API_BASE}/qa/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ challengeId, selectedOption }),
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

  return { submit, loading, error };
}
