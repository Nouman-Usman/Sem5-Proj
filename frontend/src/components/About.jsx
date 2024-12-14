import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function About() {
  const [displayText, setDisplayText] = useState("Waqeel");
  const [isDeleting, setIsDeleting] = useState(false);
  const [loopNum, setLoopNum] = useState(0);
  const [delta, setDelta] = useState(200);

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

        .typewriter {
          display: inline-block;
          border-right: 4px solid #9333EA;
          animation: blink 0.75s step-end infinite;
        }

        @keyframes blink {
          from, to { border-color: transparent }
          50% { border-color: #9333EA }
        }
      `}</style>

      {/* Add relative positioning to ensure content stays above the background effects */}
      <div className="w-full max-w-7xl flex items-center gap-12 relative z-10">
        {/* Left side - Animated Text */}
        <div className="flex-1 hidden lg:block">
          <div className="space-y-6 animate-[fadeIn_0.6s_ease-out]">
            <h1 className="text-6xl font-bold text-white leading-tight">
              About Apna{' '}
              <span className="text-[#9333EA] typewriter">{displayText}</span>
            </h1>
            <p className="text-2xl text-[#DAE0E6]">
              Your AI Lawyer Assistant
            </p>
            <p className="text-lg text-[#DAE0E6]/80 max-w-xl">
              Apna Waqeel is a platform that leverages AI technology to provide instant legal advice and connect users with experienced lawyers.
            </p>
          </div>
        </div>

        {/* Right side - About Content */}
        <div className="flex-1">
          <Card className="w-full max-w-md bg-[#030614]/80 border border-[rgba(255,255,255,0.06)] backdrop-blur-lg 
            animate-[fadeIn_0.6s_ease-out]
            shadow-[0_0_25px_rgba(147,51,234,0.3)]
            hover:shadow-[0_0_30px_rgba(147,51,234,0.5)] 
            transition-all duration-300 
            bg-gradient-to-b from-[rgba(147,51,234,0.1)] to-transparent">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-center text-white">About Us</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-[#DAE0E6]">
                Apna Waqeel is dedicated to making legal assistance accessible and efficient. Our AI-powered platform provides users with instant legal advice and connects them with experienced lawyers for further consultation.
              </p>
              <p className="text-[#DAE0E6] mt-4">
                Our mission is to bridge the gap between legal professionals and those in need of legal assistance, ensuring that everyone has access to the legal help they deserve.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default About;
