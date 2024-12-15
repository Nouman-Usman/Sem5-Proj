import React, { useState, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2, Send, User, Bot, ChevronLeft, ChevronRight, Star, History, Plus, LogOut, Settings, Star as StarIcon } from "lucide-react";
import apiService from "@/services/api";
import { useNavigate } from "react-router-dom";
import PerfectScrollbar from 'react-perfect-scrollbar';
import 'react-perfect-scrollbar/dist/css/styles.css';
import Logo from "@/assets/Main logo.svg";

const LawyerCard = ({ lawyer, onContact }) => (
  <Card className="mt-2 p-4 bg-[#1A1A2E]/90 border border-[#9333EA]/20 backdrop-blur-lg shadow-[0_0_15px_rgba(147,51,234,0.2)] hover:shadow-[0_0_30px_rgba(147,51,234,0.3)] transition-all duration-300">
    <div className="flex items-center">
      <Avatar className="h-12 w-12 mr-4 ring-2 ring-[#9333EA]/50">
        <AvatarImage src={lawyer.avatar} alt={lawyer.name} />
        <AvatarFallback className="bg-[#2E2E3A] text-white">{lawyer.name.split("").map(n => n[0]).join("")}</AvatarFallback>
      </Avatar>
      <div>
        <h3 className="font-bold text-lg text-white">{lawyer.name}</h3>
        <p className="text-sm text-gray-400">{lawyer.specialization}</p>
        <div className="flex items-center mt-1">
          <Star className="h-4 w-4 text-yellow-400 fill-current" />
          <span className="ml-1 text-sm text-gray-400">{lawyer.rating} ({lawyer.reviewCount} reviews)</span>
        </div>
      </div>
    </div>
    <p className="mt-2 text-sm text-gray-300">{lawyer.description}</p>
    <Button 
      className="mt-2 w-full bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 transition-opacity"
      onClick={() => onContact(lawyer)}
    >
      Contact {lawyer.name}
    </Button>
  </Card>
);

