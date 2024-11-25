import React, { useState, useRef, useEffect } from "react"
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Loader2, Send, User, Bot, Star } from "lucide-react"
import apiService from "../services/api"

const LawyerCard = ({ lawyer }) => (
  <div className="max-w-sm bg-white border border-gray-200 rounded-lg shadow-md dark:bg-gray-800 dark:border-gray-700">
    <a href="#">
      <img className="rounded-t-lg" src="https://via.placeholder.com/150" alt={lawyer.name} />
    </a>
    <div className="p-5">
      <a href="#">
        <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">{lawyer.name}</h5>
      </a>
      <p className="mb-3 font-normal text-gray-700 dark:text-gray-400">{lawyer.specialization}</p>
      <div className="flex items-center mt-1">
        <Star className="h-4 w-4 text-yellow-400 fill-current" />
        <span className="ml-1 text-sm">{lawyer.rating}</span>
      </div>
      <p className="mt-2 text-sm">{lawyer.experience}</p>
      <p className="mt-2 text-sm">{lawyer.location}</p>
      <p className="mt-2 text-sm">{lawyer.contact}</p>
      <a href="#" className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
        Contact {lawyer.name}
        <svg className="w-3.5 h-3.5 ms-2 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
          <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M1 5h12m0 0L9 1m4 4L9 9"/>
        </svg>
      </a>
    </div>
  </div>
)

const ReferenceCard = ({ reference, index }) => (
  <Card className="p-2 bg-white shadow-md w-40 transition-transform transform hover:scale-105">
    <div className="flex items-center">
      <div className="flex-1">
        <a href={reference} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline font-bold text-lg transition duration-300 ease-in-out transform hover:text-blue-700 hover:scale-105">
          {`Reference ${index + 1}`}
        </a>
      </div>
    </div>
  </Card>
)

export function ChatbotPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [chatId, setChatId] = useState(null)
  const scrollAreaRef = useRef(null)
  const userId = "demo_user"

  useEffect(() => {
    const loadExistingChat = async () => {
      try {
        const response = await apiService.getUserChats(userId)
        if (response.data.chat_ids.length > 0) {
          setChatId(response.data.chat_ids[0])
          const messagesResponse = await apiService.getChatMessages(userId, response.data.chat_ids[0])
          setMessages(messagesResponse.data.messages)
        }
      } catch (err) {
        console.error("Error loading chat:", err)
        setError("Failed to load chat history")
      }
    }
    loadExistingChat()
  }, [])

  const handleSend = async () => {
    if (!input.trim()) return

    setLoading(true)
    setError(null)

    const userMessage = { role: "user", content: input }
    setMessages(prev => [...prev, userMessage])
    setInput("")

    try {
      const response = await apiService.askQuestion(input, userId, chatId)
      const { answer, chat_id, recommendations, references } = response.data
      setChatId(chat_id)
      const assistantMessage = { 
        role: "assistant", 
        content: answer,
        references,
        recommendations 
      }
      setMessages(prev => [...prev, assistantMessage])
      
      if (scrollAreaRef.current) {
        scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
      }
    } catch (err) {
      console.error("Error sending message:", err)
      setError("Failed to send message. Please try again.")
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <Card className="h-[600px] flex flex-col">
        <ScrollArea ref={scrollAreaRef} className="flex-1 p-4">
          {messages.map((message, i) => (
            <div
              key={i}
              className={`flex items-start gap-3 mb-4 ${
                message.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              <Avatar>
                {message.role === "user" ? (
                  <User className="p-2" />
                ) : (
                  <Bot className="p-2" />
                )}
              </Avatar>
              <div
                className={`rounded-lg p-4 max-w-[80%] ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                <p>{message.content}</p>
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
          ))}
          {error && (
            <div className="text-red-500 text-center my-2">{error}</div>
          )}
        </ScrollArea>
        
        <div className="p-4 border-t flex gap-4">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message..."
            disabled={loading}
          />
          <Button onClick={handleSend} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </Card>
    </div>
  )
}