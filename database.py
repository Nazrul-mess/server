import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.port = os.getenv('DB_PORT')
    
    def connect(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def create_tables(self):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Users table: Added gender and phone
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(50) UNIQUE NOT NULL,
                        photo LONGTEXT,
                        full_name VARCHAR(255) NOT NULL,
                        date_of_birth DATE,
                        gender VARCHAR(20),
                        phone_number VARCHAR(20),
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        current_session VARCHAR(255),
                        INDEX(email)
                    )
                ''')

                # Pending Users: Mirroring the users table for temporary storage
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pending_users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(50),
                        photo LONGTEXT,
                        full_name VARCHAR(255),
                        date_of_birth DATE,
                        gender VARCHAR(20),
                        phone_number VARCHAR(20),
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                ''')

                # OTP verification: Added created_at for better tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS otp_verification (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        email VARCHAR(255) NOT NULL,
                        otp VARCHAR(6) NOT NULL,
                        type VARCHAR(20), -- e.g., 'signup' or 'reset'
                        expires_at DATETIME NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX(email)
                    )
                ''')

                connection.commit()
                print("Tables updated/created successfully.")
            except Error as e:
                print(f"Error creating tables: {e}")
            finally:
                cursor.close()
                connection.close()

# Initialize database
# db = Database()
# db.create_tables()