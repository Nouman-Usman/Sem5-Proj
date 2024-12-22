import React, { useState, useRef, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2, Send, User, Bot, ChevronLeft, ChevronRight, Star, History, Plus, LogOut, Settings, Star as StarIcon, BookOpen, ExternalLink, FileText, AlertCircle, Minus, ChevronDown, ArrowDown, Edit2, Trash2 } from "lucide-react";
import apiService from "@/services/api";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import PerfectScrollbar from 'react-perfect-scrollbar';
import 'react-perfect-scrollbar/dist/css/styles.css';
import Logo from "@/assets/Main logo.svg";
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import ReactMarkdown from 'react-markdown';

// Configure PDF.js with better error handling
const pdfjsVersion = pdfjs.version;
const pdfjsWorkerPath = new URL(
  `../../../node_modules/pdfjs-dist/build/pdf.worker.min.js`,
  import.meta.url
).href;

pdfjs.GlobalWorkerOptions.workerSrc = pdfjsWorkerPath;

// Add this error handling utility
const handlePdfError = (error) => {
  console.error('PDF Error:', error);
  if (error.message.includes('getHexString')) {
    return 'The PDF contains unsupported characters. Try opening in browser.';
  }
  return error.message;
};
// Add this utility function
const isGovtUrl = (url) => {
  try {
    const domain = new URL(url).hostname;
    return domain.includes('.gov.') || domain.includes('.mohr.gov.pk');
  } catch {
    return false;
  }
};

