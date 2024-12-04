import React, { useState, useRef, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar } from "@/components/ui/avatar"
import { Loader2, Send, User, Bot, PlusCircle, Trash2, ChevronLeft, ChevronRight, Star } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import apiService from "@/services/api"
import FormattedText from "@/components/FormattedText"

const ChatMessage = ({ message }) => (
  <div className={`flex items-start gap-3 mb-4 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
    <Avatar className={`${message.role === "user" ? "order-2" : ""}`}>
      {message.role === "user" ? <User className="h-6 w-6" /> : <Bot className="h-6 w-6" />}
    </Avatar>
    <div className={`rounded-lg p-4 max-w-[80%] ${
      message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
    }`}>
      {message.content === "Thinking..." ? (
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Thinking...</span>
        </div>
      ) : (
        <FormattedText text={message.content} />
      )}
      {message.references?.length > 0 && (
        <div className="mt-2 text-sm opacity-80">
          <div className="flex flex-wrap gap-2">
            {message.references.map((ref, idx) => (
              <ReferenceCard key={idx} reference={ref} index={idx} />
            ))}
          </div>
        </div>
      )}
      {message.recommendations?.length > 0 && (
        <div className="mt-4">
          <p className="font-semibold">Recommended Lawyers:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {message.recommendations.map((lawyer, idx) => (
              <LawyerCard key={idx} lawyer={lawyer} />
            ))}
          </div>
        </div>
      )}
    </div>
  </div>
)

const Sidebar = ({ isOpen, onToggle, chats, onChatSelect, selectedChatId, onNewChat, onDeleteChat }) => (
  <div className={`fixed left-0 top-0 h-full bg-background border-r transition-all duration-300 flex flex-col ${
    isOpen ? 'w-64' : 'w-16'
  }`}>
    <div className="p-4">
      {isOpen ? (
        <Button onClick={onNewChat} className="w-full">
          <PlusCircle className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      ) : (
        <Button
          variant="ghost"
          size="icon"
          onClick={onNewChat}
          className="w-full"
        >
          <PlusCircle className="h-4 w-4" />
        </Button>
      )}
    </div>
    {isOpen && (
      <ScrollArea className="flex-grow px-4">
        {chats.map((chat) => (
          <div key={chat.id} className="flex items-center mb-2">
            <Button
              variant={selectedChatId === chat.id ? "secondary" : "ghost"}
              className="w-full justify-start text-left truncate"
              onClick={() => onChatSelect(chat.id)}
            >
              {chat.name}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onDeleteChat(chat.id)}>
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ))}
      </ScrollArea>
    )}
    <div className="p-4 mt-auto">
      <Button 
        variant="ghost" 
        size="icon"
        onClick={onToggle}
        className="w-full"
        aria-label={isOpen ? "Close sidebar" : "Open sidebar"}
      >
        {isOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </Button>
    </div>
  </div>
)

const LawyerCard = ({ lawyer }) => (
  <div className="max-w-sm bg-white border border-gray-200 rounded-lg shadow-md dark:bg-gray-800 dark:border-gray-700">
    <a href="#">
      <img
        className="rounded-t-lg"
        src="https://via.placeholder.com/150"
        alt={lawyer.name}
      />
    </a>
    <div className="p-5">
      <a href="#">
        <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
          {lawyer.name}
        </h5>
      </a>
      <p className="mb-3 font-normal text-gray-700 dark:text-gray-400">
        {lawyer.specialization}
      </p>
      <div className="flex items-center mt-1">
        <Star className="h-4 w-4 text-yellow-400 fill-current" />
        <span className="ml-1 text-sm">{lawyer.rating}</span>
      </div>
      <p className="mt-2 text-sm">{lawyer.experience}</p>
      <p className="mt-2 text-sm">{lawyer.location}</p>
      <p className="mt-2 text-sm">{lawyer.contact}</p>
      <a
        href="#"
        className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
      >
        Contact {lawyer.name}
        <svg
          className="w-3.5 h-3.5 ms-2 rtl:rotate-180"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 14 10"
        >
          <path
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M1 5h12m0 0L9 1m4 4L9 9"
          />
        </svg>
      </a>
    </div>
  </div>
)

const ReferenceCard = ({ reference, index }) => (
  <Card className="p-2 bg-white shadow-md w-40 transition-transform transform hover:scale-105">
    <div className="flex items-center">
      <div className="flex-1">
        <a
          href={reference}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 underline font-bold text-lg transition duration-300 ease-in-out transform hover:text-blue-700 hover:scale-105"
        >
          {`Reference ${index + 1}`}
        </a>
      </div>
    </div>
  </Card>
)

const ThinkingAnimation = () => (
  <div className="flex items-center gap-2">
    <Loader2 className="h-4 w-4 animate-spin" />
    <span>Thinking...</span>
  </div>
)

export function ChatbotPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [chatId, setChatId] = useState(null)
  const [chats, setChats] = useState([])
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const scrollAreaRef = useRef(null)
  const userId = "demo_user"

  useEffect(() => {
    loadChats()
  }, [])

  const loadChats = async () => {
    try {
      const response = await apiService.getUserChats(userId)
      setChats(response.data.chat_ids.map((id, index) => ({ id, name: `Chat ${index + 1}` })))
      if (response.data.chat_ids.length > 0) {
        loadChat(response.data.chat_ids[0])
      }
    } catch (err) {
      console.error("Error loading chats:", err)
      setError("Failed to load chat history")
    }
  }

  const loadChat = async (chatId) => {
    try {
      const messagesResponse = await apiService.getChatMessages(userId, chatId)
      setMessages(messagesResponse.data.messages)
      setChatId(chatId)
    } catch (err) {
      console.error("Error loading chat:", err)
      setError("Failed to load chat messages")
    }
  }

  const handleSend = async () => {
    if (!input.trim()) return

    setLoading(true)
    setError(null)

    const userMessage = { role: "user", content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput("")

    const thinkingMessage = { role: "assistant", content: "Thinking..." }
    setMessages((prev) => [...prev, thinkingMessage])

    try {
      const response = await apiService.askQuestion(input, userId, chatId)
      const { answer, chat_id, references, recommendations } = response.data
      setChatId(chat_id)

      const assistantMessage = { role: "assistant", content: answer, references, recommendations }
      setMessages((prev) => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1] = assistantMessage
        return newMessages
      })

      if (scrollAreaRef.current) {
        scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
      }
    } catch (err) {
      console.error("Error sending message:", err)
      setError("Failed to send message. Please try again.")
      setMessages((prev) => prev.slice(0, -2))
    } finally {
      setLoading(false)
    }
  }

  const handleNewChat = async () => {
    try {
      const response = await apiService.createNewChat(userId)
      const newChatId = response.data.chat_id
      setChats((prev) => [...prev, { id: newChatId, name: `Chat ${prev.length + 1}` }])
      loadChat(newChatId)
    } catch (err) {
      console.error("Error creating new chat:", err)
      setError("Failed to create new chat")
    }
  }

  const handleDeleteChat = async (chatIdToDelete) => {
    try {
      await apiService.deleteChat(userId, chatIdToDelete)
      setChats((prev) => prev.filter((chat) => chat.id !== chatIdToDelete))
      if (chatId === chatIdToDelete) {
        const remainingChats = chats.filter((chat) => chat.id !== chatIdToDelete)
        if (remainingChats.length > 0) {
          loadChat(remainingChats[0].id)
        } else {
          setMessages([])
          setChatId(null)
        }
      }
    } catch (err) {
      console.error("Error deleting chat:", err)
      setError("Failed to delete chat")
    }
  }

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={toggleSidebar}
        chats={chats}
        onChatSelect={loadChat}
        selectedChatId={chatId}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />
      <div className={`flex-1 flex flex-col transition-all duration-300 ${
        isSidebarOpen ? 'ml-64' : 'ml-16'
      }`}>
        <Card className="flex-1 flex flex-col">
          <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
            {messages.map((message, i) => (
              <ChatMessage key={i} message={message} />
            ))}
            {error && (
              <div className="text-red-500 text-center my-2">{error}</div>
            )}
          </ScrollArea>
          <div className="p-4 border-t">
            <div className="flex gap-4">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Type your message..."
                disabled={loading}
                className="flex-1"
              />
              <Button onClick={handleSend} disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

