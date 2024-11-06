import React, { useState, useEffect, useRef } from "react"
import { Send, Loader, FolderOpen, User, Bot, Search, Globe } from "lucide-react"
import { Link } from "react-router-dom"

const Chatbot = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState("''")
  const [isLoading, setIsLoading] = useState(false)
  const [thinkingMode, setThinkingMode] = useState(null)
  const [previousChats, setPreviousChats] = useState([])
  const [selectedChat, setSelectedChat] = useState(null)
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

    // Simulate AI/DB search
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Simulate not finding an answer and switching to web search
    if (query.toLowerCase().includes("'complex'") || Math.random() < 0.3) {
      setThinkingMode("'web'")
      await new Promise(resolve => setTimeout(resolve, 3000))
    }

    setIsLoading(false)
    setThinkingMode(null)

    // Simulate lawyer recommendation
    if (query.toLowerCase().includes("'recommend'") || Math.random() < 0.3) {
      return {
        content: "Based on your query, I recommend speaking with Lawyer John Doe, who specializes in this area of law.",
        lawyer: { id: 123, name: "John Doe" }
      }
    }

    return { content: "Here's the information based on your query: [Simulated AI response]" }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim()) return

    const newUserMessage = { role: "'user'", content: inputMessage }
    setMessages(prevMessages => [...prevMessages, newUserMessage])
    setInputMessage("''")

    const aiResponse = await simulateAIResponse(inputMessage)
    const newAIMessage = { role: "'assistant'", content: aiResponse.content, lawyer: aiResponse.lawyer }
    setMessages(prevMessages => [...prevMessages, newAIMessage])
  }

  const handleLoadPreviousChat = (chatId) => {
    setSelectedChat(chatId)
    setMessages([
      { role: "'user'", content: "What are my rights in a property dispute?" },
      { role: "'assistant'", content: "In a property dispute, your rights depend on various factors such as ownership documentation, local laws, and the nature of dispute. Generally, you have right to:..." }
    ])
  }

  const renderMessage = (message, index) => {
    return (
      (<div
        key={index}
        className={`mb-4 flex ${message.role === "'user'" ? "'justify-end'" : "'justify-start'"}`}>
        <div
          className={`flex items-start ${message.role === "'user'" ? "'flex-row-reverse'" : "''"}`}>
          <div
            className={`p-2 rounded-full ${message.role === "'user'" ? "'bg-blue-500'" : "'bg-gray-300'"} mr-2`}>
            {message.role === "'user'" ? <User size={24} color="white" /> : <Bot size={24} />}
          </div>
          <div
            className={`p-2 rounded-lg max-w-[70%] ${
              message.role === "'user'" ? "'bg-blue-500 text-white'" : "'bg-gray-100'"
            }`}>
            {message.content}
            {message.lawyer && (
              <div className="mt-2">
                <Link
                  to={`/lawyer/${message.lawyer.id}`}
                  className="text-blue-600 hover:underline">
                  View {message.lawyer.name}'s Profile
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>)
    );
  }

  return (
    (<div className="flex h-screen bg-gray-100">
      <div className="w-64 bg-white p-4 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Previous Chats</h2>
        <ul>
          {previousChats.map(chat => (
            <li
              key={chat.id}
              className={`cursor-pointer p-2 hover:bg-gray-100 rounded ${selectedChat === chat.id ? "'bg-gray-200'" : "''"}`}
              onClick={() => handleLoadPreviousChat(chat.id)}>
              <FolderOpen className="inline-block mr-2" size={18} />
              {chat.title}
            </li>
          ))}
        </ul>
      </div>
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {messages.map((message, index) => renderMessage(message, index))}
          {isLoading && (
            <div className="text-center p-4">
              <Loader className="animate-spin inline-block mr-2" />
              {thinkingMode === "'ai_db'" ? (
                <span>Searching AI and database <Search className="inline-block ml-2" /></span>
              ) : (
                <span>Searching the web for more information <Globe className="inline-block ml-2" /></span>
              )}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="p-4 bg-white">
          <div className="flex items-center">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message here..."
              className="flex-1 p-2 border border-neutral-200 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-neutral-800" />
            <button
              type="submit"
              className="bg-blue-500 text-white p-2 rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}>
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>)
  );
}

export default Chatbot