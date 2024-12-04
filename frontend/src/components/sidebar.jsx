import React from 'react'
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from 'lucide-react'

export function Sidebar({ isOpen, onToggle, chats, onChatSelect, selectedChatId }) {
  return (
    <div className={`fixed left-0 top-0 h-full bg-background border-r transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-0'}`}>
      <Button 
        variant="ghost" 
        size="icon" 
        className="absolute -right-10 top-4" 
        onClick={onToggle}
      >
        {isOpen ? <ChevronLeft /> : <ChevronRight />}
      </Button>
      <ScrollArea className="h-full p-4">
        {chats.map((chat) => (
          <Button
            key={chat.id}
            variant={selectedChatId === chat.id ? "secondary" : "ghost"}
            className="w-full justify-start mb-2"
            onClick={() => onChatSelect(chat.id)}
          >
            {chat.name}
          </Button>
        ))}
      </ScrollArea>
    </div>
  )
}
