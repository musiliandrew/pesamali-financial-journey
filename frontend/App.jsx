import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ClerkProvider, SignedIn, SignedOut } from "@clerk/clerk-react";
import { Toaster } from "@/components/ui/toaster";
import Onboarding from "./pages/Onboarding";
import Profile from "./pages/Profile";
import Lobby from "./pages/Lobby";
import Game from "./pages/Game";
import PostGame from "./pages/PostGame";

const queryClient = new QueryClient();
const PUBLISHABLE_KEY = "pk_test_cHJlc2VudC13cmVuLTUwLmNsZXJrLmFjY291bnRzLmRldiQ";

function AppInner() {
  return (
    <BrowserRouter>
      <div className="dark min-h-screen bg-[#0F1724]">
        <SignedOut>
          <Routes>
            <Route path="*" element={<Onboarding />} />
          </Routes>
        </SignedOut>
        <SignedIn>
          <Routes>
            <Route path="/" element={<Navigate to="/lobby" replace />} />
            <Route path="/onboarding" element={<Navigate to="/lobby" replace />} />
            <Route path="/profile/:userId" element={<Profile />} />
            <Route path="/lobby" element={<Lobby />} />
            <Route path="/game/:matchId" element={<Game />} />
            <Route path="/post-game/:matchId" element={<PostGame />} />
          </Routes>
        </SignedIn>
        <Toaster />
      </div>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <QueryClientProvider client={queryClient}>
        <AppInner />
      </QueryClientProvider>
    </ClerkProvider>
  );
}