// Update the fetchPDFAsBlob function
const fetchPDFAsBlob = async (url) => {
  try {
    // For government websites, show a warning
    if (isGovtUrl(url)) {
      console.warn('Accessing government website, SSL verification might fail');
    }

    const proxyUrl = `${apiService.API_BASE_URL}/proxy-pdf?url=${encodeURIComponent(url)}`;
    
    const response = await fetch(proxyUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/pdf,*/*',
      },
      cache: 'no-cache',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    if (blob.size === 0) {
      throw new Error('Empty PDF received');
    }

    return URL.createObjectURL(blob);
  } catch (error) {
    console.error('Error fetching PDF:', error);
    throw new Error(
      isGovtUrl(url) 
        ? 'This government website is temporarily inaccessible. Please try opening in browser.' 
        : error.message
    );
  }
};

// Update the PDFViewerPopup component
const PDFViewerPopup = ({ url, onClose }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);

  useEffect(() => {
    const loadPDF = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const blobUrl = await fetchPDFAsBlob(url);
        setPdfUrl(blobUrl);
        
      } catch (err) {
        console.error('Error:', err);
        setError(handlePdfError(err));
      } finally {
        setIsLoading(false);
      }
    };

    loadPDF();
    return () => {
      // Cleanup blob URL when component unmounts
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [url]);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
    setIsLoading(false);
  }

  function onDocumentLoadError(error) {
    console.error('Error loading PDF:', error);
    setError(handlePdfError(error));
    setIsLoading(false);
  }

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/70 backdrop-blur-sm z-50">
      <div className="w-[90%] h-[90%] bg-[#1A1A2E]/90 p-4 rounded-lg shadow-[0_0_30px_rgba(147,51,234,0.3)] border border-[#9333EA]/20">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold text-white">PDF Document</h2>
            {numPages && (
              <div className="text-gray-400 text-sm">
                Page {pageNumber} of {numPages}
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            {/* Zoom controls */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setScale(scale => Math.max(0.5, scale - 0.1))}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                <Minus className="h-4 w-4" />
              </Button>
              <span className="text-white min-w-[3rem] text-center">
                {Math.round(scale * 100)}%
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setScale(scale => Math.min(2, scale + 0.1))}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            
            {/* Page navigation */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={pageNumber <= 1}
                onClick={() => setPageNumber(page => page - 1)}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={pageNumber >= numPages}
                onClick={() => setPageNumber(page => page + 1)}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => window.open(url, '_blank', 'noopener,noreferrer')}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                Open in Browser
              </Button>
              <Button
                variant="outline"
                onClick={onClose}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                Close
              </Button>
            </div>
          </div>
        </div>

        <div className="relative w-full h-[calc(100%-4rem)] rounded-lg bg-[#2E2E3A] overflow-auto">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
            </div>
          )}

          {error ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
              <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
              <p className="text-lg font-medium mb-2">{error}</p>
              <p className="text-sm text-gray-400 mb-4">
                {isGovtUrl(url) 
                  ? "Government websites may have security restrictions. Try opening in your browser."
                  : "Try opening in browser instead"}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => window.open(url, '_blank', 'noopener,noreferrer')}
                  className="border-[#9333EA]/20 text-white hover:bg-white/5"
                >
                  Open in Browser
                </Button>
                {error.includes('temporarily') && (
                  <Button
                    variant="outline"
                    onClick={() => handleRetry()}
                    className="border-[#9333EA]/20 text-white hover:bg-white/5"
                  >
                    Retry
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex justify-center p-4">
              {pdfUrl && (
                <Document
                  file={pdfUrl}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={onDocumentLoadError}
                  loading={
                    <div className="flex items-center justify-center">
                      <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
                    </div>
                  }
                >
                  <Page
                    pageNumber={pageNumber}
                    scale={scale}
                    className="shadow-xl"
                    loading={
                      <div className="flex items-center justify-center h-[800px]">
                        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
                      </div>
                    }
                  />
                </Document>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Update the ReferenceCard component
const ReferenceCard = ({ reference }) => {
  const [showPdfViewer, setShowPdfViewer] = useState(false);
  
  const handleClick = () => {
    const url = typeof reference === 'string' ? reference : reference.url;
    if (!url) return;

    // Check if the URL ends with .pdf
    if (url.toLowerCase().endsWith('.pdf')) {
      setShowPdfViewer(true);
    } else {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <>
      <Card 
        className="p-3 bg-[#1A1A2E]/90 border border-[#9333EA]/20 backdrop-blur-lg shadow-[0_0_15px_rgba(147,51,234,0.2)] hover:shadow-[0_0_30px_rgba(147,51,234,0.3)] transition-all duration-300 cursor-pointer hover:scale-[1.01]"
        onClick={handleClick}
      >
        <div className="flex items-start space-x-3">
          <div className="h-8 w-8 flex items-center justify-center rounded-full bg-[#9333EA]/20">
            {(typeof reference === 'string' ? reference : reference.url)?.toLowerCase().endsWith('.pdf') ? (
              <FileText className="h-4 w-4 text-purple-400" />
            ) : (
              <BookOpen className="h-4 w-4 text-purple-400" />
            )}
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium mb-1 hover:text-purple-400 transition-colors">
              {reference.title || 'Legal Reference'}
            </h4>
            <p className="text-sm text-gray-400 mb-2">{reference.description || reference}</p>
            {(reference.url || typeof reference === 'string') && (
              <div className="text-sm text-purple-400 hover:text-purple-300 flex items-center group">
                <ExternalLink className="h-4 w-4 mr-1 group-hover:translate-x-0.5 transition-transform" />
                {(typeof reference === 'string' ? reference : reference.url)?.toLowerCase().endsWith('.pdf') 
                  ? 'View PDF document' 
                  : 'Click to view source'
                }
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* PDF Viewer Popup */}
      {showPdfViewer && (
        <PDFViewerPopup 
          url={typeof reference === 'string' ? reference : reference.url}
          onClose={() => setShowPdfViewer(false)}
        />
      )}
    </>
  );
};

const FormattedMessage = ({ content }) => {
  return (
    <div className="prose prose-invert max-w-none">
      <ReactMarkdown
        components={{
          ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-2 mb-4" {...props} />,
          ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-2 mb-4" {...props} />,
          li: ({node, ...props}) => <li className="text-gray-300" {...props} />,
          blockquote: ({node, ...props}) => (
            <blockquote className="border-l-4 border-purple-500 pl-4 my-4" {...props} />
          ),
          code: ({node, inline, ...props}) => 
            inline ? (
              <code className="bg-[#2E2E3A] px-1 rounded text-purple-300" {...props} />
            ) : (
              <code className="block bg-[#2E2E3A] p-4 rounded-lg text-purple-300 my-4 whitespace-pre-wrap" {...props} />
            ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

const ProcessingIndicator = ({ message }) => (
  <div className="flex justify-start mb-4">
    <div className="bg-gradient-to-r from-[#2E2E3A] to-[#1A1A2E] text-gray-200 rounded-lg p-4 
      shadow-[0_0_15px_rgba(147,51,234,0.2)] animate-message border border-[#9333EA]/20 
      backdrop-blur-sm relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#9333EA]/10 to-transparent 
        animate-shimmer" style={{ backgroundSize: '200% 100%' }}></div>
      <div className="relative flex items-center">
        <div className="mr-4 bg-[#9333EA]/20 p-2 rounded-full">
          <Bot className="h-5 w-5 text-purple-400" />
        </div>
        <div className="flex items-center">
          <div className="flex space-x-1 mr-3">
            <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
            <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
            <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></span>
          </div>
          <p className="text-purple-200 font-medium">
            {message === "Cooking Best Results..." ? (
              <span className="inline-flex items-center">
                Cooking Best Results
                <span className="inline-block ml-1 opacity-80 animate-pulse">✨</span>
              </span>
            ) : (
              <span className="inline-flex items-center">
                Searching the web
                <span className="inline-block ml-1 opacity-80 animate-pulse">🔍</span>
              </span>
            )}
          </p>
        </div>
      </div>
    </div>
  </div>
);

export default function LawyerChatbotPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const [messages, setMessages] = useState([
    { id: 1, text: "", sender: "ai" } // Start with empty text
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [processing, setProcessing] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessionHistory, setSessionHistory] = useState([]);
  const messagesEndRef = useRef(null);
  const [error, setError] = useState(null);
  const [references, setReferences] = useState([]);
  const [showContactPopup, setShowContactPopup] = useState(false);
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const [contactMessage, setContactMessage] = useState("");
  const [typingText, setTypingText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");
  const textareaRef = useRef(null);

  // Updated scrollToBottom to target the correct container and scroll instantly
  const scrollToBottom = () => {
    const scrollContainer = document.querySelector('.flex-1.flex-col.min-h-0.relative');
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
    // Alternatively, ensure messagesEndRef is correctly referenced
    messagesEndRef.current?.scrollIntoView({ behavior: "auto" });
  };

  // Update the scroll position check
  const handleScroll = (e) => {
    const element = e.target;
    const atBottom = Math.abs((element.scrollHeight - element.scrollTop) - element.clientHeight) < 50;
    setShowScrollButton(!atBottom);
  };

  // Add this useEffect to handle automatic scrolling for new messages
  useEffect(() => {
    if (!showScrollButton) {
      scrollToBottom();
    }
  }, [messages, showScrollButton]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchChatTopics = async () => {
      const chatTopics = await apiService.getChatTopic();
      if (chatTopics) {
        setSessionHistory(chatTopics.topic.map((topic, index) => ({
          id: chatTopics.session_id[index],
          title: topic,
          date: chatTopics.time[index]
        })));
      }
    };

    fetchChatTopics();
    const intervalId = setInterval(fetchChatTopics, 5000);

    return () => clearInterval(intervalId);
  }, []);

  const simulateResponse = async (text) => {
    setIsTyping(true);
    await new Promise(resolve => setTimeout(resolve, 500));
    setIsTyping(false);
    return text;
  };

  useEffect(() => {
    const initialMessage = "Hello! How can I assist you with your legal question?";
    simulateResponse(initialMessage).then(text => {
      setMessages([{ id: 1, text, sender: "ai" }]);
    });
  }, []); // Run once on component mount

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (inputMessage.trim() === "") return;

    // Reset textarea height to initial state
    if (textareaRef.current) {
      textareaRef.current.style.height = '60px';
    }

    const newUserMessage = { id: messages.length + 1, text: inputMessage, sender: "user" };
    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage("");
    setProcessing("Cooking Best Results...");
    setError(null);

    try {
      const currentCredits = await apiService.getUserCredits();
      if (currentCredits === 0) {
        if (apiService.getUserRole() === 'lawyer') {
          navigate("/lawyer-subscription");
        } else {
          navigate("/subscription-plans");
        }
        return;
      }

      const sessionId = searchParams.get('session');
      const response = await apiService.askQuestion(inputMessage, sessionId);

      if (!response) {
        throw new Error('Empty response received');
      }

      await apiService.updateCredits(currentCredits - 1);

      if (response.session_id && !sessionId) {
        setSearchParams({ session: response.session_id });
      }

      const aiResponse = {
        id: messages.length + 2,
        text: response.answer,
        sender: "ai",
        references: response.references || []
      };

      await simulateResponse(response.answer);
      setMessages(prev => [...prev, aiResponse]);

    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
      const errorMessage = {
        id: messages.length + 2,
        text: "Sorry, there was an error processing your request. Please try again.",
        sender: "ai"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setProcessing(null);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const handleContact = (lawyer) => {
    setSelectedLawyer(lawyer);
    setShowContactPopup(true);
  };

  const handleSendContactMessage = async () => {
    if (contactMessage.trim() === "") return;

    try {
      await apiService.startChat(selectedLawyer.id);
      await apiService.sendMessage(selectedLawyer.id, contactMessage);
      setContactMessage("");
      setShowContactPopup(false);
    } catch (error) {
      console.error("Failed to send message:", error.message);
    }
  };

  const loadPreviousSession = async (session) => {
    try {
      setProcessing("Loading previous chat...");
      setError(null);
      
      const prevChat = await apiService.getChatsFromSessionId(session.id);
      console.log("Previous chat data:", prevChat); // Debug log
      
      if (!prevChat?.data?.data) {
        setMessages([{
          id: 1,
          text: "Hello! How can I assist you with your legal question?",
          sender: "ai"
        }]);
        setSearchParams({ session: session.id });
        return;
      }
  
      const newChats = prevChat.data.data.map((chat, index) => ({
        id: chat.message_id || index + 1,
        text: chat.message,
        sender: chat.message_type === "AI Message" ? "ai" : "user",
        references: chat.references || [],
        lawyers: Array.isArray(chat.recommended_lawyers) ? chat.recommended_lawyers : []
      }));
  
      console.log("Processed chat messages:", newChats); // Debug log
      
      if (newChats.length === 0) {
        newChats.push({
          id: 1,
          text: "Hello! How can I assist you with your legal question?",
          sender: "ai"
        });
      }
      
      setMessages(newChats);
      setSearchParams({ session: session.id });
      
    } catch (error) {
      console.error("Error loading previous session:", error);
      setError("Failed to load previous chat. Please try again.");
    } finally {
      setProcessing(null);
    }
  };

  // Add useEffect to check URL params on mount
  useEffect(() => {
    const sessionId = searchParams.get('session');
    if (sessionId && sessionHistory.length > 0) {
      const session = sessionHistory.find(s => s.id === sessionId);
      if (session) {
        loadPreviousSession(session);
      }
    }
  }, [sessionHistory, searchParams]); // Added searchParams as dependency

  const handleGoPremium = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user.role === 'lawyer') {
      navigate('/lawyer-subscription');
    } else if (user.role === 'client') {
      navigate('/subscription-plans');
    }
  };

  const handleLogout = () => {
    apiService.logout();
    navigate('/login');
  };

  const handleNewChat = () => {
    // Clear the session ID from URL
    setSearchParams({});
    
    // Reset messages to initial state
    setMessages([
      { 
        id: 1, 
        text: "Hello! How can I assist you with your legal question?", 
        sender: "ai" 
      }
    ]);
    
    setError(null);
    
    setProcessing(null);
    
    // Clear references
    setReferences([]);
  };

  const handleEditSession = (session) => {
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
  };

  const handleSaveEdit = async (sessionId) => {
    try {
      await apiService.updateChatTitle(sessionId, editingTitle);
      // Update the session history
      setSessionHistory(prevHistory =>
        prevHistory.map(session =>
          session.id === sessionId
            ? { ...session, title: editingTitle }
            : session
        )
      );
      setEditingSessionId(null);
    } catch (error) {
      console.error("Failed to update chat title:", error);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (window.confirm("Are you sure you want to delete this chat?")) {
      try {
        await apiService.deleteChat(sessionId);
        setSessionHistory(prevHistory =>
          prevHistory.filter(session => session.id !== sessionId)
        );
        
        // If the deleted session is the current one, start a new chat
        if (searchParams.get('session') === sessionId) {
          handleNewChat();
        }
      } catch (error) {
        console.error("Failed to delete chat:", error);
      }
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#030614]">
      {/* Sidebar with toggle button inside */}
      <div className={`bg-[#1A1A2E]/90 backdrop-blur-lg border-r border-[#9333EA]/20 
        ${isSidebarOpen ? "w-64" : "w-20"} 
        transition-all duration-300 ease-in-out overflow-hidden flex-shrink-0 relative`}
      >
        <div className="h-full flex flex-col">
          {/* First section for toggle button and New Chat button */}
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <Button 
                type="button" 
                onClick={toggleSidebar} 
                variant="outline" 
                size="icon"
                className="border-[#9333EA]/20 text-purple-400 hover:text-purple-300 hover:bg-white/5 group"
              >
                <ChevronLeft className="h-4 w-4 transition-colors" />
              </Button>
            </div>
            <div 
              onClick={handleNewChat}
              className="flex items-center border-[#9333EA]/20 text-purple-400
                hover:text-purple-300 hover:bg-white/5 bg-[#1A1A2E]/90 backdrop-blur-lg
                animate-fadeIn hover:scale-110 transition-all duration-200
                shadow-[0_0_15px_rgba(147,51,234,0.2)] group rounded-full p-2
                cursor-pointer"
            >
              <Plus className="h-4 w-4 transition-colors" />
              {isSidebarOpen && <span className="ml-2 text-white">New Chat</span>}
            </div>
          </div>

          {/* Second section for recent chats */}
          <div className="flex-1 p-4 overflow-hidden flex flex-col">
            <h3 className="text-white/90 mb-2 sticky top-0 bg-[#1A1A2E]/90 z-10">
              {isSidebarOpen && "Recent"}
            </h3>
            <div className="flex-1 overflow-y-hidden">
              <PerfectScrollbar
                options={{
                  suppressScrollX: true,
                  wheelPropagation: true
                }}
                className="h-full pr-2"
              >
                <div className="space-y-2">
                  {sessionHistory.map((session) => (
                    <div
                      key={session.id}
                      className="p-2 hover:bg-white/5 rounded-lg cursor-pointer border border-transparent 
                        hover:border-[#9333EA]/20 transition-all duration-300 group"
                      onClick={() => loadPreviousSession(session)} // Add this onClick handler
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          {editingSessionId === session.id ? (
                            <div className="flex items-center gap-2">
                              <Input
                                type="text"
                                value={editingTitle}
                                onChange={(e) => setEditingTitle(e.target.value)}
                                className="h-7 bg-[#2E2E3A] border-[#9333EA]/20 text-white"
                                onKeyPress={(e) => {
                                  if (e.key === 'Enter') {
                                    handleSaveEdit(session.id);
                                  }
                                }}
                                autoFocus
                              />
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleSaveEdit(session.id)}
                                className="h-7 px-2 border-[#9333EA]/20 text-purple-400"
                              >
                                Save
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => setEditingSessionId(null)}
                                className="h-7 px-2 border-[#9333EA]/20 text-purple-400"
                              >
                                Cancel
                              </Button>
                            </div>
                          ) : (
                            <>
                              <h3 className="font-medium text-white/90 truncate">
                                {isSidebarOpen && session.title}
                              </h3>
                              <p className="text-sm text-gray-400 truncate">
                                {isSidebarOpen && session.date}
                              </p>
                            </>
                          )}
                        </div>
                        {isSidebarOpen && !editingSessionId && (
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditSession(session);
                              }}
                              className="h-7 w-7 p-0 hover:bg-white/5 text-gray-400 hover:text-purple-400"
                            >
                              <Edit2 className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteSession(session.id);
                              }}
                              className="h-7 w-7 p-0 hover:bg-white/5 text-gray-400 hover:text-red-400"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </PerfectScrollbar>
            </div>
          </div>

          {/* Third section for fixed navigation items */}
          <div className="p-4 border-t border-[#9333EA]/20">
            <div className="space-y-4">
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={() => navigate('/lawyer-dashboard')}
              >
                <User className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Dashboard"}
              </Button>
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={handleGoPremium}  // Updated onClick handler
              >
                <StarIcon className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Go Premium"}
              </Button>
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={() => navigate('/account-settings')}
              >
                <Settings className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Account Settings"}
              </Button>
              <Button 
                variant="outline" 
                className="w-full text-left text-white bg-black hover:text-white hover:bg-white/5 border border-[#9333EA] hover:shadow-[0_0_15px_rgba(147,51,234,0.3)]"
                onClick={handleLogout}  // Updated onClick handler
              >
                <LogOut className="h-4 w-4 mr-2" />
                {isSidebarOpen && "Logout"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen">
        {/* Fixed Header */}
        <header className="flex-shrink-0 h-16 flex items-center justify-center bg-[#1A1A2E]/90 border-b border-[#9333EA]/20">
          <img src={Logo} alt="Logo" className="h-10" />
        </header>

        {/* Chat Container */}
        <div className="flex-1 flex flex-col min-h-0 relative">
          {/* Background Effects */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#9333EA]/20 rounded-full blur-[128px]"></div>
            <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-[#7E22CE]/20 rounded-full blur-[96px]"></div>
            <div className="absolute bottom-1/4 right-1/4 w-[300px] h-[300px] bg-[#6B21A8]/20 rounded-full blur-[64px]"></div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 min-h-0 relative">
            <PerfectScrollbar
              options={{
                suppressScrollX: true,
                wheelPropagation: true
              }}
              className="absolute inset-0"
              onScroll={handleScroll}
            >
              <div className="max-w-4xl mx-auto p-4">
                {error && (
                  <div className="bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4">
                    {error}
                  </div>
                )}

                <div className="space-y-4">
                  {messages.map((message) => (
                    <div key={message.id}>
                      <div className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"} mb-4`}>
                        <div className={`max-w-[70%] rounded-lg p-3 ${
                          message.sender === "user" 
                            ? "bg-gradient-to-r from-[#9333EA] to-[#7E22CE] text-white" 
                            : "bg-[#2E2E3A] text-gray-200"
                        } shadow-[0_0_15px_rgba(147,51,234,0.2)] animate-pop`}>
                          <div className="flex items-start">
                            {message.sender === "user" ? (
                              <User className="h-5 w-5 mr-2 mt-1" />
                            ) : (
                              <Bot className="h-5 w-5 mr-2 mt-1" />
                            )}
                            {message.sender === "ai" ? (
                              <FormattedMessage content={message.text} />
                            ) : (
                              <p>{message.text}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {/* Show references if available */}
                      {message.references && message.references.length > 0 && (
                        <div className="ml-12 mb-4 space-y-2">
                          <h4 className="text-white/90 text-sm font-medium">References:</h4>
                          {message.references.map((ref, idx) => (
                            <ReferenceCard 
                              key={idx} 
                              reference={ref}
                            />
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

                  {processing && <ProcessingIndicator message={processing} />}
                  <div ref={messagesEndRef} />
                </div>
              </div>
            </PerfectScrollbar>

            {/* Add the scroll to bottom button */}
            {showScrollButton && (
              <button
                onClick={scrollToBottom}
                className="fixed bottom-32 right-8 p-3 rounded-full
                  bg-gradient-to-r from-[#9333EA] to-[#7E22CE]
                  shadow-[0_0_20px_rgba(147,51,234,0.5)]
                  hover:shadow-[0_0_30px_rgba(147,51,234,0.8)]
                  transition-all duration-300
                  animate-pulse-subtle
                  hover:scale-110
                  group
                  z-50
                  opacity-90 hover:opacity-100"
              >
                <ArrowDown className="h-5 w-5 text-white group-hover:animate-bounce" />
              </button>
            )}
          </div>

          {/* Fixed Input Area */}
          <div className="flex-shrink-0 bg-[#1A1A2E]/90 border-t border-[#9333EA]/20 p-4">
            <div className="max-w-4xl mx-auto">
              <form onSubmit={handleSendMessage} className="relative">
                <div className="flex-1 bg-[#2E2E3A] rounded-[24px] border border-[#9333EA]/20">
                  <textarea
                    ref={textareaRef}
                    placeholder="Type your message here..."
                    value={inputMessage}
                    onChange={(e) => {
                      setInputMessage(e.target.value);
                      // Adjust height automatically
                      e.target.style.height = '60px';
                      e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage(e);
                      }
                    }}
                    className="w-full bg-transparent text-white placeholder:text-gray-400 
                      focus:outline-none px-6 py-4 min-h-[60px] max-h-[200px] rounded-[24px] 
                      resize-none overflow-auto scrollbar-thin scrollbar-thumb-[#9333EA] 
                      scrollbar-track-transparent pr-[60px]"
                    style={{
                      height: '60px',
                    }}
                  />
                  <button 
                    type="submit"
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-3 rounded-full
                      bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 
                      transition-all duration-300 flex items-center justify-center
                      shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40"
                  >
                    <Send className="h-5 w-5 text-white" />
                  </button>
                </div>
              </form>
              <div className="text-center text-gray-400 text-xs mt-2 flex items-center justify-center gap-2">
                <span>Apna Waqeel can make mistakes. Check important info.</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      {/* Contact Popup */}
      {showContactPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
          <div className="bg-[#1A1A2E]/90 p-6 rounded-lg shadow-[0_0_30px_rgba(147,51,234,0.3)] border border-[#9333EA]/20 w-96 backdrop-blur-lg">
            <h2 className="text-xl font-semibold mb-4 text-white">Contact {selectedLawyer.name}</h2>
            <textarea
              className="w-full p-2 bg-[#2E2E3A] border border-[#9333EA]/20 rounded-lg text-white placeholder:text-gray-400 mb-4 focus:ring-[#9333EA] resize-none"
              rows="4"
              placeholder="Type your message here..."
              value={contactMessage}
              onChange={(e) => setContactMessage(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button 
                variant="outline" 
                onClick={() => setShowContactPopup(false)}
                className="border-[#9333EA]/20 text-white hover:bg-white/5"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSendContactMessage}
                className="bg-gradient-to-r from-[#9333EA] to-[#7E22CE] hover:opacity-90 transition-opacity"
              >
                Send
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

<style jsx>{`
  .custom-scrollbar::-webkit-scrollbar {
    width: 8px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: #1A1A2E;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: #9333EA;
    border-radius: 10px;
    border: 2px solid #1A1A2E;
  }

  @keyframes messageIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-message {
    animation: messageIn 0.3s ease-out;
  }

  .typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: currentColor;
    margin-left: 2px;
    animation: blink 1s step-end infinite;
  }

  @keyframes blink {
    50% { opacity: 0; }
  }

  .typing-dots::after {
    content: '';
    animation: dots 1.5s infinite;
    display: inline-block;
    width: 0;
  }

  @keyframes dots {
    0%, 20% { content: ''; }
    40% { content: '.'; }
    60% { content: '..'; }
    80% { content: '...'; }
    100% { content: ''; }
  }

  @keyframes pop {
    0% {
      opacity: 0;
      transform: scale(0.8) translateY(10px);
    }
    50% {
      transform: scale(1.05) translateY(-5px);
    }
    100% {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .animate-pop {
    animation: pop 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
  }

  .input-glow {
    animation: inputGlow 2s ease-in-out infinite;
  }

  @keyframes inputGlow {
    0% {
      box-shadow: 0 0 5px rgba(147,51,234,0.2);
      border-color: rgba(147,51,234,0.2);
    }
    50% {
      box-shadow: 0 0 20px rgba(147,51,234,0.4);
      border-color: rgba(147,51,234,0.6);
    }
    100% {
      box-shadow: 0 0 5px rgba(147,51,234,0.2);
      border-color: rgba(147,51,234,0.2);
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-out forwards;
  }

  /* Custom Scrollbar Styling */
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .custom-scrollbar::-webkit-scrollbar-track {
    background: #1A1A2E;
    border-radius: 8px;
    margin: 2px;
  }

  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #9333EA 0%, #7E22CE 100%);
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: padding-box;
    transition: all 0.3s ease;
    box-shadow: 
      0 0 5px rgba(147, 51, 234, 0.3),
      0 0 10px rgba(147, 51, 234, 0.2),
      0 0 15px rgba(147, 51, 234, 0.1);
  }

  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #7E22CE 0%, #9333EA 100%);
    box-shadow: 
      0 0 10px rgba(147, 51, 234, 0.5),
      0 0 20px rgba(147, 51, 234, 0.3),
      0 0 30px rgba(147, 51, 234, 0.2);
  }

  /* Apply custom scrollbar to chat area as well */
  .flex-1.overflow-y-auto {
    scrollbar-width: thin;
    scrollbar-color: #9333EA #1A1A2E;
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar-track {
    background: #1A1A2E;
    border-radius: 8px;
    margin: 2px;
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #9333EA 0%, #7E22CE 100%);
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: padding-box;
    transition: all 0.3s ease;
    box-shadow: 
      0 0 5px rgba(147, 51, 234, 0.3),
      0 0 10px rgba(147, 51, 234, 0.2),
      0 0 15px rgba(147, 51, 234, 0.1);
  }

  .flex-1.overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #7E22CE 0%, #9333EA 100%);
    box-shadow: 
      0 0 10px rgba(147, 51, 234, 0.5),
      0 0 20px rgba(147, 51, 234, 0.3),
      0 0 30px rgba(147, 51, 234, 0.2);
  }

  /* Custom styles for the main chat area PerfectScrollbar */
  .ps__rail-y {
    background-color: transparent !important;
    width: 10px !important;
    margin-right: 0;
  }

  .ps__rail-y:hover {
    background-color: rgba(147, 51, 234, 0.1) !important;
  }

  .ps__thumb-y {
    background: linear-gradient(180deg, #9333EA 0%, #7E22CE 100%) !important;
    width: 6px !important;
    right: 2px !important;
    border-radius: 10px !important;
  }

  .ps__thumb-y:hover {
    background: linear-gradient(180deg, #7E22CE 0%, #9333EA 100%) !important;
  }

  .ps .ps__rail-y.ps--clicking,
  .ps .ps__rail-y:focus,
  .ps .ps__rail-y:hover {
    background-color: rgba(147, 51, 234, 0.1) !important;
    width: 10px !important;
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .animate-shimmer {
    animation: shimmer 3s linear infinite;
  }

  @keyframes pulse-subtle {
    0% {
      box-shadow: 0 0 15px rgba(147,51,234,0.4);
    }
    50% {
      box-shadow: 0 0 25px rgba(147,51,234,0.7);
    }
    100% {
      box-shadow: 0 0 15px rgba(147,51,234,0.4);
    }
  }

  .animate-pulse-subtle {
    animation: pulse-subtle 2s infinite;
  }
`}</style>