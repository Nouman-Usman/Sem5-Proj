import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn_string = os.getenv("AZURE_SQL_CONNECTION_STRING")

    def create_user(self, name: str, email: str, password_hash: str, user_type: str):
        with pyodbc.connect(self.conn_string) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Users (name, email, password_hash, user_type) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, user_type)
            )
            conn.commit()
            return cursor.lastrowid

    def create_lawyer_profile(self, lawyer_id: int, specialty: str, experience_years: int, location: str):
        with pyodbc.connect(self.conn_string) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO LawyerProfiles 
                   (lawyer_id, specialty, experience_years, location, rating) 
                   VALUES (?, ?, ?, ?, 0.0)""",
                (lawyer_id, specialty, experience_years, location)
            )
            conn.commit()

def create_tables():
    conn_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
    with pyodbc.connect(conn_string) as conn:
        cursor = conn.cursor()
        
        # Create lawyers table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='lawyers' AND xtype='U')
            CREATE TABLE lawyers (
                id INT PRIMARY KEY IDENTITY(1,1),
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                specialty VARCHAR(100),
                location VARCHAR(100),
                rating DECIMAL(3,2),
                experience_years INT,
                created_at DATETIME
            )
        """)

        # Create lawyer_availability table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='lawyer_availability' AND xtype='U')
            CREATE TABLE lawyer_availability (
                id INT PRIMARY KEY IDENTITY(1,1),
                lawyer_id INT,
                day_of_week INT,
                start_time TIME,
                end_time TIME,
                FOREIGN KEY (lawyer_id) REFERENCES lawyers(id)
            )
        """)

        # Create client_cases table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='client_cases' AND xtype='U')
            CREATE TABLE client_cases (
                id INT PRIMARY KEY IDENTITY(1,1),
                client_id INT,
                lawyer_id INT,
                case_type VARCHAR(100),
                description TEXT,
                status VARCHAR(50),
                created_at DATETIME,
                FOREIGN KEY (client_id) REFERENCES users(id),
                FOREIGN KEY (lawyer_id) REFERENCES lawyers(id)
            )
        """)
        
        conn.commit()

if __name__ == "__main__":
    create_tables()