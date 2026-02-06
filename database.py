# database.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class Database:
    def __init__(self):
        # For Render: Try to get external database URL first
        external_url = os.getenv('EXTERNAL_DATABASE_URL')
        
        if external_url:
            # Parse external database URL
            parsed_url = urllib.parse.urlparse(external_url)
            self.host = parsed_url.hostname
            self.user = parsed_url.username
            self.password = parsed_url.password
            self.database = parsed_url.path[1:] if parsed_url.path else os.getenv('DB_NAME')
            self.port = parsed_url.port or 3306
        else:
            # Fallback to individual env vars
            self.host = os.getenv('DB_HOST', 'localhost')
            self.user = os.getenv('DB_USER', 'root')
            self.password = os.getenv('DB_PASSWORD', '')
            self.database = os.getenv('DB_NAME', 'secure_auth')
            self.port = int(os.getenv('DB_PORT', '3306'))
        
        # For Render MySQL addon
        internal_url = os.getenv('DATABASE_URL')
        if internal_url and internal_url.startswith('mysql://'):
            import re
            pattern = r'mysql://(\w+):([^@]+)@([^:]+):(\d+)/(\w+)'
            match = re.match(pattern, internal_url)
            if match:
                self.user, self.password, self.host, self.port, self.database = match.groups()
                self.port = int(self.port)
    
    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=10,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL on {self.host}:{self.port}: {e}")
            print(f"Using database: {self.database}")
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
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
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
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            ''')
            
            # Dedicated OTP table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS otp_verification (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255),
                    otp VARCHAR(6),
                    type VARCHAR(20),
                    expires_at DATETIME,
                    INDEX idx_email_type (email, type)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            ''')
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Tables created/verified successfully")
