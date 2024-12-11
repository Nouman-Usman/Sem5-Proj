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

    def get_user_by_email(self, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM [User] WHERE Email = ?"
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            return row
    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM [User] WHERE UserId = ?"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return row
    def validate_user_input(self, name, email, password, role):
        if not isinstance(name, str) or len(name) > 100:
            raise ValueError("Invalid name format")
        if not isinstance(email, str) or len(email) > 255 or '@' not in email:
            raise ValueError("Invalid email format")
        if not isinstance(password, str) or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if role not in ['client', 'lawyer', 'system']:
            raise ValueError("Invalid role")
    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM [User] WHERE UserId = ?"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()    

    def create_user(self, name, email, password, role):
        # Validate inputs
        self.validate_user_input(name, email, password, role)
        
        # Check if email exists
        if self.get_user_by_email(email):
            raise ValueError("Email already exists")

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
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Client (UserId, CNIC, Contact, Location, Credits, ProfilePicture)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, cnic, contact, location, credits, profile_picture))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating client: {e}")
            return False

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
    def get_client_by_id(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client WHERE ClientId = ?", client_id)
            return cursor.fetchone()
        
    def delete_client(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Client WHERE ClientId = ?", client_id)
            conn.commit()
            return cursor.rowcount
    def get_client_by_user_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client WHERE UserId = ?", user_id)
            return cursor.fetchone()
    # Lawyer CRUD operations
    def create_lawyer(self, user_id, cnic, license_number, location, experience,
                     specialization, contact, email, paid=False, 
                     expiry_date=None, recommended=0, times_clicked=0, times_shown=0):
        # Input validations
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a positive integer")
        if not isinstance(cnic, str) or len(cnic) > 13:
            raise ValueError("Invalid CNIC format")
        if not isinstance(contact, str) or len(contact) > 11:
            raise ValueError("Invalid contact format")
        if not isinstance(email, str) or len(email) > 100 or '@' not in email:
            raise ValueError("Invalid email format")
        if not isinstance(specialization, str) or len(specialization) > 100:
            raise ValueError("Invalid specialization format")
        if ratings is not None and (not isinstance(ratings, (int, float)) or ratings < 0 or ratings > 5):
            raise ValueError("Ratings must be between 0 and 5")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO Lawyer (UserId, CNIC, LicenseNumber, Location, 
                      Experience, Specialization, Contact, Email, Paid, 
                      ExpiryDate, Recommended, TimesClicked, TimesShown)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (user_id, cnic, license_number, location, experience,
                                 specialization, contact, email, paid, 
                                 expiry_date, recommended, times_clicked, times_shown))
            conn.commit()
            return cursor.rowcount
    def get_lawyer_by_user_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer WHERE UserId = ?", user_id)
            return cursor.fetchone()

    def get_lawyer(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer WHERE LawyerId = ?", lawyer_id)
            return cursor.fetchone()

    def update_lawyer(self, lawyer_id, cnic, license_number, location, experience,
                     specialization, contact, email, paid=False, 
                     expiry_date=None, recommended=0, times_clicked=0, times_shown=0):
        # Input validations
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a positive integer")
        if not isinstance(cnic, str) or len(cnic) > 20:
            raise ValueError("Invalid CNIC format")
        if not isinstance(contact, str) or len(contact) > 20:
            raise ValueError("Invalid contact format")
        if not isinstance(email, str) or len(email) > 100 or '@' not in email:
            raise ValueError("Invalid email format")
        if not isinstance(specialization, str) or len(specialization) > 100:
            raise ValueError("Invalid specialization format")
        if ratings is not None and (not isinstance(ratings, (int, float)) or ratings < 0 or ratings > 5):
            raise ValueError("Ratings must be between 0 and 5")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Lawyer 
                      SET CNIC = ?, LicenseNumber = ?, Location = ?, Experience = ?,
                          Specialization = ?, Contact = ?, Email = ?, 
                          Paid = ?, ExpiryDate = ?, Recommended = ?,
                          TimesClicked = ?, TimesShown = ?
                      WHERE LawyerId = ?"""
            cursor.execute(query, (cnic, license_number, location, experience,
                                 specialization, contact, email, paid,
                                 expiry_date, recommended, times_clicked, 
                                 times_shown, lawyer_id))
            conn.commit()
            return cursor.rowcount

    def delete_lawyer(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Lawyer WHERE LawyerId = ?", lawyer_id)
            conn.commit()
            return cursor.rowcount
    def get_lawyer_by_id(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer WHERE LawyerId = ?", lawyer_id)
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

    def get_lawyers_by_specialization(self, specialization):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT l.*, u.Name
                FROM Lawyer l
                JOIN [User] u ON l.UserId = u.UserId
                WHERE l.Specialization = ?
                ORDER BY l.Ratings DESC, l.Experience DESC
            """
            cursor.execute(query, specialization)
            return cursor.fetchall()

    def get_top_rated_lawyers(self, limit=10):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT TOP (?) l.*, u.Name
                FROM Lawyer l
                JOIN [User] u ON l.UserId = u.UserId
                WHERE l.Ratings IS NOT NULL
                ORDER BY l.Ratings DESC, l.Experience DESC
            """
            cursor.execute(query, limit)
            return cursor.fetchall()

    # Session CRUD operations
    def create_session(self, user_id, topic):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # First verify user exists
                check_user_query = "SELECT 1 FROM [User] WHERE UserId = ?"
                cursor.execute(check_user_query, (user_id,))
                if not cursor.fetchone():
                    raise ValueError(f"User with ID {user_id} does not exist")
                query = """
                    INSERT INTO Sessions (UserId, Topic, Time, Active)
                    OUTPUT INSERTED.SessionId
                    VALUES (?, ?, GETDATE(), 1)
                """

                cursor.execute(query, (user_id, topic))
                query = "SELECT SCOPE_IDENTITY()"
                cursor.execute(query)
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else None
        except pyodbc.IntegrityError as e:
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error creating a new session: {str(e)}")

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
    def get_all_chat_sessions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sessions WHERE Active = 1")
            return cursor.fetchall()
    def get_chat_session_by_id(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sessions WHERE SessionId = ?", session_id)
            return cursor.fetchone()
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

    def get_chat_Topics(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # get chat topics and chat ids
            cursor.execute("SELECT Topic, ChatId FROM Sessions WHERE UserId = ?", user_id)

            return cursor.fetchone()
    
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
    def get_chat_messages_by_chat_id(self, chat_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ChatMessages WHERE ChatId = ?", chat_id)
            return cursor.fetchone()
    def get_chat_message_by_message_id(self, message_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ChatMessages WHERE MessageId = ?", message_id)
            return cursor.fetchone()
    def get_all_chat_messages(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ChatMessages ORDER BY Time")
            return cursor.fetchall()

    def create_subscription(self, user_id, subscription_type, expiry_date, remaining_credits=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO Subscription 
                      (UserId, CurrentSubscription, ExpiryDate, RemainingCredits)
                      VALUES (?, ?, ?, ?)"""
            cursor.execute(query, (user_id, subscription_type, expiry_date, remaining_credits))
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
    def get_current_subscription(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Subscription WHERE ClientId = ? ORDER BY ExpiryDate DESC", client_id)
            return cursor.fetchone()
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

    # New LawyerReview methods
    def create_lawyer_review(self, lawyer_id, client_id, stars, review_message=None):
        if not 1 <= stars <= 5:
            raise ValueError("Stars must be between 1 and 5")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """INSERT INTO LawyerReview 
                      (LawyerId, ClientId, Stars, ReviewMessage, ReviewTime)
                      VALUES (?, ?, ?, ?, GETDATE())"""
            cursor.execute(query, (lawyer_id, client_id, stars, review_message))
            conn.commit()
            return cursor.rowcount

    def get_lawyer_reviews(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """SELECT lr.*, u.Name as ClientName 
                      FROM LawyerReview lr
                      JOIN [User] u ON lr.ClientId = u.UserId
                      WHERE lr.LawyerId = ?
                      ORDER BY lr.ReviewTime DESC"""
            cursor.execute(query, (lawyer_id,))
            return cursor.fetchall()

    def update_lawyer_review(self, review_id, stars, review_message):
        if not 1 <= stars <= 5:
            raise ValueError("Stars must be between 1 and 5")
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE LawyerReview 
                      SET Stars = ?, ReviewMessage = ?
                      WHERE ReviewId = ?"""
            cursor.execute(query, (stars, review_message, review_id))
            conn.commit()
            return cursor.rowcount

    def delete_lawyer_review(self, review_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM LawyerReview WHERE ReviewId = ?", review_id)
            conn.commit()
            return cursor.rowcount
