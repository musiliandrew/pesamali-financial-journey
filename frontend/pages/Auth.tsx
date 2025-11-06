import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function Auth() {
  const { register, login, logout, token, loading, error } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");

  return (
    <div className="min-h-screen p-6 max-w-md mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Auth</h1>

      <div className="space-y-2">
        <input className="w-full p-2 rounded bg-[#0F1724]" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
        <input className="w-full p-2 rounded bg-[#0F1724]" placeholder="Email (optional)" value={email} onChange={e => setEmail(e.target.value)} />
        <input type="password" className="w-full p-2 rounded bg-[#0F1724]" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
      </div>

      <div className="flex gap-2">
        <button disabled={loading} className="px-4 py-2 rounded bg-blue-600" onClick={() => register(username, password, email)}>Register</button>
        <button disabled={loading} className="px-4 py-2 rounded bg-green-600" onClick={() => login(username, password)}>Login</button>
        <button className="px-4 py-2 rounded bg-gray-600" onClick={() => logout()}>Logout</button>
      </div>

      {token && <div className="text-sm text-green-400">Logged in</div>}
      {error && <div className="text-sm text-red-400">{error}</div>}
    </div>
  );
}
