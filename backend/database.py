import pyodbc
from datetime import datetime
import os
from dotenv import load_dotenv
import json

load_dotenv()


class Database:
    def __init__(self):
        self.conn_string = os.getenv("SQL_CONN_STRING")

    def get_connection(self):
        return pyodbc.connect(self.conn_string)

    # ============= Chat Related Methods =============
    def create_chat_message(
        self,
        session_id,
        message,
        msg_type="Human Message",
        references=None,
        recommended_lawyers=None,
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Convert lists to JSON strings
            references_str = json.dumps(references) if references else None
            recommended_lawyers_str = (
                json.dumps(recommended_lawyers) if recommended_lawyers else None
            )

            query = """
            INSERT INTO ChatMessages 
            (SessionId, Message, Type, [References], RecommendedLawyers)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(
                query,
                (
                    session_id,
                    message,
                    msg_type,
                    references_str,
                    recommended_lawyers_str,
                ),
            )
            conn.commit()
            return True

    def get_chat_messages_by_session_id(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ChatMessages WHERE SessionId = ?", session_id)
            return cursor.fetchall()

    def get_chat_topics(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
    SELECT DISTINCT Topic, SessionId, Time
    FROM Sessions
    WHERE UserId = ? AND Active = 1
    ORDER BY Time DESC
"""
            cursor.execute(query, user_id)
            rows = cursor.fetchall()
            topics = [row.Topic for row in rows]
            session_ids = [row.SessionId for row in rows]
            times = [row.Time for row in rows]
            return {"chat_topics": topics, "chat_sessions": session_ids, "Time": times}

    def update_chat_message(
        self, chat_id, message, msg_type, references=None, recommended_lawyers=None
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE ChatMessages 
                      SET Message = ?, Type = ?, References = ?, RecommendedLawyers = ?
                      WHERE ChatId = ?"""
            cursor.execute(
                query, (message, msg_type, references, recommended_lawyers, chat_id)
            )
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

    def create_chat_session(self, initiator_id, recipient_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO ChatSessions (InitiatorId, RecipientId, StartTime)
                OUTPUT INSERTED.ChatId
                VALUES (?, ?, GETDATE())
            """
            cursor.execute(query, (initiator_id, recipient_id))
            chat_id = cursor.fetchone()[0]
            conn.commit()
            return chat_id

    # ============= Session Related Methods =============
    def create_session(self, user_id, topic):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Check if user exists
                check_user_query = "SELECT 1 FROM [User] WHERE UserId = ?"
                cursor.execute(check_user_query, (user_id,))
                if not cursor.fetchone():
                    raise ValueError(f"User with ID {user_id} does not exist")

                # Insert session and get the ID using OUTPUT clause
                query = """
                    INSERT INTO Sessions (UserId, Topic, Time, Active)
                    OUTPUT INSERTED.SessionId
                    VALUES (?, ?, GETDATE(), 1)
                """
                cursor.execute(query, (user_id, topic))
                result = cursor.fetchone()
                conn.commit()

                if result:
                    return result[0]
                return None

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

    def delete_session(self, session_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Sessions WHERE SessionId = ?", session_id)
            conn.commit()
            return cursor.rowcount

    def get_all_chat_sessions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Sessions WHERE Active = 1")
            return cursor.fetchall()

    # def get_chat_session_by_id(self, session_id):
    #     with self.get_connection() as conn:
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT * FROM Sessions WHERE SessionId = ?", session_id)
    #         return cursor.fetchone()

    # ============= User Related Methods =============
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
        if not isinstance(email, str) or len(email) > 255 or "@" not in email:
            raise ValueError("Invalid email format")
        if not isinstance(password, str) or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        if role not in [
            "client",
            "lawyer",
            "system",
        ]:  # Updated to match SQL constraint
            raise ValueError("Invalid role. Must be 'client', 'lawyer', or 'system'")

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

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [User]")
            return cursor.fetchall()

    # ============= Client Related Methods =============
    def create_client(
        self, user_id, cnic, contact, location, credits=0, profile_picture=None
    ):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO Client (UserId, CNIC, Contact, Location, Credits, ProfilePicture)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (user_id, cnic, contact, location, credits, profile_picture),
                )
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

    def update_client(
        self, client_id, cnic, contact, location, credits=0, profile_picture=None
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Client 
                      SET CNIC = ?, Contact = ?, Location = ?, Credits = ?, ProfilePicture = ?
                      WHERE ClientId = ?"""
            cursor.execute(
                query, (cnic, contact, location, credits, profile_picture, client_id)
            )
            conn.commit()
            return cursor.rowcount

    def delete_client(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Client WHERE ClientId = ?", client_id)
            conn.commit()
            return cursor.rowcount

    def get_client_by_id(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client WHERE ClientId = ?", client_id)
            return cursor.fetchone()

    def get_client_by_user_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client WHERE UserId = ?", user_id)
            return cursor.fetchone()

    def get_all_clients(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Client")
            return cursor.fetchall()

    # ============= Lawyer Related Methods =============
    def check_lawyer_cnic_exists(self, cnic):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT 1 FROM Lawyer WHERE CNIC = ?"
            cursor.execute(query, (cnic,))
            return cursor.fetchone() is not None

    def create_lawyer(
        self,
        user_id,
        cnic,
        license_number,
        location,
        experience,
        specialization,
        contact,
        email,
        paid=False,
        expiry_date=None,
        recommended=0,
        times_clicked=0,
        times_shown=0,
    ):
        # Check if CNIC already exists
        if self.check_lawyer_cnic_exists(cnic):
            raise ValueError("A lawyer with this CNIC already exists")

        # Existing validation code...
        if not isinstance(cnic, str) or len(cnic) > 20:
            raise ValueError("Invalid CNIC format")
        # ...existing validation code...

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """INSERT INTO Lawyer 
                          (UserId, CNIC, LicenseNumber, Location, Experience, 
                           Specialization, Contact, Email, Paid, ExpiryDate, 
                           Recommended, TimesClicked, TimesShown)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(
                    query,
                    (
                        user_id,
                        cnic,
                        license_number,
                        location,
                        experience,
                        specialization,
                        contact,
                        email,
                        paid,
                        expiry_date,
                        recommended,
                        times_clicked,
                        times_shown,
                    ),
                )
                conn.commit()
                return cursor.rowcount
        except pyodbc.IntegrityError as e:
            if "UQ__Lawyer__AA570FD4" in str(e):
                raise ValueError("A lawyer with this CNIC already exists")
            raise e

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

    def update_lawyer(
        self,
        lawyer_id,
        cnic,
        license_number,
        location,
        experience,
        specialization,
        contact,
        email,
        paid=False,
        expiry_date=None,
        recommended=0,
        times_clicked=0,
        times_shown=0,
    ):
        # Input validations
        if not isinstance(experience, int) or experience < 0:
            raise ValueError("Experience must be a positive integer")
        if not isinstance(cnic, str) or len(cnic) > 20:
            raise ValueError("Invalid CNIC format")
        if not isinstance(contact, str) or len(contact) > 20:
            raise ValueError("Invalid contact format")
        if not isinstance(email, str) or len(email) > 100 or "@" not in email:
            raise ValueError("Invalid email format")
        if not isinstance(specialization, str) or len(specialization) > 100:
            raise ValueError("Invalid specialization format")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Lawyer 
                      SET CNIC = ?, LicenseNumber = ?, Location = ?, Experience = ?,
                          Specialization = ?, Contact = ?, Email = ?, 
                          Paid = ?, ExpiryDate = ?, Recommended = ?,
                          TimesClicked = ?, TimesShown = ?
                      WHERE LawyerId = ?"""
            cursor.execute(
                query,
                (
                    cnic,
                    license_number,
                    location,
                    experience,
                    specialization,
                    contact,
                    email,
                    paid,
                    expiry_date,
                    recommended,
                    times_clicked,
                    times_shown,
                    lawyer_id,
                ),
            )
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
            query = """
            SELECT 
                l.LawyerId,
                u.Name,
                u.Email,
                l.Contact,
                l.Location,
                l.Specialization as Category,
                l.Experience,
                CAST(COALESCE(AVG(CAST(lr.Stars AS FLOAT)), 0) AS DECIMAL(3,2)) as Rating
            FROM Lawyer l
            JOIN [User] u ON l.UserId = u.UserId
            LEFT JOIN LawyerReview lr ON l.UserId = lr.LawyerId
            WHERE l.LawyerId = ? AND l.Paid = 1
            GROUP BY 
                l.LawyerId,
                u.Name,
                u.Email,
                l.Contact,
                l.Location,
                l.Specialization,
                l.Experience
            """
            cursor.execute(query, lawyer_id)
            return cursor.fetchone()

    def get_lawyer_by_Userid(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer WHERE UserId = ?", user_id)
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
                SELECT 
                    u.Name,
                    u.Email,
                    l.Contact,
                    l.Experience,
                    l.Specialization as Category,
                    l.LawyerId,
                    l.CNIC,
                    l.LicenseNumber,
                    l.Location,
                    CAST(COALESCE(AVG(CAST(lr.Stars AS FLOAT)), 0) AS DECIMAL(3,2)) as Rating
                FROM Lawyer l
                JOIN [User] u ON l.UserId = u.UserId
                LEFT JOIN LawyerReview lr ON l.UserId = lr.LawyerId
                WHERE l.Specialization = ? AND l.Paid = 1
                GROUP BY 
                    u.Name,
                    u.Email,
                    l.Contact,
                    l.Experience,
                    l.Specialization,
                    l.LawyerId,
                    l.CNIC,
                    l.LicenseNumber,
                    l.Location
                ORDER BY 
                    Rating DESC,
                    l.Experience DESC
            """
            cursor.execute(query, specialization)
            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor) for row in rows]

    def update_lawyer_paid_status(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
            UPDATE Lawyer
            SET Paid = 1, ExpiryDate = DATEADD(MONTH, 1, GETDATE())
            WHERE UserId = ?
            """
            cursor.execute(query, lawyer_id)
            conn.commit()
            return cursor.rowcount

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

    def get_lawyer_dashboard_data(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    (SELECT COUNT(*) FROM Cases WHERE LawyerId = ?) AS totalCases,
                    (SELECT COUNT(*) FROM Clients WHERE LawyerId = ?) AS activeClients,
                    (SELECT AVG(Stars) FROM LawyerReview WHERE LawyerId = ?) AS rating,
                    (SELECT COUNT(*) FROM Appointments WHERE LawyerId = ? AND Date >= GETDATE()) AS appointments
            """
            cursor.execute(query, (lawyer_id, lawyer_id, lawyer_id, lawyer_id))
            row = cursor.fetchone()
            return {
                "totalCases": row.totalCases,
                "activeClients": row.activeClients,
                "rating": row.rating,
                "appointments": row.appointments,
            }

    def get_recent_activities(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT TOP 10 Activity, Time
                FROM Activities
                WHERE LawyerId = ?
                ORDER BY Time DESC
            """
            cursor.execute(query, lawyer_id)
            return cursor.fetchall()

    def update_lawyer_recommendation(self, lawyer_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Lawyer SET Recommended = 1, LastRecommended = CURRENT_TIMESTAMP, RecommendationCount = RecommendationCount + 1 WHERE LawyerId = ?",
                lawyer_id,
            )
            conn.commit()
            return cursor.rowcount

    def get_lawyer_recommendations(self, lawyer_id):
        with self.get_connection() as conn:
            lawyer_id = int(lawyer_id)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Lawyer WHERE LawyerId = ?", lawyer_id)
            return self._row_to_dict(cursor.fetchone(), cursor)

    # ============= Subscription Related Methods =============
    def create_subscription(
        self, user_id, subscription_type, start_date, expiry_date, remaining_credits=0
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # First check if user has an existing subscription
            check_query = "SELECT SubsId FROM Subscription WHERE UserId = ?"
            cursor.execute(check_query, (user_id,))
            existing_subscription = cursor.fetchone()

            if existing_subscription:
                # Update existing subscription
                update_query = """
                    UPDATE Subscription 
                    SET CurrentSubscription = ?,
                        StartDate = ?,
                        ExpiryDate = ?,
                        RemainingCredits = ?
                    WHERE UserId = ?
                """
                cursor.execute(
                    update_query,
                    (subscription_type, start_date, expiry_date, remaining_credits, user_id)
                )
            else:
                # Create new subscription
                insert_query = """
                    INSERT INTO Subscription 
                    (UserId, CurrentSubscription, StartDate, ExpiryDate, RemainingCredits)
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(
                    insert_query,
                    (user_id, subscription_type, start_date, expiry_date, remaining_credits)
                )
            
            conn.commit()
            return cursor.rowcount

    def get_subscription(self, user_id):
        # Updated to use UserId instead of SubsId for lookup
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Subscription WHERE UserId = ?", user_id)
            return cursor.fetchone()

    def update_subscription(
        self, subs_id, subscription_type, expiry_date, remaining_credits
    ):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """UPDATE Subscription 
                      SET CurrentSubscription = ?, ExpiryDate = ?, RemainingCredits = ?
                      WHERE SubsId = ?"""
            cursor.execute(
                query, (subscription_type, expiry_date, remaining_credits, subs_id)
            )
            conn.commit()
            return cursor.rowcount

    def delete_subscription(self, subs_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Subscription WHERE SubsId = ?", subs_id)
            conn.commit()
            return cursor.rowcount

    def get_current_subscription(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Subscription WHERE UserId = ? ORDER BY ExpiryDate DESC",
                user_id,
            )
            return cursor.fetchone()

    def get_all_subscriptions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Subscription")
            return cursor.fetchall()

    # ============= Credits Related Methods =============
    def get_credits_by_user_id(self, user_id):
        """Get credits for a user from their current subscription"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT TOP 1 RemainingCredits 
                FROM Subscription 
                WHERE UserId = ? 
                  AND ExpiryDate > GETDATE()
                ORDER BY ExpiryDate DESC
            """
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return row[0] if row else 0

    def update_credits_by_user_id(self, user_id, credits):
        """Update credits for a user's current subscription"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE Subscription 
                SET RemainingCredits = ?
                WHERE UserId = ? 
                  AND ExpiryDate > GETDATE()
                  AND SubsId = (
                    SELECT TOP 1 SubsId 
                    FROM Subscription 
                    WHERE UserId = ? 
                      AND ExpiryDate > GETDATE()
                    ORDER BY ExpiryDate DESC
                  )
            """
            cursor.execute(query, (credits, user_id, user_id))
            conn.commit()
            return cursor.rowcount
    def get_paid_lawyers(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # id": lawyer[0],
            #     "name": lawyer[1],
            #     "email": lawyer[2],
            #     "contact": lawyer[3],
            #     "location": lawyer[4],
            #     "specialization": lawyer[5],
            #     "experience": lawyer[6],
            #     "rating": float(lawyer[7]) if lawyer[7] is not None else 0.0,
            #     "avatar": None
            query = """
            SELECT
            l.LawyerId,
            l.name,
            l.email,
            l.contact,
            l.location,
            l.specialization,
            l.experience,
            l.rating,
            l.avatar
            FROM Lawyer l
            JOIN Subscription s ON l.id = s.LawyerId
            WHERE s.ExpiryDate > GETDATE()
            """

            # query = """
            # Select * from Lawyer 
            # Where Paid = 1
            # """
            cursor.execute(query)
            return cursor.fetchall()
    # ============= Review Related Methods =============
    def create_lawyer_review(self, lawyer_id, client_id, stars, review_message=None):
        # Updated validation to match SQL constraints
        if not isinstance(stars, int) or not 1 <= stars <= 5:
            raise ValueError("Stars must be between 1 and 5")
        if review_message and len(review_message) > 1000:
            raise ValueError("Review message too long")
        if not self.get_user_by_id(lawyer_id) or not self.get_user_by_id(client_id):
            raise ValueError("Invalid lawyer_id or client_id")

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

    # ============= Helper Methods =============
    def _row_to_dict(self, row, cursor):
        if not row:
            return None
        columns = [column[0] for column in cursor.description]
        result = dict(zip(columns, row))
        datetime_fields = ["LastRecommended", "Time", "ExpiryDate", "ReviewTime"]
        for field in datetime_fields:
            if field in result and result[field]:
                # Handle SQL Server datetime format
                if isinstance(result[field], str):
                    try:
                        # Try multiple datetime formats
                        formats = [
                            "%b %d %Y %I:%M%p",  # Dec 12 2024 11:06PM
                            "%Y-%m-%d %H:%M:%S",  # 2024-12-12 23:06:00
                            "%Y-%m-%d %H:%M:%S.%f",  # 2024-12-12 23:06:00.000
                        ]
                        for fmt in formats:
                            try:
                                result[field] = datetime.strptime(result[field], fmt)
                                break
                            except ValueError:
                                continue
                    except Exception as e:
                        print(f"Error parsing datetime {result[field]}: {e}")
                elif isinstance(result[field], datetime):
                    pass
        return result