from fastapi import FastAPI, Request, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, TypedDict
import uuid
from datetime import datetime, timedelta
import gc
import json
import logging
import numpy as np
from history import AzureTableChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, BaseMessage

# Import your RAGAgent class
from main import RAGAgent  # Update import to use main.py

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)

class Document(BaseModel):
    title: str
    content: str
app = FastAPI(
    title="RAG Question Answering API",
    description="""
    This API provides question-answering capabilities using RAG (Retrieval Augmented Generation).
    
    Features
    1) Ask questions and get AI-generated answers
    2) Session management for context preservation
    3) Session monitoring and cleanup
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "2022cs49@student.uet.edu.pk"
    },
    license_info={
        "name": "MIT License",
    }
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class BaseUserRequest(BaseModel):
    """Base class for all requests requiring user_id"""
    user_id: str = Field(..., description="User identifier")

class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to ask")
    user_id: str = Field(..., description="User identifier")

class ChatMessage(BaseModel):
    role: str
    content: str
    references: Optional[List[str]] = []  # Add references field

class ChatInfo(BaseModel):
    chat_id: str
    user_id: str
    created_at: datetime
    messages: List[Dict[str, str]]

class ChatInfo(BaseModel):  # Renamed from SessionInfo
    chat_id: str
    user_id: str  # Added user_id as required field
    created_at: datetime
    last_accessed: datetime
    question_count: int

class LawyerRecommendation(BaseModel):
    name: str
    specialization: str
    experience: str
    rating: str
    location: str
    contact: str

class AnswerResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer")
    chat_id: str = Field(..., description="The chat ID for context tracking")
    chat_info: ChatInfo = Field(..., description="Information about the current chat")
    recommendations: List[LawyerRecommendation] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list, description="Reference URLs")

    class Config:
        schema_extra = {
            "example": {
                "answer": "RAG (Retrieval Augmented Generation) is...",
                "chat_id": "123e4567-e89b-12d3-a456-426614174000",
                "chat_info": {
                    "chat_id": "123e4567-e89b-12d3-a456-426614174000",
                    "created_at": "2024-01-01T00:00:00",
                    "last_accessed": "2024-01-01T00:01:00",
                    "question_count": 1
                }
            }
        }

class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[Document]
    chat_id: str  
    user_id: str

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class SessionManager:
    def __init__(self, agent: RAGAgent, expiry_minutes: int = 30):
        self.agent = agent
        self.contexts: Dict[str, Dict] = {}
        self.expiry_minutes = expiry_minutes
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Initialize with empty session store - sessions will be loaded per user"""
        logging.info("Sessions will be loaded per user")
        return

    def load_user_sessions(self, user_id: str):
        """Load all sessions for a specific user"""
        try:
            chat_history = AzureTableChatMessageHistory(
                chat_id="temp",  # Changed from chat_id
                user_id=user_id,
                connection_string=self.agent.connection_string
            )
            sessions = chat_history.load_user_sessions(user_id)
            
            for session_data in sessions:
                chat_id = session_data.get('chat_id')
                if (chat_id):
                    # Convert datetime strings
                    if isinstance(session_data.get('created_at'), str):
                        session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                    if isinstance(session_data.get('last_accessed'), str):
                        session_data['last_accessed'] = datetime.fromisoformat(session_data['last_accessed'])
                    if isinstance(session_data.get('expiry'), str):
                        session_data['expiry'] = datetime.fromisoformat(session_data['expiry'])
                    
                    self.contexts[chat_id] = session_data
            
            logging.info(f"Loaded {len(sessions)} sessions for user {user_id}")
            
        except Exception as e:
            logging.error(f"Error loading sessions for user {user_id}: {e}")

    def create_session(self, user_id: str, chat_id: str) -> str:
        """Create a new chat session"""
        now = datetime.now()
        chat_data = {
            'chat_id': chat_id,
            'user_id': user_id,
            'context': None,
            'expiry': now.isoformat(),  # Convert to ISO format string
            'created_at': now.isoformat(),
            'last_accessed': now.isoformat(),
            'updated_at': now.isoformat(),
            'question_count': 0,
            'chat_history': [],
            'session_state': 'active'
        }
        
        try:
            chat_history = AzureTableChatMessageHistory(
                chat_id=chat_id,
                user_id=user_id,
                connection_string=self.agent.connection_string
            )
            
            # Store session data as JSON string
            chat_history.store_session_data(json.dumps(chat_data, cls=DateTimeEncoder))
            
            # Store in memory (keep datetime objects for in-memory usage)
            self.contexts[chat_id] = {
                **chat_data,
                'expiry': now,
                'created_at': now,
                'last_accessed': now,
                'updated_at': now
            }
            
            logging.info(f"New chat {chat_id} created for user {user_id}")
            return chat_id
            
        except Exception as e:
            logging.error(f"Error creating chat session: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create chat session: {str(e)}"
            )

    def get_context(self, chat_id: str) -> Optional[Dict]:
        # First check in-memory context
        if chat_id not in self.contexts:
            # Try loading from persistent storage
            stored_session = self.agent.load_session(chat_id)
            if (stored_session):
                self.contexts[chat_id] = stored_session
            else:
                raise HTTPException(status_code=404, detail="Session not found")
                
        context_data = self.contexts[chat_id]
        if datetime.now() < context_data['expiry']:
            context_data['last_accessed'] = datetime.now()
            # Update persistent storage
            self.agent.store_session(chat_id, context_data)
            return context_data['context']
        else:
            del self.contexts[chat_id]  # Expired, delete the session
            self.agent.delete_session(chat_id)  # Delete from persistent storage
            raise HTTPException(status_code=410, detail="Session expired")
    
    def ensure_user_sessions_loaded(self, user_id: str):
        """Ensure user sessions are loaded before access"""
        if not any(ctx['user_id'] == user_id for ctx in self.contexts.values()):
            self.load_user_sessions(user_id)

    def get_chat_info(self, user_id: str, chat_id: str) -> Optional[ChatInfo]:
        """Get information about a chat"""
        self.ensure_user_sessions_loaded(user_id)
        
        # First check in-memory contexts
        if chat_id in self.contexts:
            data = self.contexts[chat_id]
            if data['user_id'] == user_id:
                return ChatInfo(
                    chat_id=chat_id,
                    user_id=user_id,
                    created_at=data['created_at'],
                    last_accessed=data['last_accessed'],
                    question_count=data['question_count']
                )
        
        # If not in memory, check storage
        try:
            chat_history = AzureTableChatMessageHistory(
                chat_id=chat_id,
                user_id=user_id,
                connection_string=self.agent.connection_string
            )
            
            if chat_history.chat_exists(user_id, chat_id):
                messages = chat_history.messages
                # Create minimal chat info
                return ChatInfo(
                    chat_id=chat_id,
                    user_id=user_id,
                    created_at=datetime.now(),  # Use current time as fallback
                    last_accessed=datetime.now(),
                    question_count=len(messages)
                )
        except Exception as e:
            logging.error(f"Error checking chat existence: {e}")
            
        return None

    def list_active_chats(self) -> List[ChatInfo]:
        """List all active chats"""
        chats = []
        for chat_id, data in self.contexts.items():
            info = self.get_chat_info(data['user_id'], chat_id)
            if info:
                chats.append(info)
        return chats

    def set_context(self, chat_id: str, context: Dict):
        """Update session data and maintain chat history"""
        if chat_id not in self.contexts:
            raise HTTPException(status_code=404, detail="Session not found")

        now = datetime.now()
        
        # Create chat entry
        chat_entry = {
            'question': context.get('last_question', ''),
            'answer': context.get('output', ''),
            'timestamp': context.get('timestamp', now.isoformat())
        }
        
        # Update session with new data while preserving history
        if 'chat_history' not in self.contexts[chat_id]:
            self.contexts[chat_id]['chat_history'] = []
            
        # Convert datetime objects to ISO format strings
        session_data = {
            'chat_id': chat_id,
            'user_id': self.contexts[chat_id]['user_id'],
            'context': self.contexts[chat_id].get('context'),
            'last_accessed': now.isoformat(),
            'updated_at': now.isoformat(),
            'expiry': (now + timedelta(minutes=self.expiry_minutes)).isoformat(),
            'question_count': self.contexts[chat_id].get('question_count', 0),
            'chat_history': self.contexts[chat_id].get('chat_history', []) + [chat_entry],
            'session_state': 'active'
        }
        
        # Update in-memory context with datetime objects
        self.contexts[chat_id].update({
            'last_accessed': now,
            'updated_at': now,
            'expiry': now + timedelta(minutes=self.expiry_minutes),
            'chat_history': session_data['chat_history']
        })
        
        try:
            # Store session data using agent's method with serialized dates
            self.agent.store_session(chat_id, session_data)
            logging.info(f"Session {chat_id} updated with new chat entry")
        except Exception as e:
            logging.error(f"Error persisting session {chat_id}: {e}")

    def cleanup_expired(self):
        current_time = datetime.now()
        expired_sessions = [sid for sid, data in self.contexts.items() if current_time > data['expiry']]
        for sid in expired_sessions:
            del self.contexts[sid]
        logging.info(f"Cleaned up {len(expired_sessions)} expired sessions")

    def get_user_chat_ids(self, user_id: str) -> List[str]:
        """Get all chat IDs for a specific user directly from Azure Table"""
        try:
            chat_history = AzureTableChatMessageHistory(
                chat_id="temp",  # Changed from chat_id
                user_id=user_id,
                connection_string=self.agent.connection_string
            )
            # Get chat IDs from Azure Table
            chat_ids = chat_history.get_user_chats(user_id)  # Changed from get_user_chat_ids
            logging.info(f"Retrieved {len(chat_ids)} chat IDs for user {user_id}")
            return chat_ids
        except Exception as e:
            logging.error(f"Error retrieving chat IDs for user {user_id}: {e}")
            raise

agent = RAGAgent()
session_manager = SessionManager(agent=agent)

@app.get("/health", tags=["System"], summary="Health Check")
async def health_check():
    """Check the health status of the API."""
    return {"status": "healthy"}

@app.post("/ask", response_model=AnswerResponse, tags=["Questions"])
async def ask_question(
    request: QueryRequest,  # Already requires user_id through BaseUserRequest
    chat_id: Optional[str] = Query(None, description="Optional chat ID for context"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Ask a question and get an AI-generated answer.
    
    Parameters:
    - user_id (required): User identifier for maintaining chat context
    - question (required): The question to ask
    - chat_id (optional): Chat ID for continuing existing conversations
    """
    if not request.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
        
    try:
        # Verify existing chat or create new one
        if chat_id:
            chat_history = AzureTableChatMessageHistory(
                chat_id=chat_id,
                user_id=request.user_id,
                connection_string=agent.connection_string
            )
            # Verify chat belongs to user
            if not chat_history.messages and not any(msg.content for msg in chat_history.messages):
                chat_id = str(uuid.uuid4())
                logging.info(f"Creating new chat {chat_id} for user {request.user_id}")
                session_manager.create_session(request.user_id, chat_id)
        else:
            chat_id = str(uuid.uuid4())
            logging.info(f"Creating new chat {chat_id} for user {request.user_id}")
            session_manager.create_session(request.user_id, chat_id)

        # Pass both user_id and chat_id to maintain context
        result = agent.run(request.question, request.user_id, chat_id)
        
        # Extract references from result if they exist
        references = []
        answer = result
        if "\nReference:" in result:
            answer, refs = result.split("\nReference:", 1)
            references = [ref.strip() for ref in refs.split(',') if ref.strip()]
            answer = answer.strip()

        # Get lawyer recommendations
        sentiment = agent.analyze_sentiment(request.question)
        recommendations = agent.lawyer_store.get_top_lawyers(sentiment)
        
        formatted_recommendations = [
            LawyerRecommendation(
                name=lawyer['name'],
                specialization=lawyer['specialization'],
                experience=lawyer['experience'],
                rating=lawyer['rating'],
                location=lawyer['location'],
                contact=lawyer['contact']
            )
            for lawyer in recommendations
        ]

        # Store recommendations and references in Azure
        chat_history = AzureTableChatMessageHistory(
            chat_id=chat_id,
            user_id=request.user_id,
            connection_string=agent.connection_string
        )

        # Store as metadata
        metadata = {
            "lawyers": [lawyer.dict() for lawyer in formatted_recommendations],
            "references": references,
            "category": sentiment
        }
        chat_history.store_metadata(chat_id, metadata)

        # Update context with ISO formatted timestamps
        now = datetime.now()
        session_manager.set_context(chat_id, {
            "output": result,
            "last_question": request.question,
            "timestamp": now.isoformat()
        })
        
        # Get chat info for response
        chat_info = session_manager.get_chat_info(request.user_id, chat_id)
        if not chat_info:
            raise HTTPException(status_code=404, detail="Chat not found")
            
        return {
            "answer": answer,
            "chat_id": chat_id,
            "chat_info": chat_info,
            "recommendations": formatted_recommendations,
            "references": references
        }
    
    except Exception as e:
        logging.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "type": type(e).__name__}
        )
    finally:
        gc.collect()

@app.delete("/user/{user_id}/chat/{chat_id}", tags=["Chats"])
async def clear_chat(user_id: str, chat_id: str):
    """Clear a specific chat context."""
    try:
        # Load user sessions first
        session_manager.ensure_user_sessions_loaded(user_id)
        
        # Try to get chat info
        chat_info = session_manager.get_chat_info(user_id, chat_id)
        if not chat_info:
            # Initialize chat history to attempt deletion from storage
            chat_history = AzureTableChatMessageHistory(
                chat_id=chat_id,
                user_id=user_id,
                connection_string=agent.connection_string
            )
            chat_history.clear()  # Clear messages even if not in memory
            return {"message": "Chat cleared successfully"}
            
        if chat_info.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this chat")
            
        # Delete from memory if exists
        if chat_id in session_manager.contexts:
            del session_manager.contexts[chat_id]
        
        # Clear from storage
        agent.clear_session_memory(chat_id)
        return {"message": "Chat cleared successfully"}
        
    except Exception as e:
        logging.error(f"Error clearing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}/chats/active", tags=["Chats"], summary="List Active Chats")
async def list_active_chats(user_id: str):
    """List all active chats for a user."""
    return [chat for chat in session_manager.list_active_chats() if chat.user_id == user_id]

@app.get("/user/{user_id}/chat/{chat_id}", tags=["Chats"])
async def get_chat_info(user_id: str, chat_id: str):
    """Get information about a specific chat."""
    # Load user sessions first
    session_manager.ensure_user_sessions_loaded(user_id)
    
    info = session_manager.get_chat_info(user_id, chat_id)
    if not info:
        # Try to get from storage directly
        chat_history = AzureTableChatMessageHistory(
            chat_id=chat_id,
            user_id=user_id,
            connection_string=agent.connection_string
        )
        messages = chat_history.messages
        if messages:
            # Create minimal chat info if messages exist
            return ChatInfo(
                chat_id=chat_id,
                user_id=user_id,
                created_at=datetime.now(),  # Use current time as fallback
                last_accessed=datetime.now(),
                question_count=len(messages)
            )
        raise HTTPException(status_code=404, detail="Chat not found")
    return info

@app.get("/user/{user_id}/chats", tags=["Chats"], summary="Get User's Chat IDs")
async def get_user_chats(
    user_id: str,
    create_if_none: bool = Query(False, description="Create a new chat if user has none")
):
    """Get all chat IDs associated with a specific user."""
    try:
        # Initialize chat history with empty chat_id
        chat_history = AzureTableChatMessageHistory(
            chat_id="temp",
            user_id=user_id,
            connection_string=agent.connection_string,
            table_name="ChatMessages"  # Specify the correct table
        )
        
        chat_ids = chat_history.get_user_chats(user_id)
        
        if not chat_ids and create_if_none:
            new_chat_id = str(uuid.uuid4())
            session_manager.create_session(user_id, new_chat_id)
            chat_ids = [new_chat_id]
        
        return {
            "user_id": user_id, 
            "chat_ids": chat_ids,
            "count": len(chat_ids)
        }
    except Exception as e:
        logging.error(f"Error retrieving chat IDs for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chat IDs: {str(e)}"
        )

class MessageResponse(BaseModel):
    messages: List[ChatMessage]
    metadata: Optional[Dict] = None

@app.get("/user/{user_id}/chat/{chat_id}/messages", tags=["Chats"], response_model=MessageResponse)
async def get_chat_messages(user_id: str, chat_id: str):
    """Get messages with metadata including references and lawyer recommendations."""
    try:
        chat_history = AzureTableChatMessageHistory(
            chat_id=chat_id,
            user_id=user_id,
            connection_string=agent.connection_string
        )
        
        messages = chat_history.get_chat_messages(user_id, chat_id)
        logging.info(f"Found {len(messages)} messages for chat {chat_id}")
        
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage)) and msg.content:
                content = msg.content
                references = []
                
                if "\nReference:" in content:
                    main_content, refs = content.split("\nReference:", 1)
                    references = [ref.strip() for ref in refs.split(',') if ref.strip()]
                    content = main_content.strip()
                
                formatted_messages.append({
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": content,
                    "references": references
                })
        
        # Get metadata including lawyer recommendations
        metadata = chat_history.get_metadata(chat_id)
        
        return {
            "messages": formatted_messages,
            "metadata": metadata
        }
        
    except Exception as e:
        logging.error(f"Error retrieving chat messages: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "type": type(e).__name__}
        )


