from fastapi import FastAPI, Request, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
import uuid
from datetime import datetime, timedelta
import gc
import json
import logging
import numpy as np

# Import your RAGAgent class
from test import RAGAgent

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="RAG Question Answering API",
    description="""
    This API provides question-answering capabilities using RAG (Retrieval Augmented Generation).
    
    ## Features
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

# CORS configuration for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the data models
class QueryRequest(BaseModel):
    question: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        example="Which types of proceedings are excluded from the application of this Act as per Section 3?",
        description="The question you want to ask the AI"
    )

class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    last_accessed: datetime
    question_count: int

class AnswerResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer")
    session_id: str = Field(..., description="The session ID for context tracking")
    session_info: SessionInfo = Field(..., description="Information about the current session")

    class Config:
        schema_extra = {
            "example": {
                "answer": "RAG (Retrieval Augmented Generation) is...",
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "session_info": {
                    "session_id": "123e4567-e89b-12d3-a456-426614174000",
                    "created_at": "2024-01-01T00:00:00",
                    "last_accessed": "2024-01-01T00:01:00",
                    "question_count": 1
                }
            }
        }

class SessionManager:
    def __init__(self, agent: RAGAgent, expiry_minutes: int = 30):
        self.agent = agent
        self.contexts: Dict[str, Dict] = {}
        self.expiry_minutes = expiry_minutes
        self._load_existing_sessions()
    
    def _load_existing_sessions(self):
        """Load existing sessions from vector store on startup"""
        try:
            if self.agent.session_index is None:
                logging.info("Session index not available, starting with empty session store")
                return
            random_vector = np.random.randn(1024)  # Generate vector of correct dimension
            normalized_vector = (random_vector / np.linalg.norm(random_vector)).tolist()
            
            existing_sessions = self.agent.session_index.query(
                vector=normalized_vector,
                top_k=1000,
                include_metadata=True
            )
            
            if existing_sessions and hasattr(existing_sessions, 'matches'):
                for session in existing_sessions.matches:
                    try:
                        session_id = session.id
                        session_data = json.loads(session.metadata['session_data'])
                        # Convert stored strings back to datetime objects
                        if isinstance(session_data.get('created_at'), str):
                            session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
                        if isinstance(session_data.get('last_accessed'), str):
                            session_data['last_accessed'] = datetime.fromisoformat(session_data['last_accessed'])
                        if isinstance(session_data.get('expiry'), str):
                            session_data['expiry'] = datetime.fromisoformat(session_data['expiry'])
                        self.contexts[session_id] = session_data
                    except Exception as e:
                        logging.error(f"Error loading session {session_id}: {e}")
                        continue
                        
                logging.info(f"Loaded {len(self.contexts)} existing sessions")
        except Exception as e:
            logging.error(f"Error loading existing sessions: {e}")

    def create_session(self) -> str:
        """Create a new session with initial state"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session_data = {
            'context': None,
            'expiry': now + timedelta(minutes=self.expiry_minutes),
            'created_at': now,
            'last_accessed': now,
            'updated_at': now,
            'question_count': 0,
            'chat_history': [],  # Store full conversation history
            'session_state': 'active'
        }
        
        self.contexts[session_id] = session_data
        
        try:
            self.agent.store_session(session_id, session_data)
            logging.info(f"New session {session_id} created and persisted")
        except Exception as e:
            logging.error(f"Error persisting new session {session_id}: {e}")
        
        return session_id

    def get_context(self, session_id: str) -> Optional[Dict]:
        # First check in-memory context
        if session_id not in self.contexts:
            # Try loading from persistent storage
            stored_session = self.agent.load_session(session_id)
            if stored_session:
                self.contexts[session_id] = stored_session
            else:
                raise HTTPException(status_code=404, detail="Session not found")
                
        context_data = self.contexts[session_id]
        if datetime.now() < context_data['expiry']:
            context_data['last_accessed'] = datetime.now()
            # Update persistent storage
            self.agent.store_session(session_id, context_data)
            return context_data['context']
        else:
            del self.contexts[session_id]  # Expired, delete the session
            self.agent.delete_session(session_id)  # Delete from persistent storage
            raise HTTPException(status_code=410, detail="Session expired")
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        if session_id in self.contexts:
            data = self.contexts[session_id]
            return SessionInfo(
                session_id=session_id,
                created_at=data['created_at'],
                last_accessed=data['last_accessed'],
                question_count=data['question_count']
            )
        return None

    def list_active_sessions(self) -> List[SessionInfo]:
        return [self.get_session_info(sid) for sid in self.contexts.keys() if self.get_session_info(sid)]

    def set_context(self, session_id: str, context: Dict):
        """Update session data and maintain chat history"""
        if session_id not in self.contexts:
            raise HTTPException(status_code=404, detail="Session not found")

        now = datetime.now()
        
        # Create chat entry
        chat_entry = {
            'question': context.get('last_question', ''),
            'answer': context.get('output', ''),
            'timestamp': context.get('timestamp', now.isoformat())
        }
        
        # Update session with new data while preserving history
        if 'chat_history' not in self.contexts[session_id]:
            self.contexts[session_id]['chat_history'] = []
            
        self.contexts[session_id].update({
            'last_accessed': now,
            'updated_at': now,
            'expiry': now + timedelta(minutes=self.expiry_minutes)
        })
        
        # Append new chat entry to history
        self.contexts[session_id]['chat_history'].append(chat_entry)
        
        try:
            if self.agent.session_index is not None:
                self.agent.store_session(session_id, self.contexts[session_id])
                logging.info(f"Session {session_id} updated with new chat entry")
        except Exception as e:
            logging.error(f"Error persisting session {session_id}: {e}")

    def cleanup_expired(self):
        current_time = datetime.now()
        expired_sessions = [sid for sid, data in self.contexts.items() if current_time > data['expiry']]
        for sid in expired_sessions:
            del self.contexts[sid]
        logging.info(f"Cleaned up {len(expired_sessions)} expired sessions")

