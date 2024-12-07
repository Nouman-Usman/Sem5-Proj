import pyodbc
import logging
from datetime import datetime
import json
import uuid
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

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
    def create(self, username: str, email: str, user_type: str) -> Optional[str]:
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            conn.autocommit = False  # Explicitly disable autocommit
            cursor = conn.cursor()
            user_id = str(uuid.uuid4())
            profile_id = str(uuid.uuid4())

            # Map the user type correctly
            db_user_type = VALID_USER_TYPES.get(user_type.lower())
            if not db_user_type:
                raise ValueError(f"Invalid user type: {user_type}")
            
            logging.info(f"Starting transaction for user creation: {email}")
            cursor.execute("BEGIN TRANSACTION")

            # Check email existence
            logging.info(f"Checking email existence: {email}")
            cursor.execute("SELECT 1 FROM Users WHERE Email = ?", (email,))
            if cursor.fetchone():
                raise ValueError("Email already exists")

            # Create user
            logging.info(f"Creating user record with ID: {user_id}")
            user_query = """
                INSERT INTO Users (UserId, UserName, Email, UserType, CreatedAt)
                VALUES (?, ?, ?, ?, GETDATE());
            """
            cursor.execute(user_query, (user_id, username, email, db_user_type))
            
            # Verify user creation immediately
            cursor.execute("SELECT 1 FROM Users WHERE UserId = ?", (user_id,))
            if not cursor.fetchone():
                raise Exception("User creation failed - no record found")

            # Create profile
            logging.info(f"Creating user profile for ID: {user_id}")
            profile_query = """
                INSERT INTO UserProfiles (ProfileId, UserId)
                VALUES (?, ?);
            """
            cursor.execute(profile_query, (profile_id, user_id))

            # Create role-specific records
            if user_type.lower() == 'lawyer':
                logging.info("Creating lawyer details")
                license_id = f"TBD-{str(uuid.uuid4())[:8]}"
                lawyer_query = """
                    INSERT INTO LawyerDetails 
                    (LawyerId, Specialization, Experience, LicenseNumber, Rating, Location)
                    VALUES (?, ?, ?, ?, ?, ?);
                """
                cursor.execute(lawyer_query, (
                    user_id,
                    'General',
                    3,
                    license_id,
                    2.0,
                    'TBD'
                ))
            elif user_type.lower() == 'client':
                logging.info("Creating customer record")
                customer_query = """
                    INSERT INTO Customers (CustomerId, CustomerName, ContactInfo, CreatedAt)
                    VALUES (CAST(? AS UNIQUEIDENTIFIER), ?, ?, GETDATE())
                """
                cursor.execute(customer_query, (
                    user_id,
                    username,
                    '{}',
                ))

            # Verify the user was created
            logging.info("Verifying user creation")
            cursor.execute("""
                SELECT COUNT(1) FROM Users 
                WHERE UserId = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result or result[0] == 0:
                logging.error("User verification failed before commit")
                raise Exception("User creation failed - verification error")

            logging.info("Verification successful, committing transaction")
            conn.commit()
            logging.info(f"Successfully created user with ID: {user_id}")
            
            return user_id

        except Exception as e:
            logging.error(f"Error in create user: {str(e)}")
            if conn:
                try:
                    logging.info("Rolling back transaction")
                    conn.rollback()
                except Exception as rollback_error:
                    logging.error(f"Rollback failed: {str(rollback_error)}")
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    logging.error(f"Error closing cursor: {str(e)}")
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logging.error(f"Error closing connection: {str(e)}")

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
    def create(self, initiator_id: str, recipient_id: str) -> Optional[str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            chat_id = str(uuid.uuid4())
            
            cursor.execute("BEGIN TRANSACTION")
            
            # Verify both users exist
            cursor.execute("""
                SELECT COUNT(*) FROM Users 
                WHERE UserId IN (?, ?)
            """, (initiator_id, recipient_id))
            
            if cursor.fetchone()[0] != 2:
                raise Exception("One or both users do not exist")
            
            # Create chat session
            query = """
                INSERT INTO ChatSessions 
                (ChatId, InitiatorId, RecipientId, Status, StartTime)
                VALUES (?, ?, ?, 'Active', GETDATE())
            """
            cursor.execute(query, (chat_id, initiator_id, recipient_id))
            
            conn.commit()
            return chat_id
        except Exception as e:
            conn.rollback()
            logging.error(f"Error creating chat session: {e}")
            return None
        finally:
            cursor.close()
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
    def create(self, chat_id: str, sender_id: str, message: str, message_type: str) -> Optional[str]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
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
            return None
        finally:
            cursor.close()
            conn.close()

    # Add read, update, delete methods...

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
