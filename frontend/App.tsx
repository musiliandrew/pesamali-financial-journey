import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Lobby from "./pages/Lobby";
import Game from "./pages/Game";
import Profile from "./pages/Profile";
import Onboarding from "./pages/Onboarding";
import PostGame from "./pages/PostGame";
import Leaderboard from "./pages/Leaderboard";
import Challenges from "./pages/Challenges";
import Shop from "./pages/Shop";

export default function App() {
  return (
    <BrowserRouter>
      <div className="dark min-h-screen bg-[#0F1724]">
        <Routes>
          <Route path="/" element={<Navigate to="/onboarding" />} />
          <Route path="/lobby" element={<Lobby />} />
          <Route path="/game/:id" element={<Game />} />
          <Route path="/profile/:id" element={<Profile />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/postgame" element={<PostGame />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/challenges" element={<Challenges />} />
          <Route path="/shop" element={<Shop />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
