import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";

export function useGlobalLeaderboard(initialPage = 1, initialPageSize = 50) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [meta, setMeta] = useState<{ page: number; page_size: number; total: number } | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/leaderboard/global?page=${page}&page_size=${pageSize}`);
        if (!res.ok) throw new Error(`Failed: ${res.status}`);
        const json = await res.json();
        if (mounted) {
          setData(json.entries || []);
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

  return { data, loading, error, meta, page, pageSize, setPage, setPageSize };
}

export function useProfessionLeaderboard(profession: string | null, initialPage = 1, initialPageSize = 50) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [meta, setMeta] = useState<{ page: number; page_size: number; total: number } | null>(null);

  useEffect(() => {
    if (!profession) return;
    let mounted = true;
    setLoading(true);
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/leaderboard/profession/${profession}?page=${page}&page_size=${pageSize}`);
        if (!res.ok) throw new Error(`Failed: ${res.status}`);
        const json = await res.json();
        if (mounted) {
          setData(json.entries || []);
          setMeta(json.meta || null);
        }
      } catch (e: any) {
        if (mounted) setError(e.message || String(e));
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [profession, page, pageSize]);

  return { data, loading, error, meta, page, pageSize, setPage, setPageSize };
}
