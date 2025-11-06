import backend from "~backend/client";

export function useBackend() {
  const token = typeof window !== "undefined" ? localStorage.getItem("jwt") : null;
  if (!token) return backend;

  return backend.with({
    auth: async () => ({ authorization: `Bearer ${token}` }),
  });
}
