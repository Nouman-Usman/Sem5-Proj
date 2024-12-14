import React, { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MessageSquare, Users, Info, Sparkles } from "lucide-react"

export function UserHome() {
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [delta, setDelta] = useState(200);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user'));
    const userName = user?.name || 'User';
    setDisplayText(userName.charAt(0));
  }, []);

  useEffect(() => {
    let ticker = setInterval(() => {
      tick();
    }, delta);

    return () => clearInterval(ticker);
  }, [displayText, isDeleting]);

  const tick = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const fullName = user?.name || 'User';
    
    if (isDeleting) {
      setDisplayText(fullName.substring(0, displayText.length - 1));
      setDelta(100);
    } else {
      setDisplayText(fullName.substring(0, displayText.length + 1));
      setDelta(200);
    }

    if (!isDeleting && displayText === fullName) {
      setTimeout(() => setIsDeleting(true), 2000);
    } else if (isDeleting && displayText === '') {
      setIsDeleting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030614] pt-24 pb-8 px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px] animate-fadeInSlow"></div>
        <div className="absolute top-1/4 right-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px] animate-fadeInSlow delay-300"></div>
        <div className="absolute bottom-1/4 left-1/2 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px] animate-fadeInSlow delay-500"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Welcome Header */}
        <div className="mb-12 animate-fadeIn">
          <h1 className="text-4xl font-bold text-white mb-2">
            Welcome, {' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 typewriter">
              {displayText}
            </span>
          </h1>
          <p className="text-gray-400">Your AI-powered legal assistant</p>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Chat to AI Now Section */}
          <Card className="bg-[#1A1A2E]/95 border-[#9333EA]/20 hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300 backdrop-blur-sm animate-slideInLeft">
            <CardHeader>
              <CardTitle className="text-white flex items-center">
                <Sparkles className="mr-2 h-5 w-5 text-[#9333EA]" />
                Chat to AI Now
              </CardTitle>
              <CardDescription className="text-gray-400">Get instant legal advice from our AI assistant</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 mb-6">Our AI is ready to assist you with any legal questions or concerns you may have.</p>
              <a href="/chatbot">
                <Button className="w-full bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 transition-all duration-300">
                  <MessageSquare className="mr-2 h-4 w-4" /> Start AI Chat
                </Button>
              </a>
            </CardContent>
          </Card>

          {/* Talk to Our Best Lawyers Section */}
          <Card className="bg-[#1A1A2E]/95 border-[#9333EA]/20 hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300 backdrop-blur-sm animate-slideInRight">
            <CardHeader>
              <CardTitle className="text-white">Talk to Our Best Lawyers</CardTitle>
              <CardDescription className="text-gray-400">Connect with experienced legal professionals</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 mb-6">Need personalized advice? Consult with our top-rated lawyers.</p>
              <a href="/Lawyers">
                <Button className="w-full bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 transition-all duration-300">
                  <Users className="mr-2 h-4 w-4" /> Explore Our Lawyers
                </Button>
              </a>
            </CardContent>
          </Card>

          {/* What's New Section */}
          <Card className="bg-[#1A1A2E]/95 border-[#9333EA]/20 hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300 backdrop-blur-sm animate-slideInUp delay-300">
            <CardHeader>
              <CardTitle className="text-white">What's New</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-[#9333EA] rounded-full mr-3 animate-pulse"></div>
                  New AI model for more accurate legal advice
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-[#9333EA] rounded-full mr-3 animate-pulse"></div>
                  Expanded database of legal precedents
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-[#9333EA] rounded-full mr-3 animate-pulse"></div>
                  Improved user interface for easier navigation
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-[#9333EA] rounded-full mr-3 animate-pulse"></div>
                  Added support for multiple languages
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* What is AI Section */}
          <Card className="bg-[#1A1A2E]/95 border-[#9333EA]/20 hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300 backdrop-blur-sm animate-slideInUp delay-400">
            <CardHeader>
              <CardTitle className="text-white">What is AI?</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 mb-4">
                Artificial Intelligence (AI) in legal tech refers to advanced computer systems that can perform tasks 
                typically requiring human intelligence. Our AI can analyze legal documents, provide quick answers to 
                common legal questions, and even predict case outcomes based on historical data.
              </p>
              <p className="text-gray-300 mb-6">
                While AI is a powerful tool, it complements human expertise rather than replacing it, allowing 
                lawyers to focus on complex aspects of legal practice.
              </p>
              <a href="/about">
                <Button variant="outline" className="w-full border-[#9333EA] text-[#9333EA] hover:bg-[#9333EA] hover:text-white transition-all duration-300">
                  <Info className="mr-2 h-4 w-4" /> Learn More About AI in Law
                </Button>
              </a>
            </CardContent>
          </Card>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideInLeft {
          from { opacity: 0; transform: translateX(-50px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(50px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes slideInUp {
          from { opacity: 0; transform: translateY(50px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out forwards;
        }

        .animate-slideInLeft {
          animation: slideInLeft 0.6s ease-out forwards;
        }

        .animate-slideInRight {
          animation: slideInRight 0.6s ease-out forwards;
        }

        .animate-slideInUp {
          animation: slideInUp 0.6s ease-out forwards;
        }

        .delay-300 {
          animation-delay: 300ms;
        }

        .delay-400 {
          animation-delay: 400ms;
        }

        .typewriter {
          display: inline-block;
          border-right: 4px solid #9333EA;
          animation: blink 0.75s step-end infinite;
          padding-right: 4px;
        }

        @keyframes blink {
          from, to { border-color: transparent }
          50% { border-color: #9333EA }
        }
      `}</style>
    </div>
  );
}