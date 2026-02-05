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
        
    def connect(self):
        try:
            return mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def create_tables(self):
        connection = self.connect()
        if connection:
            cursor = connection.cursor()
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    photo LONGTEXT,
                    full_name VARCHAR(255),
                    date_of_birth DATE,
                    email VARCHAR(255) UNIQUE,
                    password VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Pending Users (Temporary storage before OTP)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pending_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    photo LONGTEXT,
                    full_name VARCHAR(255),
                    date_of_birth DATE,
                    email VARCHAR(255) UNIQUE,
                    password VARCHAR(255),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            # Dedicated OTP table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS otp_verification (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255),
                    otp VARCHAR(6),
                    type VARCHAR(20),
                    expires_at DATETIME
                )
            ''')
            connection.commit()
            cursor.close()
            connection.close()