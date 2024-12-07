import pyodbc
from typing import List, Dict, Optional
import datetime
import json
import os
import csv
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()

class LawyerStore:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._load_lawyers_from_csv()

    def _get_db_connection(self):
        return pyodbc.connect(self.connection_string)

    def _load_lawyers_from_csv(self):
        """Load lawyers from CSV and store in MS SQL"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            with open("lawyers.csv", mode="r", encoding='utf-8') as file:
                lawyers = csv.DictReader(file)
                for lawyer in lawyers:
                    # First insert into Lawyers table
                    lawyer_query = """
                        INSERT INTO Lawyers (LawyerName, ContactInfo, CreatedAt)
                        OUTPUT INSERTED.LawyerId
                        VALUES (?, ?, ?)
                    """
                    contact_info = json.dumps({
                        'specialization': lawyer['Specialization'],
                        'experience': lawyer['Experience'],
                        'rating': lawyer['Rating'],
                        'location': lawyer['Location'],
                        'contact': lawyer['Contact']
                    })
                    
                    cursor.execute(lawyer_query, (
                        lawyer['Name'],
                        contact_info,
                        datetime.datetime.utcnow()
                    ))
                    
                    # Get the auto-generated LawyerId
                    lawyer_id = cursor.fetchval()
                    
                    # Then insert into LawyerStore with the new LawyerId
                    store_query = """
                        INSERT INTO LawyerStore (LawyerId, LawyerName, Email, CreatedAt, 
                                               Specialization, Experience, Rating, Location, Contact)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(store_query, (
                        lawyer_id,
                        lawyer['Name'],
                        lawyer.get('Email', ''),
                        datetime.datetime.utcnow(),
                        lawyer['Specialization'],
                        lawyer['Experience'],
                        lawyer['Rating'],
                        lawyer['Location'],
                        lawyer['Contact']
                    ))
            conn.commit()
            logging.info("Successfully loaded lawyers from CSV")
            
        except Exception as e:
            logging.error(f"Error loading lawyers from CSV: {e}")
        finally:
            cursor.close()
            conn.close()

    def calculate_weight(self, rating: str, experience: str) -> float:
        """Calculate weight for lawyer ranking using 60-40 weighted formula"""
        try:
            # Normalize rating to 0-1 scale
            normalized_rating = float(rating) / 5.0
            # Extract years from experience and normalize to 0-1 scale (assuming max 35 years)
            years = int(experience.split()[0])
            normalized_exp = min(float(years) / 35.0, 1.0)
            # Apply weights: 60% rating, 40% experience
            return (0.6 * normalized_rating) + (0.4 * normalized_exp)
        except (ValueError, IndexError) as e:
            logging.error(f"Error calculating weight: {e}")
            return 0.0

    def get_top_lawyers(self, category: str) -> List[Dict]:
        """Get lawyers by category sorted by weighted score"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT u.UserName, u.Email, ld.Specialization, ld.Experience, 
                       ld.Rating, ld.Location
                FROM Users u
                JOIN LawyerDetails ld ON u.UserId = ld.LawyerId
                WHERE ld.Specialization = ?
                ORDER BY ld.Rating DESC, ld.Experience DESC
            """
            cursor.execute(query, (category,))
            
            lawyers = []
            for row in cursor.fetchall():
                lawyers.append({
                    'name': row.UserName,
                    'email': row.Email,
                    'specialization': row.Specialization,
                    'experience': row.Experience,
                    'rating': float(row.Rating),
                    'location': row.Location,
                })
            return lawyers
            
        except Exception as e:
            logging.error(f"Error getting top lawyers: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def format_recommendation(self, lawyers: List[Dict]) -> Dict:
        """Format lawyer recommendations with detailed info"""
        formatted = []
        for lawyer in lawyers:
            formatted.append({
                "name": lawyer["name"],
                "specialization": lawyer["specialization"],
                "experience": lawyer["experience"],
                "rating": lawyer["rating"],
                "location": lawyer["location"],
                "contact": lawyer["contact"],
                "recommended_for": lawyer["specialization"],
                "recommendation_score": self.calculate_weight(lawyer["rating"], lawyer["experience"])
            })
        return formatted

    def add_lawyer(self, lawyer_data: Dict) -> None:
        """Add a new lawyer to the database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # First create user record
            user_id = str(uuid.uuid4())
            user_query = """
                INSERT INTO Users (UserId, UserName, Email, UserType, CreatedAt)
                VALUES (?, ?, ?, 'Lawyer', ?)
            """
            cursor.execute(user_query, (
                user_id,
                lawyer_data["name"],
                lawyer_data["email"],
                datetime.datetime.utcnow()
            ))

            # Then create lawyer details
            lawyer_query = """
                INSERT INTO LawyerDetails 
                (LawyerId, Specialization, Experience, LicenseNumber, Rating, Location)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(lawyer_query, (
                user_id,
                lawyer_data["specialization"],
                lawyer_data["experience"],
                lawyer_data["license_number"],
                lawyer_data["rating"],
                lawyer_data["location"]
            ))

            # Add specializations
            spec_query = """
                INSERT INTO LawyerSpecializationMapping (LawyerId, SpecializationId)
                VALUES (?, ?)
            """
            for spec_id in lawyer_data.get("specializations", []):
                cursor.execute(spec_query, (user_id, spec_id))

            conn.commit()
            
        except Exception as e:
            logging.error(f"Error adding lawyer: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_lawyers_by_category(self, category: str) -> List[Dict]:
        """Get lawyers by category from the database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT LawyerName, Email, Specialization, Experience, 
                       Rating, Location, Contact
                FROM LawyerStore
                WHERE Specialization = ?
            """
            cursor.execute(query, (category,))
            
            lawyers = []
            for row in cursor.fetchall():
                lawyers.append({
                    'name': row.LawyerName,
                    'email': row.Email,
                    'specialization': row.Specialization,
                    'experience': row.Experience,
                    'rating': row.Rating,
                    'location': row.Location,
                    'contact': row.Contact
                })
            return lawyers
            
        except Exception as e:
            logging.error(f"Error getting lawyers by category: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def update_lawyer(self, lawyer_id: str, lawyer_data: Dict) -> None:
        """Update lawyer information in the database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE Lawyers
                SET LawyerName = ?, ContactInfo = ?
                WHERE LawyerId = ?
            """
            cursor.execute(query, (
                lawyer_data["name"],
                json.dumps({
                    'specialization': lawyer_data['specialization'],
                    'experience': lawyer_data['experience'],
                    'rating': lawyer_data['rating'],
                    'location': lawyer_data['location'],
                    'contact': lawyer_data['contact']
                }),
                lawyer_id
            ))
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error updating lawyer: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_lawyer(self, category: str, lawyer_id: str) -> None:
        """Delete a lawyer from the database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                DELETE FROM Lawyers
                WHERE LawyerId = ? AND JSON_VALUE(ContactInfo, '$.specialization') = ?
            """
            cursor.execute(query, (lawyer_id, category))
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error deleting lawyer: {e}")
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    user = LawyerStore(connection_string=os.getenv("SQL_CONN_STRING"))
    userData = user.get_top_lawyers("Intellectual Property")
    print(userData)
    # print(user.get_top_lawyers("Banking and Finance", limit=3))
