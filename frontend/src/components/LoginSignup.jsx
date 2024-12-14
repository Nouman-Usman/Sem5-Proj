import React, { useState, useEffect } from "react"
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { authService } from "@/services/auth"
import apiService from "@/services/api"


export function LoginSignup() {
  const [showPassword, setShowPassword] = useState(false)
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("client");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentView, setCurrentView] = useState("login")

  const [displayText, setDisplayText] = useState("Waqeel");
  const [isDeleting, setIsDeleting] = useState(false);
  const [loopNum, setLoopNum] = useState(0);
  const [delta, setDelta] = useState(200);

  useEffect(()=>{

    const init = async()=>{
      const user = JSON.parse(localStorage.getItem("user"));
      if (user == null){
        return;
      }
      if (user.role == 'client') {
        window.location.href = '/user-home';
      }
      else {
        window.location.href = '/lawyer-dashboard';
      }
    }
    init();
  }, [])

  useEffect(() => {
    let ticker = setInterval(() => {
      tick();
    }, delta);

    return () => clearInterval(ticker);
  }, [displayText, isDeleting]);

  const tick = () => {
    const fullText = "Waqeel";
    
    if (isDeleting) {
      setDisplayText(fullText.substring(0, displayText.length - 1));
      setDelta(100);
    } else {
      setDisplayText(fullText.substring(0, displayText.length + 1));
      setDelta(200);
    }

    if (!isDeleting && displayText === fullText) {
      setTimeout(() => setIsDeleting(true), 2000);
    } else if (isDeleting && displayText === '') {
      setIsDeleting(false);
      setLoopNum(loopNum + 1);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await authService.login(email, password);
      const currentRole = apiService.getUserRole();
      if (currentRole.role == 'client') {
        window.location.href = '/user-home';
      }
      else {
        window.location.href = '/lawyer-dashboard';
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      setError("SignUp..");
      await authService.signup(name, email, password, role);
      // Auto login after successful signup
      // await authService.login(email, password);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-[#030614] py-12 px-4 sm:px-6 lg:px-8 overflow-hidden">
      {/* Add purple luminous background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px]"></div>
        <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px]"></div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes slideRight {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes slideLeft {
          from {
            opacity: 0;
            transform: translateX(20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .typewriter {
          display: inline-block;
          border-right: 4px solid #9333EA;
          animation: blink 0.75s step-end infinite;
        }

        @keyframes blink {
          from, to { border-color: transparent }
          50% { border-color: #9333EA }
        }

        .form-container {
          position: relative;
        }

        .form-content {
          position: absolute;
          width: 100%;
          opacity: 0;
          visibility: hidden;
          transition: opacity 0.3s ease-in-out, visibility 0.3s ease-in-out;
        }

        .form-content.active {
          opacity: 1;
          visibility: visible;
          position: relative;
        }
      `}</style>

      {/* Add relative positioning to ensure content stays above the background effects */}
      <div className="w-full max-w-7xl flex items-center gap-12 relative z-10">
        {/* Left side - Animated Text */}
        <div className="flex-1 hidden lg:block">
          <div className="space-y-6 animate-[fadeIn_0.6s_ease-out]">
            <h1 className="text-6xl font-bold text-white leading-tight">
              Welcome to Apna{' '}
              <span className="text-[#9333EA] typewriter">{displayText}</span>
            </h1>
            <p className="text-2xl text-[#DAE0E6]">
              Your AI Lawyer Assistant
            </p>
            <p className="text-lg text-[#DAE0E6]/80 max-w-xl">
              Experience professional legal assistance powered by cutting-edge AI technology. 
              Get instant legal advice and connect with experienced lawyers.
            </p>
          </div>
        </div>

        {/* Right side - Login/Signup Form */}
        <div className="flex-1">
          <Card className="w-full max-w-md bg-[#030614]/80 border border-[rgba(255,255,255,0.06)] backdrop-blur-lg 
            animate-[fadeIn_0.6s_ease-out]
            shadow-[0_0_25px_rgba(147,51,234,0.3)]
            hover:shadow-[0_0_30px_rgba(147,51,234,0.5)] 
            transition-all duration-300 
            bg-gradient-to-b from-[rgba(147,51,234,0.1)] to-transparent">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-center text-white">Apna Waqeel</CardTitle>
              
            </CardHeader>
            <CardContent>
              {error && (
                <div className="mb-4 p-2 text-sm text-red-400 bg-red-900/20 rounded border border-red-800">
                  {error}
                </div>
              )}
              
              <div className="flex mb-6 bg-[#030614] border border-[rgba(255,255,255,0.06)] rounded-lg p-1">
                <button
                  type="button"
                  onClick={() => setCurrentView("login")}
                  className={`flex-1 py-2 text-center rounded-md transition-all duration-300 ${
                    currentView === "login" 
                      ? 'bg-gradient-to-b from-[#9333EA] to-[#7E22CE] text-white' 
                      : 'text-[#DAE0E6]'
                  }`}
                >
                  Login
                </button>
                <button
                  type="button"
                  onClick={() => setCurrentView("signup")}
                  className={`flex-1 py-2 text-center rounded-md transition-all duration-300 ${
                    currentView === "signup" 
                      ? 'bg-gradient-to-b from-[#9333EA] to-[#7E22CE] text-white' 
                      : 'text-[#DAE0E6]'
                  }`}
                >
                  Sign Up
                </button>
              </div>

              <div className="form-container">
                <div className={`form-content ${currentView === "login" ? "active" : ""}`}>
                  <form onSubmit={handleLogin}>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-[#DAE0E6]">Email</Label>
                        <div className="relative">
                          <Mail
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#9333EA] z-10"
                            size={20} // Use size prop instead of height/width
                          />
                          <Input
                            id="email"
                            type="email"
                            placeholder="Enter your email"
                            className="pl-10 bg-[#030614] border-[rgba(255,255,255,0.06)] text-white 
                              placeholder:text-gray-400 focus:border-[#9333EA] focus:ring-[#9333EA]
                              transition-all duration-300 hover:border-[#9333EA]/50
                              transform-gpu focus:scale-[1.02]"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="password" className="text-[#DAE0E6]">Password</Label>
                        <div className="relative">
                          <Lock
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#9333EA] z-10"
                            size={20} // Use size prop instead of height/width
                          />
                          <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="Enter your password"
                            className="pl-10 pr-10 bg-[#030614] border-[rgba(255,255,255,0.06)] text-white 
                              placeholder:text-gray-400 focus:border-[#9333EA] focus:ring-[#9333EA]
                              transition-all duration-300 hover:border-[#9333EA]/50
                              transform-gpu focus:scale-[1.02]"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required />
                          <button
                            type="button"
                            onClick={togglePasswordVisibility}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2">
                            {showPassword ? (
                              <EyeOff className="h-5 w-5 text-[#9333EA]" />
                            ) : (
                              <Eye className="h-5 w-5 text-[#9333EA]" />
                            )}
                          </button>
                        </div>
                      </div>
                      <Button 
                        type="submit" 
                        className="w-full bg-gradient-to-b from-[#9333EA] to-[#7E22CE] 
                          transition-all duration-300 
                          hover:opacity-90 hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(147,51,234,0.5)]
                          active:scale-[0.98]"
                        disabled={loading}
                      >
                        {loading ? "Logging in..." : "Login"}
                      </Button>
                    </div>
                  </form>
                </div>
                
                <div className={`form-content ${currentView === "signup" ? "active" : ""}`}>
                  <form onSubmit={handleSignup}>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="name" className="text-[#DAE0E6]">Full Name</Label>
                        <div className="relative">
                          <User
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#9333EA] z-10"
                            size={20} // Use size prop instead of height/width
                          />
                          <Input
                            id="name"
                            type="text"
                            placeholder="Enter your full name"
                            className="pl-10 bg-[#030614] border-[rgba(255,255,255,0.06)] text-white 
                              placeholder:text-gray-400 focus:border-[#9333EA] focus:ring-[#9333EA]
                              transition-all duration-300 hover:border-[#9333EA]/50
                              transform-gpu focus:scale-[1.02]"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="signup-email" className="text-[#DAE0E6]">Email</Label>
                        <div className="relative">
                          <Mail
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#9333EA] z-10"
                            size={20} // Use size prop instead of height/width
                          />
                          <Input
                            id="signup-email"
                            type="email"
                            placeholder="Enter your email"
                            className="pl-10 bg-[#030614] border-[rgba(255,255,255,0.06)] text-white 
                              placeholder:text-gray-400 focus:border-[#9333EA] focus:ring-[#9333EA]
                              transition-all duration-300 hover:border-[#9333EA]/50
                              transform-gpu focus:scale-[1.02]"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="signup-password" className="text-[#DAE0E6]">Password</Label>
                        <div className="relative">
                          <Lock
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#9333EA] z-10"
                            size={20} // Use size prop instead of height/width
                          />
                          <Input
                            id="signup-password"
                            type={showPassword ? "text" : "password"}
                            placeholder="Create a password"
                            className="pl-10 pr-10 bg-[#030614] border-[rgba(255,255,255,0.06)] text-white 
                              placeholder:text-gray-400 focus:border-[#9333EA] focus:ring-[#9333EA]
                              transition-all duration-300 hover:border-[#9333EA]/50
                              transform-gpu focus:scale-[1.02]"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required />
                          <button
                            type="button"
                            onClick={togglePasswordVisibility}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2">
                            {showPassword ? (
                              <EyeOff className="h-5 w-5 text-[#9333EA]" />
                            ) : (
                              <Eye className="h-5 w-5 text-[#9333EA]" />
                            )}
                          </button>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="signup-password" className="text-[#DAE0E6]">I am a </Label>
                        <div className="flex justify-around gap-5 pl-10 pr-10 border border-neutral-200 rounded-md" style={{ padding: "4px" }}>
                          <div className="form-check">
                            <input
                              className="form-check-input"
                              style={{ marginRight: "4px" }}
                              type="radio"
                              name="role"
                              id="client"
                              value="client"
                            checked={role === 'client'}
                            onClick={()=>setRole('client')}
                            />
                            <label className="form-check-label text-[#DAE0E6]" htmlFor="client">
                              Client
                            </label>
                          </div>
                          <div className="form-check">
                            <input
                              className="form-check-input"
                              type="radio"
                              style={{ marginRight: "4px" }}
                              name="role"
                              id="lawyer"
                              value="lawyer"
                            checked={role === 'lawyer'}
                            onClick={()=>setRole('lawyer')}
                            />
                            <label className="form-check-label text-[#DAE0E6]" htmlFor="lawyer">
                              Lawyer
                            </label>
                          </div>
                        </div>
                      </div>
                      <Button 
                        type="submit" 
                        className="w-full bg-gradient-to-b from-[#9333EA] to-[#7E22CE] 
                          transition-all duration-300 
                          hover:opacity-90 hover:scale-[1.02] hover:shadow-[0_0_20px_rgba(147,51,234,0.5)]
                          active:scale-[0.98]"
                        disabled={loading}
                      >
                        {loading ? "Signing up..." : "Sign Up"}
                      </Button>
                    </div>
                  </form>
                </div>
              </div>
            </CardContent>
            <CardFooter 
              className="text-center text-sm text-[rgba(255,255,255,0.8)]
                animate-[fadeIn_0.8s_ease-out]">
              By continuing, you agree to Apna Waqeel's Terms of Service and Privacy Policy.
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
}