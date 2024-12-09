import pyodbc
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn_string = os.getenv('SQL_CONN_STRING')
        
    def get_connection(self):
        return pyodbc.connect(self.conn_string)

    def create_user(self, name, email, password, role):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO [User] (Name, Email, Password, Role) 
                      VALUES (?, ?, ?, ?)"""
            cursor.execute(query, (name, email, password, role))
            conn.commit()
            return cursor.rowcount

    def get_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [User] WHERE UserId = ?", user_id)
            return cursor.fetchone()

    def update_user(self, user_id, name, email, password, role):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE [User] 
                      SET Name = ?, Email = ?, Password = ?, Role = ?
                      WHERE UserId = ?"""
            cursor.execute(query, (name, email, password, role, user_id))
            conn.commit()
            return cursor.rowcount

    def delete_user(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [User] WHERE UserId = ?", user_id)
            conn.commit()
            return cursor.rowcount

    # Client CRUD operations
    def create_client(self, user_id, cnic, contact, location, credits=0, profile_picture=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO Client (UserId, CNIC, Contact, Location, Credits, ProfilePicture)
                      VALUES (?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (user_id, cnic, contact, location, credits, profile_picture))
            conn.commit()
            return cursor.rowcount

    def get_client(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client WHERE ClientId = ?", client_id)
            return cursor.fetchone()

    def update_client(self, client_id, cnic, contact, location, credits=0, profile_picture=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Client 
                      SET CNIC = ?, Contact = ?, Location = ?, Credits = ?, ProfilePicture = ?
                      WHERE ClientId = ?"""
            cursor.execute(query, (cnic, contact, location, credits, profile_picture, client_id))
            conn.commit()
            return cursor.rowcount

    def delete_client(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Client WHERE ClientId = ?", client_id)
            conn.commit()
            return cursor.rowcount

    # Lawyer CRUD operations
    def create_lawyer(self, user_id, cnic, license_number, location, experience, ratings=None, 
                     paid=False, expiry_date=None, recommended=0, click_ratio=0.0):
        # Validate inputs
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a positive integer")
        if ratings is not None and (ratings < 0 or ratings > 5):
            raise ValueError("Ratings must be between 0 and 5")
        if not isinstance(cnic, str) or len(cnic) > 20:
            raise ValueError("Invalid CNIC format")
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO Lawyer (UserId, CNIC, LicenseNumber, Location, Experience, 
                      Ratings, Paid, ExpiryDate, Recommended, ClickRatio)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (user_id, cnic, license_number, location, experience,
                                 ratings, paid, expiry_date, recommended, click_ratio))
            conn.commit()
            return cursor.rowcount

    def get_lawyer(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer WHERE LawyerId = ?", lawyer_id)
            return cursor.fetchone()

    def update_lawyer(self, lawyer_id, cnic, license_number, location, experience, 
                     ratings=None, paid=False, expiry_date=None, recommended=0, click_ratio=0.0):
        # Validate inputs
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a positive integer")
        if ratings is not None and (ratings < 0 or ratings > 5):
            raise ValueError("Ratings must be between 0 and 5")
        if not isinstance(cnic, str) or len(cnic) > 20:
            raise ValueError("Invalid CNIC format")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Lawyer 
                      SET CNIC = ?, LicenseNumber = ?, Location = ?, Experience = ?,
                          Ratings = ?, Paid = ?, ExpiryDate = ?, Recommended = ?, 
                          ClickRatio = ?
                      WHERE LawyerId = ?"""
            cursor.execute(query, (cnic, license_number, location, experience, ratings,
                                 paid, expiry_date, recommended, click_ratio, lawyer_id))
            conn.commit()
            return cursor.rowcount

    def delete_lawyer(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Lawyer WHERE LawyerId = ?", lawyer_id)
            conn.commit()
            return cursor.rowcount

    def get_lawyer_with_details(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT l.*, u.Name, u.Email 
                FROM Lawyer l
                JOIN [User] u ON l.UserId = u.UserId
                WHERE l.LawyerId = ?
            """
            cursor.execute(query, lawyer_id)
            return cursor.fetchone()

    def get_lawyers_by_experience(self, min_experience):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT l.*, u.Name, u.Email 
                FROM Lawyer l
                JOIN [User] u ON l.UserId = u.UserId
                WHERE l.Experience >= ?
                ORDER BY l.Experience DESC, l.Ratings DESC
            """
            cursor.execute(query, min_experience)
            return cursor.fetchall()

    # Session CRUD operations
    def create_session(self, user_id, topic):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO Sessions (UserId, Topic, Time, Active)
                      VALUES (?, ?, GETDATE(), 1)"""
            cursor.execute(query, (user_id, topic))
            conn.commit()
            return cursor.rowcount

    def get_session(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sessions WHERE SessionId = ?", session_id)
            return cursor.fetchone()

    def update_session(self, session_id, topic, active=True):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Sessions 
                      SET Topic = ?, Active = ?
                      WHERE SessionId = ?"""
            cursor.execute(query, (topic, active, session_id))
            conn.commit()
            return cursor.rowcount

    def delete_session(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Sessions WHERE SessionId = ?", session_id)
            conn.commit()
            return cursor.rowcount

    # ChatMessages CRUD operations
    def create_chat_message(self, session_id, message, msg_type, references=None, recommended_lawyers=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO ChatMessages (SessionId, Message, Type, Time, References, RecommendedLawyers)
                      VALUES (?, ?, ?, GETDATE(), ?, ?)"""
            cursor.execute(query, (session_id, message, msg_type, references, recommended_lawyers))
            conn.commit()
            return cursor.rowcount

    def get_chat_messages(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ChatMessages WHERE SessionId = ? ORDER BY Time", session_id)
            return cursor.fetchall()

    def update_chat_message(self, chat_id, message, msg_type, references=None, recommended_lawyers=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE ChatMessages 
                      SET Message = ?, Type = ?, References = ?, RecommendedLawyers = ?
                      WHERE ChatId = ?"""
            cursor.execute(query, (message, msg_type, references, recommended_lawyers, chat_id))
            conn.commit()
            return cursor.rowcount

    def delete_chat_message(self, chat_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ChatMessages WHERE ChatId = ?", chat_id)
            conn.commit()
            return cursor.rowcount

    def get_all_chat_messages(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ChatMessages ORDER BY Time")
            return cursor.fetchall()

    def create_subscription(self, client_id, subscription_type, expiry_date, remaining_credits):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO Subscription (ClientId, CurrentSubscription, ExpiryDate, RemainingCredits)
                      VALUES (?, ?, ?, ?)"""
            cursor.execute(query, (client_id, subscription_type, expiry_date, remaining_credits))
            conn.commit()
            return cursor.rowcount

    def get_subscription(self, subs_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Subscription WHERE SubsId = ?", subs_id)
            return cursor.fetchone()

    def update_subscription(self, subs_id, subscription_type, expiry_date, remaining_credits):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Subscription 
                      SET CurrentSubscription = ?, ExpiryDate = ?, RemainingCredits = ?
                      WHERE SubsId = ?"""
            cursor.execute(query, (subscription_type, expiry_date, remaining_credits, subs_id))
            conn.commit()
            return cursor.rowcount

    def delete_subscription(self, subs_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Subscription WHERE SubsId = ?", subs_id)
            conn.commit()
            return cursor.rowcount

    def get_all_subscriptions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Subscription")
            return cursor.fetchall()

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [User]")
            return cursor.fetchall()

    def get_all_clients(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client")
            return cursor.fetchall()

    def get_all_lawyers(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer")
            return cursor.fetchall()

    def get_all_sessions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sessions ORDER BY Time DESC")
            return cursor.fetchall()