export function ChatbotPage() {
  const navigate = useNavigate();

  const [messages, setMessages] = useState([
    { id: 1, text: "", sender: "ai" } // Start with empty text
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [processing, setProcessing] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessionHistory, setSessionHistory] = useState([]);
  const messagesEndRef = useRef(null);
  const [error, setError] = useState(null);
  const [references, setReferences] = useState([]);
  const [showContactPopup, setShowContactPopup] = useState(false);
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const [contactMessage, setContactMessage] = useState("");
  const [typingText, setTypingText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchChatTopics = async () => {
      const chatTopics = await apiService.getChatTopic();
      if (chatTopics) {
        setSessionHistory(chatTopics.topic.map((topic, index) => ({
          id: chatTopics.session_id[index],
          title: topic,
          date: chatTopics.time[index]
        })));
      }
    };

    fetchChatTopics();
    const intervalId = setInterval(fetchChatTopics, 5000);

    return () => clearInterval(intervalId);
  }, []);

  const simulateResponse = async (text) => {
    setIsTyping(true);
    // Add a small delay before showing the message
    await new Promise(resolve => setTimeout(resolve, 500));
    setIsTyping(false);
    return text;
  };

  useEffect(() => {
    const initialMessage = "Hello! How can I assist you with your legal questions today?";
    simulateResponse(initialMessage).then(text => {
      setMessages([{ id: 1, text, sender: "ai" }]);
    });
  }, []); // Run once on component mount

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (inputMessage.trim() === "") return;

    const newUserMessage = { id: messages.length + 1, text: inputMessage, sender: "user" };
    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage("");
    setProcessing("thinking");
    setError(null);

    try {
      const currentCredits = await apiService.getUserCredits();
      if (currentCredits === 0) {
        if (apiService.getUserRole() === 'lawyer') {
          navigate("/lawyer-subscription");
        } else {
          navigate("/subscription-plans");
        }
        return;
      }

      const response = await apiService.askQuestion(inputMessage);

      if (!response) {
        throw new Error('Empty response received');
      }

      await apiService.updateCredits(currentCredits - 1);

      // Show the AI response immediately with pop animation
      const aiResponse = {
        id: messages.length + 2,
        text: response.answer,
        sender: "ai",
        lawyers: response.recommendedLawyers
      };

      await simulateResponse(response.answer);
      setMessages(prev => [...prev, aiResponse]);
      setReferences(response.references || []);

    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, there was an error processing your request. Please try again.",
        sender: "ai"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setProcessing(null);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleContact = (lawyer) => {
    setSelectedLawyer(lawyer);
    setShowContactPopup(true);
  };

  const handleSendContactMessage = async () => {
    if (contactMessage.trim() === "") return;

    try {
      await apiService.startChat(selectedLawyer.id);
      await apiService.sendMessage(selectedLawyer.id, contactMessage);
      setContactMessage("");
      setShowContactPopup(false);
    } catch (error) {
      console.error("Failed to send message:", error.message);
    }
  };

  const loadPreviousSession = async (session) => {
    const prevChat = await apiService.getChatsFromSessionId(session.id);
    if (prevChat == null) {
      setMessages([]);
      return;
    };
    const newChats = [];
    prevChat.data.data.forEach((chat) => {
      newChats.push({
        id: chat.message_id,
        text: chat.message,
        sender: chat.message_type === "AI Message" ? "ai" : "user",
      });
    });
    setMessages(newChats);
  }

  const handleGoPremium = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user.role === 'lawyer') {
      navigate('/lawyer-subscription');
    } else if (user.role === 'client') {
      navigate('/subscription-plans');
    }
  };

  const handleLogout = () => {
    apiService.logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#030614]">
      {/* Sidebar with toggle button inside */}
      <div className={`bg-[#1A1A2E]/90 backdrop-blur-lg border-r border-[#9333EA]/20 
        ${isSidebarOpen ? "w-64" : "w-20"} 
        transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0 relative`}
      >
        <div className="h-full flex flex-col">
          {/* First section for toggle button and New Chat button */}
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <Button 
                type="button" 
                onClick={toggleSidebar} 
                variant="outline" 
                size="icon"
                className="border-[#9333EA]/20 text-purple-400 hover:text-purple-300 hover:bg-white/5 group"
              >
                <ChevronLeft className="h-4 w-4 transition-colors" />
              </Button>
            </div>
            <div className="flex items-center border-[#9333EA]/20 text-purple-400
              hover:text-purple-300 hover:bg-white/5 bg-[#1A1A2E]/90 backdrop-blur-lg
              animate-fadeIn hover:scale-110 transition-all duration-200
              shadow-[0_0_15px_rgba(147,51,234,0.2)] group rounded-full p-2"
            >
              <Plus className="h-4 w-4 transition-colors" />
              {isSidebarOpen && <span className="ml-2 text-white">New Chat</span>}
            </div>
          </div>

          {/* Second section for recent chats */}
          <div className="flex-1 p-4 overflow-hidden flex flex-col">
            <h3 className="text-white/90 mb-2 sticky top-0 bg-[#1A1A2E]/90 z-10">
              {isSidebarOpen && "Recent"}
            </h3>
            <div className="flex-1 overflow-y-hidden">
              <PerfectScrollbar
                options={{
                  suppressScrollX: true,
                  wheelPropagation: true
                }}
                className="h-full pr-2"
              >
                <div className="space-y-2">
                  {sessionHistory.map((session) => (
                    <div
                      key={session.id}
                      onClick={() => loadPreviousSession(session)}
                      className="p-2 hover:bg-white/5 rounded-lg cursor-pointer border border-transparent 
                        hover:border-[#9333EA]/20 transition-all duration-300"
                    >
                      <h3 className="font-medium text-white/90 truncate">
                        {isSidebarOpen && session.title}
                      </h3>
                      <p className="text-sm text-gray-400 truncate">
                        {isSidebarOpen && session.date}
                      </p>
                    </div>
                  ))}
                </div>
              </PerfectScrollbar>
            </div>
          </div>

          {/* Third section for fixed navigation items */}
          <div className="p-4 border-t border-[#9333EA]/20">
            <div className="space-y-4">
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={() => navigate('/lawyer-dashboard')}
              >
                <User className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Dashboard"}
              </Button>
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={handleGoPremium}  // Updated onClick handler
              >
                <StarIcon className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Go Premium"}
              </Button>
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={() => navigate('/account-settings')}
              >
                <Settings className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Account Settings"}
              </Button>
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={handleLogout}  // Updated onClick handler
              >
                <LogOut className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Logout"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Fixed Header */}
        <header className="flex-shrink-0 h-16 flex items-center justify-center bg-[#1A1A2E]/90 border-b border-[#9333EA]/20">
          <img src={Logo} alt="Logo" className="h-10" />
        </header>

        {/* Chat Container */}
        <div className="flex-1 flex flex-col min-h-0 relative">
          {/* Background Effects */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
            <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px]"></div>
            <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px]"></div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 min-h-0 relative">
            <PerfectScrollbar
              options={{
                suppressScrollX: true,
                wheelPropagation: true
              }}
              className="absolute inset-0"
            >
              <div className="max-w-4xl mx-auto p-4">
                {error && (
                  <div className="bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4">
                    {error}
                  </div>
                )}

                <div className="space-y-4">
                  {messages.map((message) => (
                    <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"} mb-4`}>
                      <div className={`max-w-[70%] rounded-lg p-3 ${
                        message.sender === "user" 
                          ? "bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white" 
                          : "bg-[#2E2E3A] text-gray-200"
                      } shadow-[0_0_15px_rgba(147,51,234,0.2)] animate-pop`}>
                        <div className="flex items-start">
                          {message.sender === "user" ? (
                            <User className="h-5 w-5 mr-2 mt-1" />
                          ) : (
                            <Bot className="h-5 w-5 mr-2 mt-1" />
                          )}
                          <p>{message.text}</p>
                        </div>
                      </div>
                    </div>
                  ))}

                  {references.length > 0 && (
                    <div className="mt-4 p-3 bg-gray-50 rounded">
                      <h4 className="font-semibold mb-2">References:</h4>
                      <ul className="list-disc pl-5">
                        {references.map((ref, idx) => (
                          <li key={idx} className="text-sm text-blue-600 hover:underline">
                            <a href={ref} target="_blank" rel="noopener noreferrer">{ref}</a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {processing && (
                    <div className="flex justify-start mb-4">
                      <div className="bg-[#2E2E3A] text-gray-200 rounded-lg p-3 shadow-[0_0_15px_rgba(147,51,234,0.2)] animate-message">
                        <div className="flex items-center">
                          <Bot className="h-5 w-5 mr-2" />
                          <Loader2 className="h-5 w-5 animate-spin mr-2" />
                          <p>{processing === "thinking" ? "Thinking..." : "Searching the web..."}</p>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            </PerfectScrollbar>
          </div>

          {/* Fixed Input Area */}
          <div className="flex-shrink-0 bg-[#1A1A2E]/90 border-t border-[#9333EA]/20 p-4">
            <div className="max-w-4xl mx-auto">
              <form onSubmit={handleSendMessage} className="flex gap-2">
                <div className="flex-1 bg-[#2E2E3A] rounded-lg border border-[#9333EA]/20">
                  <Input
                    type="text"
                    placeholder="Type your message here..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    className="w-full bg-transparent text-white placeholder:text-gray-400 focus:outline-none px-4 py-2"
                  />
                </div>
                <Button 
                  type="submit"
                  className="bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 transition-all duration-300 flex items-center px-4"
                >
                  <Send className="h-5 w-5 mr-2" />
                  Send
                </Button>
              </form>
              <div className="text-center text-gray-400 text-sm mt-2">
                Apna Waqeel can make mistakes. Check important info.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Popup */}
      {showContactPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
          <div className="bg-[#1A1A2E]/90 p-6 rounded-lg shadow-[0_0_30px_rgba(147,51,234,0.3)] border border-[#9333EA]/20 w-96 backdrop-blur-lg">
            <h2 className="text-xl font-semibold mb-4 text-white">Contact {selectedLawyer.name}</h2>
            <textarea
              className="w-full p-2 bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg text-white placeholder:text-gray-400 mb-4 focus:ring-[#9333EA] resize-none"
              rows="4"
              placeholder="Type your message here..."
              value={contactMessage}
              onChange={(e) => setContactMessage(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button 
                variant="outline" 
                onClick={() => setShowContactPopup(false)}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSendContactMessage}
                className="bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 transition-opacity"
              >
                Send
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

<style jsx>{`
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: #1A1A2E;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: #9333EA;
    border-radius: 10px;
    border: 2px solid #1A1A2E;
  }

  @keyframes messageIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-message {
    animation: messageIn 0.3s ease-out;
  }

  .typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: currentColor;
    margin-left: 2px;
    animation: blink 1s step-end infinite;
  }

  @keyframes blink {
    50% { opacity: 0; }
  }

  .typing-dots::after {
    content: '';
    animation: dots 1.5s infinite;
    display: inline-block;
    width: 0;
  }

  @keyframes dots {
    0%, 20% { content: ''; }
    40% { content: '.'; }
    60% { content: '..'; }
    80% { content: '...'; }
    100% { content: ''; }
  }

  @keyframes pop {
    0% {
      opacity: 0;
      transform: scale(0.8) translateY(10px);
    }
    50% {
      transform: scale(1.05) translateY(-5px);
    }
    100% {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .animate-pop {
    animation: pop 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
  }

  .input-glow {
    animation: inputGlow 2s ease-in-out infinite;
  }

  @keyframes inputGlow {
    0% {
      box-shadow: 0 0 5px rgba(147,51,234,0.2);
      border-color: rgba(147,51,234,0.2);
    }
    50% {
      box-shadow: 0 0 20px rgba(147,51,234,0.4);
      border-color: rgba(147,51,234,0.6);
    }
    100% {
      box-shadow: 0 0 5px rgba(147,51,234,0.2);
      border-color: rgba(147,51,234,0.2);
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out forwards;
  }

  /* Custom Scrollbar Styling */
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .custom-scrollbar::-webkit-scrollbar-track {
    background: #1A1A2E;
    border-radius: 8px;
    margin: 2px;
  }

  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #9333EA 0%, #7E22CE 100%);
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: padding-box;
    transition: all 0.3s ease;
    box-shadow: 
      0 0 5px rgba(147, 51, 234, 0.3),
      0 0 10px rgba(147, 51, 234, 0.2),
      0 0 15px rgba(147, 51, 234, 0.1);
  }

  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #7E22CE 0%, #9333EA 100%);
    box-shadow: 
      0 0 10px rgba(147, 51, 234, 0.5),
      0 0 20px rgba(147, 51, 234, 0.3),
      0 0 30px rgba(147, 51, 234, 0.2);
  }

  /* Apply custom scrollbar to chat area as well */
  .flex-1.overflow-y-auto {
    scrollbar-width: thin;
    scrollbar-color: #9333EA #1A1A2E;
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar-track {
    background: #1A1A2E;
    border-radius: 8px;
    margin: 2px;
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #9333EA 0%, #7E22CE 100%);
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: padding-box;
    transition: all 0.3s ease;
    box-shadow: 
      0 0 5px rgba(147, 51, 234, 0.3),
      0 0 10px rgba(147, 51, 234, 0.2),
      0 0 15px rgba(147, 51, 234, 0.1);
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #7E22CE 0%, #9333EA 100%);
    box-shadow: 
      0 0 10px rgba(147, 51, 234, 0.5),
      0 0 20px rgba(147, 51, 234, 0.3),
      0 0 30px rgba(147, 51, 234, 0.2);
  }

  /* Custom styles for the main chat area PerfectScrollbar */
  .ps__rail-y {
    background-color: transparent !important;
    width: 10px !important;
    margin-right: 0;
  }

  .ps__rail-y:hover {
    background-color: rgba(147, 51, 234, 0.1) !important;
  }

  .ps__thumb-y {
    background: linear-gradient(180deg, #9333EA 0%, #7E22CE 100%) !important;
    width: 6px !important;
    right: 2px !important;
    border-radius: 10px !important;
  }

  .ps__thumb-y:hover {
    background: linear-gradient(180deg, #7E22CE 0%, #9333EA 100%) !important;
  }

  .ps .ps__rail-y.ps--clicking,
  .ps .ps__rail-y:focus,
  .ps .ps__rail-y:hover {
    background-color: rgba(147, 51, 234, 0.1) !important;
    width: 10px !important;
  }
`}</style>