agent = RAGAgent()
session_manager = SessionManager(agent=agent)

@app.get("/health", tags=["System"], summary="Health Check")
async def health_check():
    """Check the health status of the API."""
    return {"status": "healthy"}

@app.post("/ask", response_model=AnswerResponse, tags=["Questions"])
async def ask_question(
    request: QueryRequest,
    session_id: Optional[str] = Query(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Ask a question and get an AI-generated answer.
    - Provide a `session_id` to continue an existing conversation or let the API create a new session.
    """
    try:
        if not session_id:
            session_id = session_manager.create_session()
        
        result = agent.run(request.question, session_id)
        
        session_manager.set_context(session_id, {
            "output": result,
            "last_question": request.question,
            "timestamp": datetime.now().isoformat()
        })
        
        session_manager.contexts[session_id]['question_count'] += 1        
        background_tasks.add_task(session_manager.cleanup_expired)
        
        return {
            "answer": result,
            "session_id": session_id,
            "session_info": session_manager.get_session_info(session_id)
        }
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "type": type(e).__name__}
        )
    finally:
        gc.collect()

@app.delete("/session/{session_id}", tags=["Sessions"], summary="Clear a Session")
async def clear_session(session_id: str):
    """Clear a specific session context."""
    if session_id in session_manager.contexts:
        del session_manager.contexts[session_id]
        agent.clear_session_memory(session_id)
        return {"message": "Session cleared successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/sessions", response_model=List[SessionInfo], tags=["Sessions"], summary="List Active Sessions")
async def list_sessions():
    """List all active sessions."""
    return session_manager.list_active_sessions()

@app.get("/session/{session_id}", response_model=SessionInfo, tags=["Sessions"], summary="Get Session Info")
async def get_session_info(session_id: str):
    """Get information about a specific session."""
    info = session_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    return info


