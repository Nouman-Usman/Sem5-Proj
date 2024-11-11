import React, { useState } from "react"
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea"
import { Star, MessageSquare, Phone, Mail, Send } from "lucide-react"

const lawyers = [
  {
    id: 1,
    name: "Jane Doe",
    specialization: "Family Law",
    rating: 4.8,
    reviewCount: 120,
    description: "Jane Doe is an experienced family law attorney with over 15 years of practice. She specializes in divorce, child custody, and adoption cases.",
    avatar: "/placeholder.svg?height=100&width=100",
    phone: "+1 (555) 123-4567",
    email: "jane.doe@example.com",
    whatsapp: "+1 (555) 987-6543"
  },
  {
    id: 2,
    name: "John Smith",
    specialization: "Criminal Defense",
    rating: 4.6,
    reviewCount: 95,
    description: "John Smith is a skilled criminal defense attorney known for his aggressive courtroom tactics and thorough case preparation.",
    avatar: "/placeholder.svg?height=100&width=100",
    phone: "+1 (555) 234-5678",
    email: "john.smith@example.com",
    whatsapp: "+1 (555) 876-5432"
  },
  // Add more lawyer objects as needed
]

const LawyerCard = ({ lawyer, onContactClick }) => (
  <Card className="mb-4">
    <CardContent className="flex items-start p-6">
      <Avatar className="h-24 w-24 mr-6">
        <AvatarImage src={lawyer.avatar} alt={lawyer.name} />
        <AvatarFallback>{lawyer.name.split("").map(n => n[0]).join("")}</AvatarFallback>
      </Avatar>
      <div className="flex-grow">
        <CardTitle className="text-xl mb-2">{lawyer.name}</CardTitle>
        <CardDescription className="mb-2">{lawyer.specialization}</CardDescription>
        <div className="flex items-center mb-2">
          <Star className="h-4 w-4 text-yellow-400 fill-current mr-1" />
          <span>{lawyer.rating} ({lawyer.reviewCount} reviews)</span>
        </div>
        <p className="text-sm text-gray-600 mb-4">{lawyer.description}</p>
        <Button onClick={() => onContactClick(lawyer)}>Contact Lawyer</Button>
      </div>
    </CardContent>
  </Card>
)

const ContactSheet = ({ lawyer, isOpen, onClose }) => {
  const [message, setMessage] = useState("")

  const handleSendMessage = (e) => {
    e.preventDefault()
    // Implement send message logic here
    console.log(`Sending message to ${lawyer.name}: ${message}`)
    setMessage("")
    onClose()
  }

  return (
    (<Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Contact {lawyer.name}</SheetTitle>
          <SheetDescription>Choose a method to contact the lawyer</SheetDescription>
        </SheetHeader>
        <div className="py-4">
          <h3 className="mb-2 font-semibold">Send a Message</h3>
          <form onSubmit={handleSendMessage}>
            <Textarea
              placeholder="Type your message here..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="mb-2" />
            <Button type="submit" className="w-full">
              <Send className="mr-2 h-4 w-4" /> Send Message
            </Button>
          </form>
          <div className="mt-4 space-y-2">
            <h3 className="font-semibold">Other Contact Options</h3>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => window.open(`tel:${lawyer.phone}`)}>
              <Phone className="mr-2 h-4 w-4" /> Call
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => window.open(`mailto:${lawyer.email}`)}>
              <Mail className="mr-2 h-4 w-4" /> Email
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => window.open(`https://wa.me/${lawyer.whatsapp}`)}>
              <MessageSquare className="mr-2 h-4 w-4" /> WhatsApp
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>)
  );
}

export function LawyerRecommendationPage() {
  const [selectedLawyer, setSelectedLawyer] = useState(null)

  const handleContactClick = (lawyer) => {
    setSelectedLawyer(lawyer)
  }

  const handleCloseContact = () => {
    setSelectedLawyer(null)
  }

  return (
    (<div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Recommended Lawyers</h1>
      <ScrollArea className="h-[calc(100vh-10rem)]">
        {lawyers.map((lawyer) => (
          <LawyerCard key={lawyer.id} lawyer={lawyer} onContactClick={handleContactClick} />
        ))}
      </ScrollArea>
      {selectedLawyer && (
        <ContactSheet
          lawyer={selectedLawyer}
          isOpen={!!selectedLawyer}
          onClose={handleCloseContact} />
      )}
    </div>)
  );
}