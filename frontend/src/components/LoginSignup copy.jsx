import React, { useState, useEffect } from "react"
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function LoginSignup() {
  const [showPassword, setShowPassword] = useState(false)
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("client");
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }
  const [authenticatedRole, setAuthenticatedRole] = useState(null);


  const handleSignup = async () => {
    const data = { name, email, password, role };

    try {
      const response = await fetch("http://127.0.0.1:5000/api/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Signup failed");
      }

      alert("Signup successful");
    } catch (error) {
      console.error("Signup error", error.message);
      alert("Signup failed: " + error.message);
    }
  };

  // Login handler
  const handleLogin = async () => {
    const data = { email, password };

    try {
      const response = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Login failed");
      }

      const responseData = await response.json();
      const { access_token } = responseData;

      // Store JWT token in localStorage
      localStorage.setItem("access_token", access_token);
      alert("Login successful");
    } catch (error) {
      console.error("Login error", error.message);
      alert("Login failed: " + error.message);
    }
  };

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.log("No token found, please log in.");
        return;
      }
      try {
        const response = await fetch("http://127.0.0.1:5000/api/verify-token", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}` // Send the token as a Bearer token in the header
          }
        });

        const data = await response.json();  // Make sure to extract the JSON response
        if (response.ok && data.role === 'lawyer') {
          setAuthenticatedRole("lawyer");
        } else if (response.ok && data.role === 'customer') {
          setAuthenticatedRole("customer");
        } else {
          console.log("Access denied, role not authorized.");
        }
      } catch (error) {
        console.log(error.message);
      }
    };

    verifyToken();
  }, []);




  if (authenticatedRole === "customer") {
    return <Redirect to="/user-home" />;
  }
  else if (authenticatedRole === "lawyer") {
    return <Redirect to="/lawyers" />
  }

  return (
    (<div
      className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-center">Welcome to Apna Waqeel</CardTitle>
          <CardDescription className="text-center">Your AI Lawyer Assistant</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <form onSubmit={(e) => e.preventDefault()}>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <div className="relative">
                      <Mail
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="Enter your email"
                        className="pl-10"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Lock
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        className="pl-10 pr-10"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required />
                      <button
                        type="button"
                        onClick={togglePasswordVisibility}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        {showPassword ? (
                          <EyeOff className="h-5 w-5 text-gray-400" />
                        ) : (
                          <Eye className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  <Button type="submit" className="w-full" onClick={handleLogin}>Login</Button>
                </div>
              </form>
            </TabsContent>
            <TabsContent value="signup">
              <form onSubmit={(e) => e.preventDefault()}>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <div className="relative">
                      <User
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        id="name"
                        type="text"
                        placeholder="Enter your full name"
                        className="pl-10"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-email">Email</Label>
                    <div className="relative">
                      <Mail
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        id="signup-email"
                        type="email"
                        placeholder="Enter your email"
                        className="pl-10"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">Password</Label>
                    <div className="relative">
                      <Lock
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        id="signup-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Create a password"
                        className="pl-10 pr-10"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required />
                      <button
                        type="button"
                        onClick={togglePasswordVisibility}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        {showPassword ? (
                          <EyeOff className="h-5 w-5 text-gray-400" />
                        ) : (
                          <Eye className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="signup-password">I am a </Label>
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
                          onChange={() => setRole('client')}
                        />
                        <label className="form-check-label" htmlFor="client">
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
                          onChange={() => setRole('lawyer')}
                        />
                        <label className="form-check-label" htmlFor="lawyer">
                          Lawyer
                        </label>
                      </div>
                    </div>
                  </div>
                  <Button type="submit" className="w-full" onClick={handleSignup}>Sign Up</Button>
                </div>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="text-center text-sm text-gray-600">
          By continuing, you agree to Apna Waqeel's Terms of Service and Privacy Policy.
        </CardFooter>
      </Card>
    </div>)
  );
}