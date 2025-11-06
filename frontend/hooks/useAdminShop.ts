import { useCallback, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";
const authHeader = () => {
  const t = typeof window !== 'undefined' ? localStorage.getItem('jwt') : null;
  return t ? { Authorization: `Bearer ${t}` } : {} as Record<string, string>;
};

export function useAdminShop(){
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string|null>(null);

  const load = useCallback(async()=>{
    setLoading(true); setError(null);
    try{ const r=await fetch(`${API_BASE}/admin/shop/items`,{ headers:{...authHeader()} }); if(!r.ok) throw new Error((await r.json()).detail||`Failed:${r.status}`); setItems(await r.json()); }
    catch(e:any){ setError(e.message||String(e)); }
    finally{ setLoading(false); }
  },[]);

  useEffect(()=>{ load(); },[load]);

  const create = useCallback(async(p:any)=>{
    const r = await fetch(`${API_BASE}/admin/shop/items/`,{ method:'POST', headers:{ 'Content-Type':'application/json', ...authHeader() }, body: JSON.stringify(p)});
    if(!r.ok) throw new Error((await r.json()).detail||`Failed:${r.status}`);
    await load();
  },[load]);

  const remove = useCallback(async(id:string)=>{
    const r = await fetch(`${API_BASE}/admin/shop/items/${id}`,{ method:'DELETE', headers:{ ...authHeader() } });
    if(!r.ok) throw new Error((await r.json()).detail||`Failed:${r.status}`);
    await load();
  },[load]);

  return { items, loading, error, create, remove, reload: load };
}
