import React, { useState, useRef, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Loader2, Send, User, Bot, ChevronLeft, ChevronRight, Star, PlusCircle, Trash2 } from "lucide-react"
import apiService from "@/services/api"  // Add this import

const LawyerCard = ({ lawyer }) => (
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
    <Button className="mt-2 w-full">Contact {lawyer.name}</Button>
  </Card>
)

export function ChatbotPage() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! How can I assist you with your legal questions today?", sender: "ai" }
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [processing, setProcessing] = useState(null) // 'thinking' or 'searching'
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [chatHistory, setChatHistory] = useState([
    { id: 1, title: "Previous Chat 1", date: "2023-05-01" },
    { id: 2, title: "Previous Chat 2", date: "2023-05-02" },
  ])
  const messagesEndRef = useRef(null)
  const [error, setError] = useState(null)
  const [references, setReferences] = useState([])
  const userId = "test_user" // In production, get from auth system
  const [currentChatId, setCurrentChatId] = useState(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (inputMessage.trim() === "") return

    const newUserMessage = { id: messages.length + 1, text: inputMessage, sender: "user" }
    setMessages(prev => [...prev, newUserMessage])
    setInputMessage("")
    setProcessing("thinking")
    setError(null)

    try {
      const response = await apiService.askQuestion(inputMessage, userId, currentChatId)
      
      const aiResponse = {
        id: messages.length + 2,
        text: response.answer,
        sender: "ai",
        lawyers: response.recommendedLawyers
      }

      setMessages(prev => [...prev, aiResponse])
      setReferences(response.references || [])
      
      if (response.chatId && !currentChatId) {
        setCurrentChatId(response.chatId)
      }

    } catch (err) {
      setError(err.message)
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, there was an error processing your request. Please try again.",
        sender: "ai"
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setProcessing(null)
    }
  }

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
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
              {chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className="mb-2 p-2 hover:bg-gray-100 rounded cursor-pointer">
                  <h3 className="font-medium">{chat.title}</h3>
                  <p className="text-sm text-gray-500">{chat.date}</p>
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
                    className={`max-w-[70%] rounded-lg p-3 ${
                      message.sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"
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
                      <LawyerCard lawyer={message.lawyer} />
                    </div>
                  </div>
                )}
                {message.lawyers && message.lawyers.length > 0 && (
                  <div className="flex flex-col gap-2 mt-2">
                    {message.lawyers.map((lawyer, idx) => (
                      <LawyerCard key={idx} lawyer={lawyer} />
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
    </div>
  )
}

