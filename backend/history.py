import uuid
from langchain.schema import BaseChatMessageHistory, BaseMessage, HumanMessage, AIMessage
from typing import Optional, List, Dict
import pyodbc
import datetime
import json
import logging
from dotenv import load_dotenv
import os

load_dotenv()

VALID_USER_TYPES = ['client', 'lawyer']

class SQLChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, chat_id: str, user_id: str, connection_string: str):
        self.chat_id = chat_id
        self.connection_string = os.getenv('SQL_CONN_STRING')
    def _get_db_connection(self):
        return pyodbc.connect(self.connection_string)

    @property
    def messages(self) -> List[BaseMessage]:
        return self.get_chat_messages(self.user_id, self.chat_id)

    def get_chat_messages(self, user_id: str, chat_id: str) -> List[BaseMessage]:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT [Message], [MessageType], [Timestamp]
                FROM ChatMessages 
                WHERE [SenderId] = CAST(? AS UNIQUEIDENTIFIER)
                AND [ChatId] = CAST(? AS UNIQUEIDENTIFIER)
                ORDER BY [Timestamp]
            """
            cursor.execute(query, (user_id, chat_id))
            
            messages = []
            for row in cursor:
                if hasattr(row, 'Message') and hasattr(row, 'MessageType'):  # Check if columns exist
                    content = row.Message
                    msg_type = row.MessageType
                    if msg_type == 'HumanMessage':
                        messages.append(HumanMessage(content=content))
                    elif msg_type == 'AIMessage':
                        messages.append(AIMessage(content=content))
            return messages
            
        except Exception as e:
            logging.error(f"Error retrieving chat messages: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def is_valid_uuid(self, uuid_str: str) -> bool:
        try:
            uuid.UUID(uuid_str)
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    def add_message(self, message: BaseMessage) -> None:
        try:
            # Ensure valid UUIDs
            if not self.is_valid_uuid(self.chat_id):
                self.chat_id = str(uuid.uuid4())
            if not self.is_valid_uuid(self.user_id):
                self.user_id = str(uuid.uuid4())

            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO ChatMessages 
                (MessageId, ChatId, SenderId, Message, MessageType, Timestamp)
                VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            cursor.execute(query, (
                str(uuid.uuid4()),  # Generate new MessageId
                self.chat_id,
                self.user_id,
                message.content,
                message.__class__.__name__
            ))
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error adding message: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def clear(self) -> None:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM ChatMessages WHERE UserId = ? AND ChatId = ?"
            cursor.execute(query, (self.user_id, self.chat_id))
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error clearing messages: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def create_customer(self, customer_id: str, name: str) -> bool:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO Customers (CustomerId, CustomerName, ContactInfo, CreatedAt)
                VALUES (?, ?, ?, ?)
            """
            contact_info = json.dumps({}) 
            cursor.execute(query, (
                customer_id,
                name,
                contact_info,
                datetime.datetime.utcnow()
            ))
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error creating customer: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def create_lawyer(self, lawyer_id: str, name: str) -> bool:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # First insert into Lawyers table
            lawyer_query = """
                INSERT INTO Lawyers (LawyerId, LawyerName, ContactInfo, CreatedAt)
                VALUES (?, ?, ?, ?);
                SELECT SCOPE_IDENTITY();
            """
            contact_info = json.dumps({})
            cursor.execute(lawyer_query, (
                lawyer_id,
                name,
                contact_info,
                datetime.datetime.utcnow()
            ))
            
            # Get the auto-generated LawyerId
            lawyer_store_id = cursor.fetchone()[0]
            
            # Then insert into LawyerStore table
            lawyer_store_query = """
                INSERT INTO LawyerStore (
                    LawyerId, LawyerName, Email, CreatedAt, 
                    Specialization, Experience, Rating, Location, Contact
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(lawyer_store_query, (
                lawyer_store_id,  # Use the auto-generated ID
                name,
                '',  # Email - can be updated later
                datetime.datetime.utcnow(),
                'General',  # Default specialization
                '0',  # Default experience
                '0.0',  # Default rating
                '',  # Default location
                ''   # Default contact
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error creating lawyer: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def create_user(self, user_id, email: str, name: str, password: str, role: str) -> bool:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()            
    
            user_query = """
                INSERT INTO Users (UserId, UserName, Email, UserType, CreatedAt)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(user_query, (user_id, name, email, role, datetime.datetime.utcnow()))
            
            # Create user profile
            profile_query = """
                INSERT INTO UserProfiles (UserId)
                VALUES (?)
            """
            cursor.execute(profile_query, (user_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_user(self, email: str) -> Optional[Dict]:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM Users WHERE Email = ?"
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'user_id': row.UserId,
                    'name': row.UserName,
                    'email': row.Email,
                    'created_at': row.CreatedAt
                }
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_chats(self, user_id: str) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT DISTINCT cm1.ChatId, 
                    (SELECT TOP 1 [Message] FROM ChatMessages cm2 
                     WHERE cm2.ChatId = cm1.ChatId 
                     ORDER BY [Timestamp] DESC) as LastMessage,
                    (SELECT TOP 1 [Timestamp] FROM ChatMessages cm3 
                     WHERE cm3.ChatId = cm1.ChatId 
                     ORDER BY [Timestamp] DESC) as LastTimestamp,
                    COUNT(*) as MessageCount
                FROM ChatMessages cm1
                WHERE [UserId] = ?
                GROUP BY ChatId
                ORDER BY LastTimestamp DESC
            """
            cursor.execute(query, (user_id,))
            
            chats = []
            for row in cursor.fetchall():
                chats.append({
                    'chat_id': row.ChatId,
                    'last_message': row.LastMessage[:100] if row.LastMessage else '',
                    'last_timestamp': row.LastTimestamp.isoformat() if row.LastTimestamp else None,
                    'message_count': row.MessageCount
                })
            return chats
            
        except Exception as e:
            logging.error(f"Error retrieving user chats: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def check_email_exist(self, email: str) -> bool:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM Users WHERE Email = ?"
            cursor.execute(query, (email,))
            return cursor.fetchone() is not None
            
        except Exception as e:
            logging.error(f"Error checking email: {e}")
            return False
        finally:
            cursor.close()
            conn.close()