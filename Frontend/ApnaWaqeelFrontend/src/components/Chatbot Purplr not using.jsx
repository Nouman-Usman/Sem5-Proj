import React, { useState, useEffect, useRef } from "react"
import { Send, Loader, FolderOpen, User, Bot, Search, Globe, ChevronRight, ChevronLeft } from "lucide-react";
import { Link } from "react-router-dom"

const Chatbot = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [thinkingMode, setThinkingMode] = useState(null)
  const [previousChats, setPreviousChats] = useState([])
  const [selectedChat, setSelectedChat] = useState(null)
  const [isHistoryOpen, setIsHistoryOpen] = useState(true)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    const fetchPreviousChats = () => {
      const mockPreviousChats = [
        { id: 1, title: "Legal Advice on Property Dispute" },
        { id: 2, title: "Questions about Employment Law" },
        { id: 3, title: "Consultation on Divorce Proceedings" }
      ]
      setPreviousChats(mockPreviousChats)
    }
    fetchPreviousChats()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const simulateAIResponse = async (query) => {
    setIsLoading(true)
    setThinkingMode("'ai_db'")

    await new Promise(resolve => setTimeout(resolve, 2000))

    if (query.toLowerCase().includes("'complex'") || query.toLowerCase().includes("'specific case law'")) {
      setThinkingMode("'web'")
      await new Promise(resolve => setTimeout(resolve, 3000))
    }

    setIsLoading(false)
    setThinkingMode(null)

    const legalKeywords = ["'sue'", "'court'", "'lawsuit'", "'divorce'", "'criminal'", "'charges'"]
    const shouldRecommendLawyer = legalKeywords.some(keyword => 
      query.toLowerCase().includes(keyword))

    if (shouldRecommendLawyer) {
      return {
        content: "Based on the legal situation you've described, I recommend consulting with Advocate Sarah Khan, who specializes in this area of law. She has handled similar cases successfully.",
        lawyer: { 
          id: 123, 
          name: "Sarah Khan",
          specialization: "Family Law"
        }
      }
    }

    return { 
      content: "Here's what you need to know about your legal query: [Simulated AI response based on Pakistani law]" 
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim()) return

    const newUserMessage = { role: "'user'", content: inputMessage }
    setMessages(prevMessages => [...prevMessages, newUserMessage])
    setInputMessage("")

    const aiResponse = await simulateAIResponse(inputMessage)
    const newAIMessage = { 
      role: "'assistant'", 
      content: aiResponse.content, 
      lawyer: aiResponse.lawyer 
    }
    setMessages(prevMessages => [...prevMessages, newAIMessage])
  }

  const handleLoadPreviousChat = (chatId) => {
    setSelectedChat(chatId)
    setMessages([
      { role: "'user'", content: "What are my rights in a property dispute?" },
      { role: "'assistant'", content: "According to Pakistani law, in a property dispute, your rights include: [Simulated previous chat content]" }
    ])
  }

  const toggleHistory = () => {
    setIsHistoryOpen(!isHistoryOpen)
  }

  return (
    (<div className="flex h-screen bg-black">
      {/* Sidebar */}
      <div
        className={`${isHistoryOpen ? "'w-72'" : "'w-12'"} bg-gray-900 transition-all duration-300 ease-in-out`}>
        <div className="p-4 flex items-center justify-between text-white">
          <h2 className={`text-xl font-bold ${isHistoryOpen ? "" : "hidden"}`}>Previous Chats</h2>
          <button
            onClick={toggleHistory}
            className="text-white hover:text-purple-500 transition-colors">
            {isHistoryOpen ? <ChevronLeft size={24} /> : <ChevronRight size={24} />}
          </button>
        </div>
        {isHistoryOpen && (
          <ul className="space-y-2 p-4">
            {previousChats.map(chat => (
              <li
                key={chat.id}
                className={`cursor-pointer p-3 rounded-lg transition-colors duration-200
                  ${selectedChat === chat.id 
                    ? "'bg-purple-700 text-white'" 
                    : "'text-gray-300 hover:bg-gray-800'"}`}
                onClick={() => handleLoadPreviousChat(chat.id)}>
                <FolderOpen className="inline-block mr-2 w-4 h-4" />
                {chat.title}
              </li>
            ))}
          </ul>
        )}
      </div>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-800">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-6 flex ${message.role === "'user'" ? "'justify-end'" : "'justify-start'"}`}>
              <div
                className={`flex max-w-[80%] ${message.role === "'user'" ? "'flex-row-reverse'" : "'flex-row'"}`}>
                <div
                  className={`flex items-center justify-center w-8 h-8 rounded-full shrink-0
                    ${message.role === "'user'" 
                      ? "'bg-purple-600 ml-3'" 
                      : "'bg-gray-700 mr-3'"}`}>
                  {message.role === "'user'" 
                    ? <User size={16} className="text-white" /> 
                    : <Bot size={16} className="text-white" />}
                </div>
                <div
                  className={`flex flex-col space-y-2 p-4 rounded-2xl
                    ${message.role === "'user'"
                      ? "'bg-purple-600 text-white'"
                      : "'bg-gray-700 text-white'"}`}>
                  {message.content}
                  {message.lawyer && (
                    <div className="mt-3 p-3 bg-gray-600 rounded-lg">
                      <p className="text-sm text-purple-300 mb-2">Recommended Lawyer:</p>
                      <Link
                        to={`/lawyer/${message.lawyer.id}`}
                        className="flex items-center text-white hover:text-purple-300 transition-colors">
                        <User className="w-4 h-4 mr-2" />
                        <span>{message.lawyer.name}</span>
                        <span className="text-sm text-purple-300 ml-2">
                          ({message.lawyer.specialization})
                        </span>
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-center justify-center space-x-2 text-white p-4">
              <Loader className="animate-spin" />
              <span>
                {thinkingMode === "'ai_db'" 
                  ? "'Searching legal database'" 
                  : "'Analyzing relevant case law'"}
              </span>
              {thinkingMode === "'ai_db'" 
                ? <Search className="ml-2" /> 
                : <Globe className="ml-2" />}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gray-900">
          <form onSubmit={handleSendMessage} className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your legal question here..."
              className="flex-1 bg-gray-800 text-white placeholder-gray-400 p-4 rounded-xl border border-neutral-200 border-gray-700 focus:outline-none focus:border-purple-500 transition-colors dark:border-neutral-800" />
            <button
              type="submit"
              disabled={isLoading}
              className="bg-purple-600 text-white p-4 rounded-xl hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>)
  );
}

export default Chatbot