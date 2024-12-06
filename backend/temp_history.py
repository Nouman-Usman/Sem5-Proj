import uuid
from langchain.schema import BaseChatMessageHistory, BaseMessage, _message_to_dict, HumanMessage, AIMessage
from typing import Optional, List, Dict  # Add Dict to imports
import pyodbc  # Add pyodbc import
from dotenv import load_dotenv
import os
import datetime
import json
import logging
from langchain.schema import messages_from_dict
from pprint import pprint
load_dotenv()

# Connection string for MS SQL
connection_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'  # Local server
    'DATABASE=Apna_Waqeel;'  # Database name
    'Trusted_Connection=Yes;'  # Equivalent to Integrated Security=True
)

class AzureTableChatMessageHistory(BaseChatMessageHistory):
    def __init__(
            self,
            chat_id: str,
            user_id: str,
            connection_string: str = connection_string,
            key_prefix: str = "chat_history:"
        ):
        self.chat_id = chat_id  # Changed from chat_id
        self.user_id = user_id
        self.connection_string = connection_string
        self.key_prefix = key_prefix
        
        # Establish connection
        self.connection = pyodbc.connect(self.connection_string)
        self.cursor = self.connection.cursor()

    def _get_message_partition_key(self) -> str:
        return f"chat_history:{self.user_id}:{self.chat_id}"
        
    def _get_session_partition_key(self) -> str:
        return f"session:{self.user_id}"

    @property
    def key(self) -> str:
        """Build partition key in format chat_history:user_id:chat_id"""
        return f"{self.key_prefix}{self.user_id}:{self.chat_id}"

    @property 
    def messages(self) -> List[BaseMessage]:
        """Get messages for current chat"""
        return self.get_chat_messages(self.user_id, self.chat_id)

    def get_chat_messages(self, user_id: str, chat_id: str) -> List[BaseMessage]:
        """Retrieve all messages for a specific chat"""
        try:
            query = f"SELECT * FROM ChatMessages WHERE user_id = '{user_id}' AND chat_id = '{chat_id}' ORDER BY timestamp"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            messages = []
            for row in rows:
                content = row.content
                if not content:
                    continue
                msg_type = row.message_type
                if msg_type == 'HumanMessage':
                    messages.append(HumanMessage(content=content))
                elif msg_type == 'AIMessage':
                    messages.append(AIMessage(content=content))
                logging.info(f"Retrieved {msg_type}: {content[:50]}...")
            logging.info(f"Retrieved {len(messages)} messages for chat {chat_id}")
            return messages
        except Exception as e:
            logging.error(f"Error retrieving chat messages: {e}")
            raise

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat history"""
        try:
            timestamp = datetime.datetime.utcnow()
            message_id = f"{self.chat_id}_{timestamp.isoformat()}"
            
            # Ensure message has content
            if not message.content:
                logging.warning("Attempted to add empty message")
                return
                
            query = """
                INSERT INTO ChatMessages (PartitionKey, RowKey, user_id, chat_id, timestamp, message_type, content)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (
                self._get_message_partition_key(),
                message_id,
                self.user_id,
                self.chat_id,
                timestamp,
                message.__class__.__name__,
                message.content
            ))
            self.connection.commit()
            logging.info(f"Added {message.__class__.__name__} to chat {self.chat_id}: {message.content[:50]}...")
        except Exception as e:
            logging.error(f"Error adding message: {e}")
            raise

    def clear(self) -> None:
        try:
            query = f"DELETE FROM ChatMessages WHERE PartitionKey = '{self.key}'"
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            print(f"Error clearing messages: {e}")

    def get_user_chats(self, user_id: str) -> List[str]:
        """Retrieve all chat IDs for a given user"""
        try:
            query = f"SELECT DISTINCT chat_id FROM ChatMessages WHERE user_id = '{user_id}'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            chat_ids = [row.chat_id for row in rows]
            logging.info(f"Found {len(chat_ids)} chats for user {user_id}")
            return chat_ids
        except Exception as e:
            logging.error(f"Error retrieving chats: {e}")
            raise  # Propagate error for better handling

    def check_chat_exists(self, user_id: str, chat_id: str) -> bool:
        """Check if a chat exists across all relevant tables"""
        try:
            query = f"SELECT 1 FROM ChatMessages WHERE user_id = '{user_id}' AND chat_id = '{chat_id}'"
            self.cursor.execute(query)
            exists = self.cursor.fetchone() is not None
            return exists
        except Exception as e:
            logging.error(f"Error in check_chat_exists: {e}")
            return False

    def load_user_sessions(self, user_id: str) -> List[dict]:
        """Load all sessions for a given user"""
        try:
            query = f"SELECT SessionData FROM UserSessions WHERE user_id = '{user_id}'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            sessions = [json.loads(row.SessionData) for row in rows]
            return sessions
        except Exception as e:
            print(f"Error loading user sessions: {e}")
            return []

    def store_session_data(self, session_data: dict):
        query = """
            INSERT INTO UserSessions (PartitionKey, RowKey, user_id, chat_id, timestamp, session_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(query, (
            self._get_session_partition_key(),
            self.chat_id,
            self.user_id,
            self.chat_id,
            datetime.datetime.utcnow(),
            json.dumps(session_data)
        ))
        self.connection.commit()

    def store_lawyer_recommendation(self, chat_id: str, lawyer_data: dict):
        """Store lawyer recommendation for a chat"""
        query = """
            INSERT INTO LawyerRecommendations (PartitionKey, RowKey, user_id, chat_id, timestamp, lawyer_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            self.cursor.execute(query, (
                f"lawyer_rec:{self.user_id}:{chat_id}",
                str(uuid.uuid4()),
                self.user_id,
                chat_id,
                datetime.datetime.utcnow(),
                json.dumps(lawyer_data)
            ))
            self.connection.commit()
            logging.info(f"Stored lawyer recommendation for chat {chat_id}")
        except Exception as e:
            logging.error(f"Error storing lawyer recommendation: {e}")
            raise

    def store_metadata(self, chat_id: str, metadata: dict):
        """Store metadata (lawyers and references) for a chat"""
        try:
            query = """
                INSERT INTO ChatMetadata (PartitionKey, RowKey, user_id, chat_id, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (
                f"metadata:{self.user_id}:{chat_id}",
                str(uuid.uuid4()),
                self.user_id,
                chat_id,
                datetime.datetime.utcnow(),
                json.dumps(metadata)
            ))
            self.connection.commit()
            logging.info(f"Stored metadata for chat {chat_id}")
        except Exception as e:
            logging.error(f"Error storing metadata: {e}")
            raise

    def get_metadata(self, chat_id: str) -> Optional[dict]:
        """Retrieve metadata for a chat including both lawyers and references"""
        try:
            query = f"SELECT TOP 1 metadata FROM ChatMetadata WHERE PartitionKey = 'metadata:{self.user_id}:{chat_id}' ORDER BY timestamp DESC"
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            if row and row.metadata:
                metadata = json.loads(row.metadata)
                return {
                    'lawyers': metadata.get('lawyers', []),
                    'references': metadata.get('references', []),
                    'category': metadata.get('category', ''),
                    'timestamp': row.timestamp.isoformat() if row.timestamp else None
                }
            return None
        except Exception as e:
            logging.error(f"Error retrieving metadata: {e}")
            return None

    def get_chat_topics(self, user_id: str) -> List[Dict]:
        """Retrieve all chat topics for a given user"""
        try:
            query = f"SELECT chat_id, topic, timestamp FROM ChatTopics WHERE PartitionKey = 'chat_topic:{user_id}'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            topics = [{'chat_id': row.chat_id, 'topic': row.topic, 'timestamp': row.timestamp} for row in rows]
            return topics
        except Exception as e:
            logging.error(f"Error retrieving chat topics: {e}")
            return []

    def if_chat_exist(self, user_id: str, chat_id: str) -> bool:
        """Check if chat exists for a given user"""
        try:
            query = f"SELECT 1 FROM ChatMessages WHERE PartitionKey = '{self._get_message_partition_key()}' AND chat_id = '{chat_id}'"
            self.cursor.execute(query)
            exists = self.cursor.fetchone() is not None
            return exists
        except Exception as e:
            logging.error(f"Error checking chat existence: {e}")
            return False

    def create_user(self, email: str, name: str, password: str, role: str) -> bool:
        """Create a new user"""
        try:
            query = """
                INSERT INTO Users (PartitionKey, RowKey, name, password, created_at)
                VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (
                role,
                email,
                name,
                password,  # Note: Should be hashed in production
                datetime.datetime.utcnow()
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return False

    def create_customer(self, user_id: str, subscription: str) -> bool:
        """Create a new customer record"""
        try:
            query = """
                INSERT INTO Customers (PartitionKey, RowKey, current_subscription, created_at)
                VALUES (?, ?, ?, ?)
            """
            self.cursor.execute(query, (
                'customer',
                user_id,
                subscription,
                datetime.datetime.utcnow()
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error creating customer: {e}")
            return False

    def create_lawyer(self, user_id: str) -> bool:
        """Create a new lawyer record"""
        try:
            query = """
                INSERT INTO Lawyers (PartitionKey, RowKey, created_at)
                VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (
                'lawyer',
                user_id,
                datetime.datetime.utcnow()
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error creating lawyer: {e}")
            return False

    def get_user(self, email: str) -> Optional[Dict]:
        """Retrieve user by email"""
        try:
            query = f"SELECT * FROM Users WHERE RowKey = '{email}'"
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            if row:
                return {
                    'email': row.RowKey,
                    'name': row.name,
                    'role': row.PartitionKey,
                    'created_at': row.created_at
                }
            return None
        except Exception as e:
            logging.error(f"Error retrieving user: {e}")
            return None

if __name__ == "__main__":
    user_id = "test_user"
    chat_id = "test_session"
    user = AzureTableChatMessageHistory(chat_id="test_session", user_id="test_user")
    # print (user.get_chat_messages(chat_id=chat_id, user_id=user_id))