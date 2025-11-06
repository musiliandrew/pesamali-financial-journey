import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useAuth } from "@/hooks/useAuth";

const TUTORIAL_SLIDES = [
  {
    title: "Welcome to PesaMali",
    description: "Learn financial literacy through play! Make smart money decisions to achieve your dreams.",
    image: "💰"
  },
  {
    title: "Build Your Wealth",
    description: "Buy assets, save money, and manage your finances wisely to win the game.",
    image: "📈"
  },
  {
    title: "Compete & Learn",
    description: "Play with friends or AI opponents. Track your progress and climb the leaderboard!",
    image: "🎯"
  }
];

const PROFESSIONS = [
  { value: "teacher_highschool", label: "High School Teacher" },
  { value: "teacher_campus", label: "Campus Teacher" },
  { value: "teacher_professor", label: "Professor" },
  { value: "writer_poet", label: "Poet" },
  { value: "writer_novelist", label: "Novelist" },
  { value: "doctor", label: "Doctor" },
  { value: "engineer", label: "Engineer" },
  { value: "artist_painter", label: "Painter" },
  { value: "artist_musician", label: "Musician" },
  { value: "artist_designer", label: "Designer" },
  { value: "athlete_footballer", label: "Footballer" },
  { value: "athlete_runner", label: "Runner" },
  { value: "entrepreneur", label: "Entrepreneur" }
];

export default function Onboarding() {
  const [slideIndex, setSlideIndex] = useState(0);
  const [authTab, setAuthTab] = useState<'register'|'login'>('register');
  const [showSignup, setShowSignup] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [profession, setProfession] = useState("");
  const navigate = useNavigate();
  const { toast } = useToast();
  const { register, login, loading, error } = useAuth();

  const handleNext = () => {
    if (slideIndex < TUTORIAL_SLIDES.length - 1) {
      setSlideIndex(slideIndex + 1);
    } else {
      setShowSignup(true);
    }
  };

  const handlePrev = () => {
    if (slideIndex > 0) {
      setSlideIndex(slideIndex - 1);
    }
  };

  const handleSignup = async () => {
    if (!username || !email || !password || !profession) {
      toast({
        title: "Missing information",
        description: "Please fill in all fields",
        variant: "destructive"
      });
      return;
    }

    try {
      await register(username, password, email, profession);
      // Optionally call backend.users/create if needed, but /auth/register already creates a profile
      navigate("/lobby");
    } catch (err: any) {
      console.error(err);
      toast({
        title: "Error",
        description: err?.message || "Failed to create account",
        variant: "destructive"
      });
    }
  };

  const handleLogin = async () => {
    if (!username || !password) {
      toast({ title: "Missing information", description: "Enter username and password", variant: "destructive" });
      return;
    }
    try {
      await login(username, password);
      navigate("/lobby");
    } catch (err: any) {
      toast({ title: "Login failed", description: err?.message || "Invalid credentials", variant: "destructive" });
    }
  };

  if (showSignup) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-semibold text-foreground">Welcome to PesaMali</h1>
            <p className="text-sm text-muted-foreground">Create your financial journey or sign in</p>
          </div>
          <div className="bg-[#0F1724] rounded-2xl p-4 border border-[#2A3342]">
            <div className="flex gap-2 mb-4">
              <button className={`px-3 py-2 rounded ${authTab==='register'?'bg-blue-600':''}`} onClick={()=>setAuthTab('register')}>Register</button>
              <button className={`px-3 py-2 rounded ${authTab==='login'?'bg-blue-600':''}`} onClick={()=>setAuthTab('login')}>Login</button>
            </div>

            {authTab==='register' ? (
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Your Name</label>
                  <Input placeholder="Enter your name" value={username} onChange={(e)=>setUsername(e.target.value)} className="bg-[#1A2332] border-[#2A3342] text-white placeholder:text-[#8891a9]" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Email</label>
                  <Input type="email" placeholder="Enter your email" value={email} onChange={(e)=>setEmail(e.target.value)} className="bg-[#1A2332] border-[#2A3342] text-white placeholder:text-[#8891a9]" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Password</label>
                  <Input type="password" placeholder="Create a password" value={password} onChange={(e)=>setPassword(e.target.value)} className="bg-[#1A2332] border-[#2A3342] text-white placeholder:text-[#8891a9]" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Profession</label>
                  <Select value={profession} onValueChange={setProfession}>
                    <SelectTrigger className="bg-[#1A2332] border-[#2A3342] text-white">
                      <SelectValue placeholder="Select your profession" />
                    </SelectTrigger>
                    <SelectContent>
                      {PROFESSIONS.map((p) => (
                        <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button disabled={loading} onClick={handleSignup} className="w-full bg-[#0E6FFF] hover:bg-[#0D5FE5]">
                  {loading ? 'Creating account...' : 'Start Playing'}
                </Button>
                {error && <div className="text-red-400 text-sm">{error}</div>}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Username</label>
                  <Input placeholder="Enter your username" value={username} onChange={(e)=>setUsername(e.target.value)} className="bg-[#1A2332] border-[#2A3342] text-white placeholder:text-[#8891a9]" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-foreground">Password</label>
                  <Input type="password" placeholder="Your password" value={password} onChange={(e)=>setPassword(e.target.value)} className="bg-[#1A2332] border-[#2A3342] text-white placeholder:text-[#8891a9]" />
                </div>
                <Button disabled={loading} onClick={handleLogin} className="w-full bg-[#0E6FFF] hover:bg-[#0D5FE5]">
                  {loading ? 'Signing in...' : 'Sign In'}
                </Button>
                {error && <div className="text-red-400 text-sm">{error}</div>}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center space-y-8 mb-12">
          <div className="text-8xl">{TUTORIAL_SLIDES[slideIndex].image}</div>
          <div className="space-y-3">
            <h2 className="text-2xl font-semibold text-foreground">
              {TUTORIAL_SLIDES[slideIndex].title}
            </h2>
            <p className="text-muted-foreground">
              {TUTORIAL_SLIDES[slideIndex].description}
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-8">
          <Button
            variant="ghost"
            size="icon"
            onClick={handlePrev}
            disabled={slideIndex === 0}
            className="text-foreground"
          >
            <ChevronLeft className="h-6 w-6" />
          </Button>

          <div className="flex gap-2">
            {TUTORIAL_SLIDES.map((_, idx) => (
              <div
                key={idx}
                className={`h-2 rounded-full transition-all ${
                  idx === slideIndex 
                    ? "w-8 bg-[#0E6FFF]" 
                    : "w-2 bg-[#2A3342]"
                }`}
              />
            ))}
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={handleNext}
            className="text-foreground"
          >
            <ChevronRight className="h-6 w-6" />
          </Button>
        </div>

        <Button 
          onClick={handleNext}
          className="w-full bg-[#0E6FFF] hover:bg-[#0D5FE5]"
        >
          {slideIndex === TUTORIAL_SLIDES.length - 1 ? "Get Started" : "Continue"}
        </Button>
      </div>
    </div>
  );
}
