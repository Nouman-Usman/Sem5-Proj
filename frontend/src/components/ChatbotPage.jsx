import React, { useState, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2, Send, User, Bot, ChevronLeft, ChevronRight, Star, PlusCircle, Trash2 } from "lucide-react";
import apiService from "@/services/api";  // Add this import
import { useNavigate } from "react-router-dom";


const LawyerCard = ({ lawyer, onContact }) => (
  <Card className="mt-2 p-4 bg-white shadow-md">
    <div className="flex items-center">
      <Avatar className="h-12 w-12 mr-4">
        <AvatarImage src={lawyer.avatar} alt={lawyer.name} />
        <AvatarFallback>{lawyer.name.split("").map(n => n[0]).join("")}</AvatarFallback>
      </Avatar>
      <div>
        <h3 className="font-bold text-lg">{lawyer.name}</h3>
        <p className="text-sm text-gray-500">{lawyer.specialization}</p>
        <div className="flex items-center mt-1">
          <Star className="h-4 w-4 text-yellow-400 fill-current" />
          <span className="ml-1 text-sm">{lawyer.rating} ({lawyer.reviewCount} reviews)</span>
        </div>
      </div>
    </div>
    <p className="mt-2 text-sm">{lawyer.description}</p>
    <Button className="mt-2 w-full" onClick={() => onContact(lawyer)}>Contact {lawyer.name}</Button>
  </Card>
);

export function ChatbotPage() {
  const navigate = useNavigate(); // useNavigate hook for navigation

  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I assist you with your legal questions today?", sender: "ai" }
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [processing, setProcessing] = useState(null); // 'thinking' or 'searching'
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessionHistory, setSessionHistory] = useState([]);
  const messagesEndRef = useRef(null);
  const [error, setError] = useState(null);
  const [references, setReferences] = useState([]);
  const [showContactPopup, setShowContactPopup] = useState(false);
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const [contactMessage, setContactMessage] = useState("");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchChatTopics = async () => {
      const chatTopics = await apiService.getChatTopic();
      // console.log("chat topics are ", chatTopics)
      // console.log(cha)
      if (chatTopics) {
        setSessionHistory(chatTopics.topic.map((topic, index) => ({
          id: chatTopics.session_id[index],
          title: topic,
          date: chatTopics.time[index]
        })));
      }
    };

    fetchChatTopics();
    const intervalId = setInterval(fetchChatTopics, 5000); // Poll every 5 seconds

    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (inputMessage.trim() === "") return;

    try {
      // function to get current credits
      const currentCredits = apiService.getUserCredits();
      if (currentCredits == 0) {
        if (apiService.getUserRole() == 'lawyer') {
          navigate("/lawyer-subscription");
        } else {
          navigate("/subscription-plans");
        }
      }
      else{
        apiService.updateCredits(currentCredits - 1);
      }
    } catch (error) {
      console.log("error handling credits: ", error);
      return;
    }

    const newUserMessage = { id: messages.length + 1, text: inputMessage, sender: "user" };
    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage("");
    setProcessing("thinking");
    setError(null);

    try {
      const response = await apiService.askQuestion(inputMessage);

      if (!response) {
        throw new Error('Empty response received');
      }

      const aiResponse = {
        id: messages.length + 2,
        text: response.answer,
        sender: "ai",
        lawyers: response.recommendedLawyers
      };

      setMessages(prev => [...prev, aiResponse]);
      setReferences(response.references || []);

    } catch (err) {
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
    console.log(session);
    // select * from ChatMessages where ChatMessages.SessionId = session.id


    // now we will just load chats in this syntax
    // { id: 1, text: "Hello! How can I assist you with your legal questions today?", sender: "ai" }
    const prevChat = await apiService.getChatsFromSessionId(session.id);
    if (prevChat == null) {
      console.log("No chats found for this session");
      setMessages([]);
      return;
    };
    console.log(prevChat);
    const newChats = [];
    prevChat.data.data.forEach((chat) => {
      newChats.push({
        id: chat.message_id,
        text: chat.message,
        sender: chat.message_type === "AI Message" ? "ai" : "user",
      });
    });
    console.log(newChats);
    setMessages(newChats);
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-100">
      {/* Sidebar */}
      <div
        className={`bg-gray-100 ${isSidebarOpen ? "w-64" : "w-0"} transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0 p-[10px] border-[5px] border-white`}>
        <div className="h-full overflow-y-auto">
          <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Chat History</h2>
            <ScrollArea className="h-[calc(100vh-8rem)]">
              {sessionHistory.map((session) => (
                <div
                  key={session.id}
                  onClick={() => loadPreviousSession(session)}
                  className="mb-2 p-2 hover:bg-gray-100 rounded cursor-pointer">
                  <h3 className="font-medium">{session.title}</h3>
                  <p className="text-sm text-gray-500">{session.date}</p>
                </div>
              ))}
            </ScrollArea>
          </div>
        </div>
      </div>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden bg-gray-50">
        <div className="flex-1 overflow-y-auto">
          <div className="min-h-full bg-white p-4 rounded-lg shadow-sm">
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            {messages.map((message) => (
              <div key={message.id}>
                <div
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"} mb-4`}>
                  <div
                    className={`max-w-[70%] rounded-lg p-3 ${message.sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"
                      }`}>
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
                {message.lawyer && (
                  <div className="flex justify-start mb-4">
                    <div className="max-w-[70%]">
                      <LawyerCard lawyer={message.lawyer} onContact={handleContact} />
                    </div>
                  </div>
                )}
                {message.lawyers && message.lawyers.length > 0 && (
                  <div className="flex flex-col gap-2 mt-2">
                    {message.lawyers.map((lawyer, idx) => (
                      <LawyerCard key={idx} lawyer={lawyer} onContact={handleContact} />
                    ))}
                  </div>
                )}
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
                <div className="bg-gray-200 text-gray-800 rounded-lg p-3">
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
        <div className="p-4 bg-white border-t">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <Button type="button" onClick={toggleSidebar} variant="outline" size="icon">
              {isSidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </Button>
            <Input
              type="text"
              placeholder="Type your message here..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              className="flex-grow" />
            <Button type="submit">
              <Send className="h-4 w-4 mr-2" />
              Send
            </Button>
          </form>
        </div>
      </div>

      {/* Contact Popup */}
      {showContactPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-96">
            <h2 className="text-xl font-semibold mb-4">Contact {selectedLawyer.name}</h2>
            <textarea
              className="w-full p-2 border border-gray-300 rounded mb-4"
              rows="4"
              placeholder="Type your message here..."
              value={contactMessage}
              onChange={(e) => setContactMessage(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowContactPopup(false)}>Cancel</Button>
              <Button onClick={handleSendContactMessage}>Send</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

