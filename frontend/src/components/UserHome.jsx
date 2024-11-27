import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MessageSquare, Users, Info } from "lucide-react"

export function UserHome() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Welcome to Apna Waqeel</h1>
      {/* What's New Section */}
      <section className="mb-12">
        <Card>
          <CardHeader>
            <CardTitle>What's New</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-2">
              <li>New AI model for more accurate legal advice</li>
              <li>Expanded database of legal precedents</li>
              <li>Improved user interface for easier navigation</li>
              <li>Added support for multiple languages</li>
            </ul>
          </CardContent>
        </Card>
      </section>
      {/* Chat to AI Now Section */}
      <section className="mb-12">
        <Card>
          <CardHeader>
            <CardTitle>Chat to AI Now</CardTitle>
            <CardDescription>Get instant legal advice from our AI assistant</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="mb-4">Our AI is ready to assist you with any legal questions or concerns you may have.</p>
            <a href="/chatbot">
              <Button className="w-full sm:w-auto">
                <MessageSquare className="mr-2 h-4 w-4" /> Start AI Chat
              </Button>
            </a>
          </CardContent>
        </Card>
      </section>
      {/* Talk to Our Best Lawyers Section */}
      <section className="mb-12">
        <Card>
          <CardHeader>
            <CardTitle>Talk to Our Best Lawyers</CardTitle>
            <CardDescription>Connect with experienced legal professionals</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="mb-4">Need personalized advice? Consult with our top-rated lawyers.</p>
            <a href="/Lawyers">
              <Button className="w-full sm:w-auto">
                <Users className="mr-2 h-4 w-4" /> Explore Our Lawyers
              </Button>
            </a>
          </CardContent>
        </Card>
      </section>
      {/* What is AI Section */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle>What is AI?</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Artificial Intelligence (AI) in legal tech refers to advanced computer systems that can perform tasks 
              typically requiring human intelligence. Our AI can analyze legal documents, provide quick answers to 
              common legal questions, and even predict case outcomes based on historical data.
            </p>
            <p>
              While AI is a powerful tool, it's important to note that it doesn't replace human lawyers. Instead, 
              it complements their expertise by handling routine tasks and providing initial guidance, allowing 
              human lawyers to focus on more complex aspects of legal practice.
            </p>
            <a href="/about">
              <Button variant="outline" className="mt-4">
                <Info className="mr-2 h-4 w-4" /> Learn More About AI in Law
              </Button>
            </a>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}