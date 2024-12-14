import React, { useState } from "react"
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea"
import { Star, MessageSquare, Phone, Mail, Send } from "lucide-react"
import { motion } from "framer-motion";

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
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ scale: 1.02 }}
    transition={{ duration: 0.3 }}
  >
    <Card className="mb-4 bg-[#1A1A2E]/90 border border-[#9333EA]/20 backdrop-blur-lg shadow-lg hover:shadow-[0_0_30px_rgba(147,51,234,0.2)] transition-all duration-300">
      <CardContent className="flex items-start p-6">
        <Avatar className="h-24 w-24 mr-6 ring-2 ring-[#9333EA]/50">
          <AvatarImage src={lawyer.avatar} alt={lawyer.name} />
          <AvatarFallback className="bg-[#2E2E3A] text-white">
            {lawyer.name.split("").map(n => n[0]).join("")}
          </AvatarFallback>
        </Avatar>
        <div className="flex-grow">
          <CardTitle className="text-xl mb-2 text-white">{lawyer.name}</CardTitle>
          <CardDescription className="mb-2 text-purple-300">{lawyer.specialization}</CardDescription>
          <div className="flex items-center mb-2">
            <Star className="h-4 w-4 text-yellow-400 fill-current mr-1" />
            <span className="text-gray-300">{lawyer.rating} ({lawyer.reviewCount} reviews)</span>
          </div>
          <p className="text-sm text-gray-400 mb-4">{lawyer.description}</p>
          <Button 
            onClick={() => onContactClick(lawyer)}
            className="bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white
              hover:shadow-[0_0_20px_rgba(147,51,234,0.5)] transition-all duration-300"
          >
            Contact Lawyer
          </Button>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

const ContactSheet = ({ lawyer, isOpen, onClose }) => {
  const [message, setMessage] = useState("");
  const [selectedMethod, setSelectedMethod] = useState(null);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (message.trim()) {
      console.log(`Sending message to ${lawyer.name}: ${message}`);
      setMessage("");
      onClose();
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent className="bg-[#1A1A2E] border-l border-[#9333EA]/20 w-[400px] overflow-hidden">
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 50 }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
          className="h-full flex flex-col"
        >
          <SheetHeader className="pb-6 border-b border-[#9333EA]/20">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <SheetTitle className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Contact {lawyer.name}
              </SheetTitle>
              <SheetDescription className="text-gray-400">
                Choose your preferred contact method
              </SheetDescription>
            </motion.div>
          </SheetHeader>

          <motion.div 
            className="flex-1 py-6 overflow-y-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="space-y-6">
              {/* Contact Methods */}
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: <Mail className="w-6 h-6" />, label: "Email", action: () => setSelectedMethod("email") },
                  { icon: <Phone className="w-6 h-6" />, label: "Call", action: () => setSelectedMethod("call") },
                  { icon: <MessageSquare className="w-6 h-6" />, label: "Message", action: () => setSelectedMethod("message") },
                  { icon: <Send className="w-6 h-6" />, label: "WhatsApp", action: () => setSelectedMethod("whatsapp") }
                ].map((method, index) => (
                  <motion.button
                    key={method.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * (index + 1) }}
                    onClick={method.action}
                    className={`p-4 rounded-xl border flex flex-col items-center gap-2 transition-all duration-300
                      ${selectedMethod === method.label.toLowerCase() 
                        ? 'border-[#9333EA] bg-[#9333EA]/20 text-white' 
                        : 'border-[#9333EA]/20 text-gray-400 hover:border-[#9333EA]/50 hover:bg-[#9333EA]/10'}`}
                  >
                    {method.icon}
                    <span className="text-sm font-medium">{method.label}</span>
                  </motion.button>
                ))}
              </div>

              {/* Message Form */}
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ 
                  opacity: selectedMethod ? 1 : 0,
                  height: selectedMethod ? "auto" : 0 
                }}
                transition={{ duration: 0.3 }}
              >
                <form onSubmit={handleSendMessage} className="space-y-4">
                  <Textarea
                    placeholder="Type your message here..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="min-h-[150px] bg-[#2E2E3A] border-[#9333EA]/20 text-white resize-none
                      focus:border-[#9333EA] focus:ring-1 focus:ring-[#9333EA] transition-all
                      hover:border-[#9333EA]/50 rounded-xl p-4"
                  />
                  
                  <motion.div
                    className="space-y-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <Button 
                      type="submit" 
                      className="w-full bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white
                        hover:shadow-[0_0_20px_rgba(147,51,234,0.5)] transition-all duration-300
                        rounded-xl py-3"
                    >
                      <Send className="mr-2 h-4 w-4" />
                      Send Message
                    </Button>

                    <p className="text-xs text-gray-500 text-center">
                      Response time: Usually within 24 hours
                    </p>
                  </motion.div>
                </form>
              </motion.div>

              {/* Lawyer Info */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-6 p-4 rounded-xl bg-[#2E2E3A]/50 border border-[#9333EA]/20"
              >
                <h3 className="text-white font-medium mb-2">Contact Information</h3>
                <div className="space-y-2 text-sm text-gray-400">
                  <p className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {lawyer.email}
                  </p>
                  <p className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {lawyer.phone}
                  </p>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      </SheetContent>
    </Sheet>
  );
};

export function LawyerRecommendationPage() {
  const [selectedLawyer, setSelectedLawyer] = useState(null);

  const handleContactClick = (lawyer) => {
    setSelectedLawyer(lawyer);
  };

  const handleCloseContact = () => {
    setSelectedLawyer(null);
  };

  return (
    <div className="min-h-screen bg-[#030614] pt-24">
      <div className="max-w-6xl mx-auto px-4 py-8 relative">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
          <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px]"></div>
          <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px]"></div>
        </div>

        {/* Content */}
        <div className="relative z-10">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400"
          >
            Recommended Lawyers
          </motion.h1>
          <ScrollArea className="h-[calc(100vh-10rem)] pr-4">
            {lawyers.map((lawyer) => (
              <LawyerCard key={lawyer.id} lawyer={lawyer} onContactClick={handleContactClick} />
            ))}
          </ScrollArea>
          {selectedLawyer && (
            <ContactSheet
              lawyer={selectedLawyer}
              isOpen={!!selectedLawyer}
              onClose={handleCloseContact}
            />
          )}
        </div>
      </div>
    </div>
  );
}