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
        # self._load_lawyers_from_csv()

    def _get_db_connection(self):
        return pyodbc.connect(self.connection_string)

    def _load_lawyers_from_csv(self):
        """Load lawyers from CSV and create proper user accounts with lawyer details"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            with open("lawyers.csv", mode="r", encoding='utf-8') as file:
                lawyers = csv.DictReader(file)
                for lawyer in lawyers:
                    user_id = str(uuid.uuid4())
                    profile_id = str(uuid.uuid4())
                    
                    # Create user record
                    user_query = """
                        INSERT INTO Users (UserId, UserName, Email, UserType, CreatedAt)
                        VALUES (CAST(? AS UNIQUEIDENTIFIER), ?, ?, 'Lawyer', GETDATE())
                    """
                    cursor.execute(user_query, (
                        user_id,
                        lawyer['Name'],
                        lawyer.get('Email', f"{lawyer['Name'].replace(' ', '').lower()}@example.com")
                    ))

                    profile_query = """
                        INSERT INTO UserProfiles (ProfileId, UserId, ContactNumber, Address)
                        VALUES (CAST(? AS UNIQUEIDENTIFIER), CAST(? AS UNIQUEIDENTIFIER), ?, ?)
                    """
                    cursor.execute(profile_query, (
                        profile_id,
                        user_id,
                        lawyer.get('Contact', 'Not provided'),
                        lawyer.get('Location', 'Not provided')
                    ))
                    lawyer_details_query = """
                        INSERT INTO LawyerDetails 
                        (LawyerId, Specialization, Experience, LicenseNumber, Rating, Location)
                        VALUES (CAST(? AS UNIQUEIDENTIFIER), ?, ?, ?, ?, ?)
                    """
                    license_number = f"TBD-{str(uuid.uuid4())[:8]}"
                    cursor.execute(lawyer_details_query, (
                        user_id,
                        lawyer['Specialization'],
                        int(lawyer.get('Experience', '0').split()[0]),  # Extract years
                        license_number,
                        float(lawyer.get('Rating', '0')),
                        lawyer['Location']
                    ))
                    if 'Specializations' in lawyer:
                        specializations = [s.strip() for s in lawyer['Specializations'].split(',')]
                        for spec in specializations:
                            spec_id = str(uuid.uuid4())
                            # Create or get specialization
                            cursor.execute("""
                                MERGE INTO LawyerSpecializations AS target
                                USING (SELECT ? as Name) AS source
                                ON target.Name = source.Name
                                WHEN NOT MATCHED THEN
                                    INSERT (SpecializationId, Name)
                                    VALUES (CAST(? AS UNIQUEIDENTIFIER), ?);
                                
                                SELECT SpecializationId FROM LawyerSpecializations WHERE Name = ?;
                            """, (spec, spec_id, spec, spec))
                            
                            spec_id = cursor.fetchone()[0]
                            
                            # Create mapping
                            cursor.execute("""
                                INSERT INTO LawyerSpecializationMapping (LawyerId, SpecializationId)
                                VALUES (CAST(? AS UNIQUEIDENTIFIER), ?)
                            """, (user_id, spec_id))

                    conn.commit()
                    logging.info(f"Successfully created lawyer account for {lawyer['Name']}")
                
                logging.info("Successfully loaded all lawyers from CSV")
                
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            logging.error(f"Error loading lawyers from CSV: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def calculate_weight(self, rating: str, experience: str) -> float:
        try:
            normalized_rating = float(rating) / 5.0
            years = int(experience.split()[0])
            normalized_exp = min(float(years) / 35.0, 1.0)
            return (0.6 * normalized_rating) + (0.4 * normalized_exp)
        except (ValueError, IndexError) as e:
            logging.error(f"Error calculating weight: {e}")
            return 0.0

    def get_top_lawyers(self, category: str) -> List[Dict]:
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT u.UserName, u.Email, ld.Specialization, ld.Experience, 
                       ld.Rating, ld.Location, ld.LicenseNumber,
                       up.ContactNumber, up.Address
                FROM Users u
                JOIN LawyerDetails ld ON u.UserId = ld.LawyerId
                LEFT JOIN UserProfiles up ON u.UserId = up.UserId
                WHERE ld.Specialization = ? AND u.UserType = 'Lawyer'
                ORDER BY ld.Rating DESC, ld.Experience DESC
            """
            cursor.execute(query, (category,))            
            lawyers = []
            for row in cursor.fetchall():
                contact_info = {
                    'phone': row.ContactNumber or 'Not provided',
                    'address': row.Address or 'Not provided'
                }
                lawyers.append({
                    'name': row.UserName,
                    'email': row.Email,
                    'specialization': row.Specialization,
                    'experience': str(row.Experience) + ' years',
                    'rating': float(row.Rating),
                    'location': row.Location,
                    'license_number': row.LicenseNumber,
                    'contact_info': contact_info,
                    'avatar': None,  
                    'reviewCount': 0  
                })
            return lawyers
            
        except Exception as e:
            logging.error(f"Error getting top lawyers: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def get_lawyer_details(self, lawyer_id: str) -> Optional[Dict]:
        """Get detailed information for a specific lawyer"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT u.UserName, u.Email, ld.*, up.ContactNumber, up.Address,
                       (SELECT STRING_AGG(ls.Name, ',')
                        FROM LawyerSpecializationMapping lsm
                        JOIN LawyerSpecializations ls ON lsm.SpecializationId = ls.SpecializationId
                        WHERE lsm.LawyerId = ld.LawyerId) as Specializations
                FROM Users u
                JOIN LawyerDetails ld ON u.UserId = ld.LawyerId
                LEFT JOIN UserProfiles up ON u.UserId = up.UserId
                WHERE u.UserId = ? AND u.UserType = 'Lawyer'
            """
            cursor.execute(query, (lawyer_id,))
            row = cursor.fetchone()
            
            if row:
                specializations = row.Specializations.split(',') if row.Specializations else []
                return {
                    'id': lawyer_id,
                    'name': row.UserName,
                    'email': row.Email,
                    'specialization': row.Specialization,
                    'specializations': specializations,
                    'experience': row.Experience,
                    'rating': float(row.Rating),
                    'location': row.Location,
                    'license_number': row.LicenseNumber,
                    'contact': {
                        'phone': row.ContactNumber or 'Not provided',
                        'address': row.Address or 'Not provided'
                    }
                }
            return None
            
        except Exception as e:
            logging.error(f"Error getting lawyer details: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def search_lawyers(self, query: str) -> List[Dict]:
        """Search lawyers by name, specialization, or location"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            search_query = """
                SELECT DISTINCT u.UserName, u.Email, ld.Specialization, 
                       ld.Experience, ld.Rating, ld.Location
                FROM Users u
                JOIN LawyerDetails ld ON u.UserId = ld.LawyerId
                LEFT JOIN LawyerSpecializationMapping lsm ON ld.LawyerId = lsm.LawyerId
                LEFT JOIN LawyerSpecializations ls ON lsm.SpecializationId = ls.SpecializationId
                WHERE u.UserType = 'Lawyer'
                AND (
                    u.UserName LIKE ? OR
                    ld.Specialization LIKE ? OR
                    ld.Location LIKE ? OR
                    ls.Name LIKE ?
                )
                ORDER BY ld.Rating DESC
            """
            search_pattern = f"%{query}%"
            cursor.execute(search_query, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            return [self._format_lawyer_result(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logging.error(f"Error searching lawyers: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def _format_lawyer_result(self, row) -> Dict:
        """Helper method to format lawyer data consistently"""
        return {
            'name': row.UserName,
            'email': row.Email,
            'specialization': row.Specialization,
            'experience': str(row.Experience) + ' years',
            'rating': float(row.Rating),
            'location': row.Location,
            'reviewCount': 0,  # Add actual review count when implemented
            'description': f"Specializes in {row.Specialization} with {row.Experience} years of experience"
        }

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
    userData = user.get_top_lawyers("Consitutional")
    print(userData)
    # print(user.get_top_lawyers("Banking and Finance", limit=3))
