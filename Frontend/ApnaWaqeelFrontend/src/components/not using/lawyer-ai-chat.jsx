import React, { useState, useRef, useEffect } from "react"
import { ChevronLeft, ChevronRight, Plus, Send, MessageSquare, GripVertical } from "lucide-react"

export function LawyerAiChatJsx() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [sidebarWidth, setSidebarWidth] = useState(256) // 16rem = 256px
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState("''")
  const [isThinking, setIsThinking] = useState(false)
  const [thinkingMessage, setThinkingMessage] = useState("''")
  const [isDragging, setIsDragging] = useState(false)
  const sidebarRef = useRef(null)

  const handleSendMessage = () => {
    if (inputMessage.trim() === "''") return

    setMessages([...messages, { type: "'user'", content: inputMessage }])
    setInputMessage("''")

    setIsThinking(true)
    setThinkingMessage(Math.random() < 0.5 ? "'ChatBot is thinking...'" : "'Searching web...'")

    setTimeout(() => {
      setIsThinking(false)
      const aiResponse = "This is a simulated AI response. Sometimes, I might recommend lawyer."
      setMessages(prevMessages => [...prevMessages, { type: "'ai'", content: aiResponse }])

      if (Math.random() < 0.33) {
        setMessages(prevMessages => [
          ...prevMessages,
          {
            type: "'recommendation'",
            content: {
              name: "'John Doe'",
              specialization: "'Criminal Law'",
              experience: "'15 years'"
            }
          }
        ])
      }
    }, 2000)
  }

  const handleMouseDown = (e) => {
    setIsDragging(true)
    document.addEventListener("'mousemove'", handleMouseMove)
    document.addEventListener("'mouseup'", handleMouseUp)
  }

  const handleMouseMove = (e) => {
    if (isDragging) {
      const newWidth = e.clientX
      setSidebarWidth(Math.max(200, Math.min(newWidth, 400))) // Min 200px, Max 400px
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    document.removeEventListener("'mousemove'", handleMouseMove)
    document.removeEventListener("'mouseup'", handleMouseUp)
  }

  useEffect(() => {
    return () => {
      document.removeEventListener("'mousemove'", handleMouseMove)
      document.removeEventListener("'mouseup'", handleMouseUp)
    };
  }, [])

  return (
    (<div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <div
        ref={sidebarRef}
        className={`bg-gray-900 text-white transition-all duration-300 ${sidebarOpen ? "''" : "'w-0'"} overflow-hidden relative`}
        style={{ width: sidebarOpen ? `${sidebarWidth}px` : "'0px'" }}>
        <div className="p-4 h-full flex flex-col">
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-2 w-full mb-4 flex items-center justify-center transition duration-200">
            <Plus size={18} className="mr-2" /> New Chat
          </button>
          <div className="space-y-2 flex-grow overflow-y-auto">
            {["'Previous Chat 1'", "'Previous Chat 2'", "'Previous Chat 3'"].map((chat, index) => (
              <div
                key={index}
                className="bg-gray-800 rounded-lg p-3 hover:bg-gray-700 transition duration-200 cursor-pointer flex items-center">
                <MessageSquare size={18} className="mr-2 text-gray-400" />
                <span className="text-sm">{chat}</span>
              </div>
            ))}
          </div>
          {/* Sidebar Toggle */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="absolute bottom-4 right-4 bg-gray-800 text-white p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-gray-500 hover:bg-gray-700 transition duration-200">
            {sidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
          </button>
        </div>
        {/* Drag handle */}
        <div
          className="absolute top-0 right-0 w-1 h-full cursor-ew-resize bg-gray-700 hover:bg-blue-500 transition-colors duration-200"
          onMouseDown={handleMouseDown}>
          <div
            className="absolute top-1/2 right-0 transform -translate-y-1/2 bg-gray-600 p-1 rounded-l">
            <GripVertical size={12} />
          </div>
        </div>
      </div>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === "'user'" ? "'justify-end'" : "'justify-start'"}`}>
              <div
                className={`max-w-[70%] rounded-lg p-3 ${
                  message.type === "'user'" 
                    ? "'bg-blue-600 text-white'" 
                    : "'bg-white shadow-md'"
                }`}>
                {message.type === "'recommendation'" ? (
                  <div className="bg-green-100 p-3 rounded-lg shadow-inner">
                    <h3 className="font-bold text-green-800">Recommended Lawyer</h3>
                    <p className="text-green-700">{message.content.name}</p>
                    <p className="text-green-600">{message.content.specialization}</p>
                    <p className="text-green-600">{message.content.experience} experience</p>
                  </div>
                ) : (
                  <p
                    className={message.type === "'user'" ? "'text-white'" : "'text-gray-800'"}>{message.content}</p>
                )}
              </div>
            </div>
          ))}
          {isThinking && (
            <div className="flex justify-start">
              <div className="bg-gray-200 rounded-lg p-3 max-w-[70%] animate-pulse">
                {thinkingMessage}
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <div className="flex items-center">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 p-3 border border-neutral-200 border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-neutral-800"
              onKeyPress={(e) => e.key === "'Enter'" && handleSendMessage()} />
            <button
              onClick={handleSendMessage}
              className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-r-lg transition duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>)
  );
}