import pyodbc
import logging
from datetime import datetime
import json
import uuid
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

VALID_USER_TYPES = {
    'client': 'Customer',  # Map frontend role to database UserType
    'lawyer': 'Lawyer'
}

class Database:
    def __init__(self):
        self.connection_string = os.getenv('SQL_CONN_STRING')

    def get_connection(self):
        return pyodbc.connect(self.connection_string)

class UserCRUD(Database):
    def create(self, username: str, email: str, user_type: str, password: str) -> Optional[str]:
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            user_id = str(uuid.uuid4())
            profile_id = str(uuid.uuid4())

            # Map the user type correctly
            db_user_type = VALID_USER_TYPES.get(user_type.lower())
            if not db_user_type:
                raise ValueError(f"Invalid user type: {user_type}")
            
            logging.info(f"Creating user: {email}")
            
            # Check email existence
            cursor.execute("SELECT 1 FROM Users WHERE Email = ?", (email,))
            if cursor.fetchone():
                raise ValueError("Email already exists")
            user_query = """
                INSERT INTO Users (UserId, UserName, Email, UserType, PasswordHash, CreatedAt)
                VALUES (CAST(? AS UNIQUEIDENTIFIER), ?, ?, ?, ?, GETDATE())
            """
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute(user_query, (user_id, username, email, db_user_type, password_hash))
            conn.commit()

            # Create profile
            profile_query = """
                INSERT INTO UserProfiles (ProfileId, UserId)
                VALUES (CAST(? AS UNIQUEIDENTIFIER), CAST(? AS UNIQUEIDENTIFIER))
            """
            cursor.execute(profile_query, (profile_id, user_id))
            conn.commit()

            if user_type.lower() == 'lawyer':
                license_id = f"TBD-{str(uuid.uuid4())[:8]}"
                lawyer_query = """
                    INSERT INTO LawyerDetails 
                    (LawyerId, Specialization, Experience, LicenseNumber, Rating, Location)
                    VALUES (CAST(? AS UNIQUEIDENTIFIER), ?, ?, ?, ?, ?)
                """
                cursor.execute(lawyer_query, (user_id, 'General', 3, license_id, 2.0, 'TBD'))
                conn.commit()                
            elif user_type.lower() == 'client':
                customer_query = """
                    INSERT INTO Customers (CustomerId, CustomerName, ContactInfo, CreatedAt)
                    VALUES (CAST(? AS UNIQUEIDENTIFIER), ?, ?, GETDATE())
                """
                cursor.execute(customer_query, (user_id, username, '{}'))
                conn.commit()
            logging.info(f"Successfully created user with ID: {user_id}")
            return user_id
        except Exception as e:
            logging.error(f"Error in create user: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    def read(self, user_id: str) -> Optional[Dict]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM Users WHERE UserId = ?"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'user_id': row.UserId,
                    'username': row.UserName,
                    'email': row.Email,
                    'user_type': row.UserType,
                    'created_at': row.CreatedAt
                }
            return None
        except Exception as e:
            logging.error(f"Error reading user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update(self, user_id: str, username: str = None, email: str = None) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            if username:
                updates.append("UserName = ?")
                params.append(username)
            if email:
                updates.append("Email = ?")
                params.append(email)
            
            if not updates:
                return True
                
            params.append(user_id)
            query = f"UPDATE Users SET {', '.join(updates)} WHERE UserId = ?"
            cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def delete(self, user_id: str) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            # Delete from LawyerSpecializationMapping
            cursor.execute("""
                DELETE FROM LawyerSpecializationMapping 
                WHERE LawyerId = ?
            """, (user_id,))
            
            # Delete from LawyerDetails
            cursor.execute("""
                DELETE FROM LawyerDetails 
                WHERE LawyerId = ?
            """, (user_id,))
            
            # Delete from UserProfiles
            cursor.execute("""
                DELETE FROM UserProfiles 
                WHERE UserId = ?
            """, (user_id,))
            
            # Delete from Users
            cursor.execute("""
                DELETE FROM Users 
                WHERE UserId = ?
            """, (user_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logging.error(f"Error deleting user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def check_credentials(self, email: str, password: str) -> Optional[Dict]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT UserId, UserName, Email, UserType, PasswordHash 
                FROM Users 
                WHERE Email = ?
            """
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            
            if row and check_password_hash(row.PasswordHash, password):
                return {
                    'user_id': row.UserId,
                    'username': row.UserName,
                    'email': row.Email,
                    'user_type': row.UserType
                }
            return None
            
        except Exception as e:
            logging.error(f"Error checking credentials: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def update_password(self, user_id: str, new_password: str) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            query = "UPDATE Users SET PasswordHash = ? WHERE UserId = ?"
            cursor.execute(query, (password_hash, user_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating password: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

class CustomerCRUD(Database):
    def create(self, name: str, contact_info: Dict) -> Optional[int]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO Customers (CustomerName, ContactInfo, CreatedAt)
                VALUES (?, ?, GETDATE());
                SELECT SCOPE_IDENTITY();
            """
            cursor.execute(query, (name, json.dumps(contact_info)))
            customer_id = cursor.fetchone()[0]
            conn.commit()
            return customer_id
        except Exception as e:
            logging.error(f"Error creating customer: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def read(self, customer_id: int) -> Optional[Dict]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM Customers WHERE CustomerId = ?"
            cursor.execute(query, (customer_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'customer_id': row.CustomerId,
                    'name': row.CustomerName,
                    'contact_info': json.loads(row.ContactInfo),
                    'created_at': row.CreatedAt
                }
            return None
        except Exception as e:
            logging.error(f"Error reading customer: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

class LawyerCRUD(Database):
    def create(self, name: str, contact_info: Dict) -> Optional[int]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO Lawyers (LawyerName, ContactInfo, CreatedAt)
                VALUES (?, ?, GETDATE());
                SELECT SCOPE_IDENTITY();
            """
            cursor.execute(query, (name, json.dumps(contact_info)))
            lawyer_id = cursor.fetchone()[0]
            conn.commit()
            return lawyer_id
        except Exception as e:
            logging.error(f"Error creating lawyer: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def read(self, lawyer_id: int) -> Optional[Dict]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM Lawyers WHERE LawyerId = ?"
            cursor.execute(query, (lawyer_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'lawyer_id': row.LawyerId,
                    'name': row.LawyerName,
                    'contact_info': json.loads(row.ContactInfo),
                    'created_at': row.CreatedAt
                }
            return None
        except Exception as e:
            logging.error(f"Error reading lawyer: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    # Add similar update and delete methods...

class ChatSessionCRUD(Database):
    def ensure_system_user_exists(self) -> str:
        """Ensure system user exists and return its ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            system_id = "00000000-0000-0000-0000-000000000000"
            
            # Check if system user exists
            cursor.execute("""
                SELECT UserId FROM Users 
                WHERE UserId = CAST(? AS UNIQUEIDENTIFIER)
            """, (system_id,))
            
            if not cursor.fetchone():
                # Create system user
                cursor.execute("""
                    INSERT INTO Users (UserId, UserName, Email, UserType, PasswordHash, CreatedAt)
                    VALUES (
                        CAST(? AS UNIQUEIDENTIFIER),
                        'System',
                        'system@example.com',
                        'System',
                        'not_used',
                        GETDATE()
                    )
                """, (system_id,))
                conn.commit()
            
            return system_id
        except Exception as e:
            logging.error(f"Error ensuring system user: {e}")
            if 'conn' in locals():
                conn.rollback()
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def create(self, initiator_id: str, recipient_id: str) -> Optional[str]:
        try:
            if recipient_id == "00000000-0000-0000-0000-000000000000":
                recipient_id = self.ensure_system_user_exists()
                if not recipient_id:
                    raise Exception("Failed to ensure system user exists")

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ChatId FROM ChatSessions 
                WHERE InitiatorId = CAST(? AS UNIQUEIDENTIFIER) 
                AND RecipientId = CAST(? AS UNIQUEIDENTIFIER)
            """, (initiator_id, recipient_id))            
            existing = cursor.fetchone()
            if existing:
                return existing[0]            
            chat_id = str(uuid.uuid4())
            query = """
                INSERT INTO ChatSessions 
                (ChatId, InitiatorId, RecipientId, Status, StartTime)
                VALUES (CAST(? AS UNIQUEIDENTIFIER), CAST(? AS UNIQUEIDENTIFIER), 
                        CAST(? AS UNIQUEIDENTIFIER), 'Active', GETDATE())
            """
            cursor.execute(query, (chat_id, initiator_id, recipient_id))
            conn.commit()
            return chat_id

        except Exception as e:
            logging.error(f"Error creating chat session: {e}")
            if 'conn' in locals():
                conn.rollback()
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def delete(self, chat_id: str) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("BEGIN TRANSACTION")
            
            # Delete chat messages first
            cursor.execute("""
                DELETE FROM ChatMessages 
                WHERE ChatId = ?
            """, (chat_id,))
            
            # Delete chat session
            cursor.execute("""
                DELETE FROM ChatSessions 
                WHERE ChatId = ?
            """, (chat_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logging.error(f"Error deleting chat session: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

class ChatMessageCRUD(Database):
    def is_valid_uuid(self, uuid_str: str) -> bool:
        try:
            uuid.UUID(str(uuid_str))
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    def create(self, chat_id: str, sender_id: str, message: str, message_type: str) -> Optional[str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # First verify chat session exists
            cursor.execute("""
                SELECT 1 FROM ChatSessions WHERE ChatId = ?
            """, (chat_id,))
            
            if not cursor.fetchone():
                raise ValueError(f"Chat session {chat_id} does not exist")
            
            message_id = str(uuid.uuid4())
            query = """
                INSERT INTO ChatMessages 
                (MessageId, ChatId, SenderId, Message, MessageType, Timestamp)
                VALUES (?, ?, ?, ?, ?, GETDATE())
            """
            cursor.execute(query, (message_id, chat_id, sender_id, message, message_type))
            conn.commit()
            return message_id
            
        except Exception as e:
            logging.error(f"Error creating message: {e}")
            if 'conn' in locals():
                conn.rollback()
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get_chat_messages(self, user_id: str, chat_id: str) -> Optional[List[Dict]]:
        """Get messages for a specific chat"""
        try:
            if not chat_id or not user_id:
                return []
                
            if not self.is_valid_uuid(chat_id) or not self.is_valid_uuid(user_id):
                logging.error(f"Invalid UUID format - chat_id: {chat_id}, user_id: {user_id}")
                return []

            conn = self.get_connection()
            cursor = conn.cursor()
            
            chat_query = """
                SELECT cm.Message, cm.MessageType, cm.Timestamp 
                FROM ChatMessages cm
                INNER JOIN ChatSessions cs ON cs.ChatId = cm.ChatId
                WHERE cs.ChatId = ?
                AND (cs.InitiatorId = ? OR cs.RecipientId = ?)
                ORDER BY cm.Timestamp DESC
            """
            
            logging.info(f"Executing query with chat_id: {chat_id}, user_id: {user_id}")
            cursor.execute(chat_query, (chat_id, user_id, user_id))            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'content': row.Message,
                    'role': 'user' if row.MessageType == 'HumanMessage' else 'assistant',
                    'timestamp': row.Timestamp.isoformat() if row.Timestamp else None
                })
            
            logging.info(f"Retrieved {len(messages)} messages")
            return messages
            
        except Exception as e:
            logging.error(f"Error getting chat messages: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

class LawyerDetailsCRUD(Database):
    def create(self, lawyer_id: str, specialization: str, experience: int, 
              license_number: str, location: str, specializations: List[str] = None) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("BEGIN TRANSACTION")
            
            # Check for Lawyer with proper case
            cursor.execute("""
                SELECT UserType FROM Users 
                WHERE UserId = ? AND UserType = 'Lawyer'
            """, (lawyer_id,))
            
            if not cursor.fetchone():
                raise Exception("User does not exist or is not a lawyer")
            
            # Create or update lawyer details
            details_query = """
                MERGE INTO LawyerDetails AS target
                USING (SELECT ? AS LawyerId) AS source
                ON target.LawyerId = source.LawyerId
                WHEN MATCHED THEN
                    UPDATE SET 
                        Specialization = ?,
                        Experience = ?,
                        LicenseNumber = ?,
                        Location = ?
                WHEN NOT MATCHED THEN
                    INSERT (LawyerId, Specialization, Experience, LicenseNumber, Rating, Location)
                    VALUES (?, ?, ?, ?, 0.0, ?);
            """
            cursor.execute(details_query, (
                lawyer_id, specialization, experience, license_number, location,
                lawyer_id, specialization, experience, license_number, location
            ))
            
            # Add specializations if provided
            if specializations:
                for spec in specializations:
                    spec_id = self._get_or_create_specialization(cursor, spec)
                    
                    # Create mapping
                    mapping_query = """
                        INSERT INTO LawyerSpecializationMapping (LawyerId, SpecializationId)
                        VALUES (?, ?)
                    """
                    cursor.execute(mapping_query, (lawyer_id, spec_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            logging.error(f"Error creating lawyer details: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _get_or_create_specialization(self, cursor, spec_name: str) -> str:
        # Check if specialization exists
        cursor.execute("""
            SELECT SpecializationId FROM LawyerSpecializations 
            WHERE Name = ?
        """, (spec_name,))
        row = cursor.fetchone()
        
        if row:
            return row.SpecializationId
            
        # Create new specialization
        spec_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO LawyerSpecializations (SpecializationId, Name)
            VALUES (?, ?)
        """, (spec_id, spec_name))
        
        return spec_id

class LawyerSpecializationCRUD(Database):
    def create(self, name: str) -> Optional[str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            spec_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO LawyerSpecializations (SpecializationId, Name)
                VALUES (?, ?)
            """
            cursor.execute(query, (spec_id, name))
            conn.commit()
            return spec_id
        except Exception as e:
            logging.error(f"Error creating specialization: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    # Add read, update, delete methods...

# Example usage:
# user_crud = UserCRUD()
# lawyer_crud = LawyerCRUD()
# chat_crud = ChatSessionCRUD()
# messages_crud = ChatMessageCRUD()
# lawyer_details_crud = LawyerDetailsCRUD()
# specializations_crud = LawyerSpecializationCRUD()
