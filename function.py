import mysql.connector
import pyotp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta
import re
from mysql.connector import Error

class RequirementFunctions:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }

    def get_db_connection(self):
        return mysql.connector.connect(**self.db_config)

    def send_email(self, to_email, subject, html_content):
        try:
            msg = MIMEMultipart()
            msg['From'] = os.getenv('EMAIL_USER')
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
            server.starttls()
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
            server.sendmail(os.getenv('EMAIL_USER'), to_email, msg.as_string())
            server.quit()
            return True
        except Exception as err:
            print(f"Email Error: {err}")
            return False

    def generate_otp(self):
        return str(pyotp.random_base32()[:6]).upper()

    def validate_email(self, email):
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    def calculate_age(self, dob_str):
        try:
            birth_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except:
            return 0

    def handle_resend_otp(self, email, otp_type):
        """Generic logic to refresh OTP for any flow"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        otp = self.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)
        
        cursor.execute("DELETE FROM otp_verification WHERE email = %s AND type = %s", (email, otp_type))
        cursor.execute("INSERT INTO otp_verification (email, otp, type, expires_at) VALUES (%s, %s, %s, %s)", 
                       (email, otp, otp_type, expires_at))
        conn.commit()
        
        body = f"<h2>Your New Code</h2><p>Your requested {otp_type} code is: <b>{otp}</b></p>"
        sent = self.send_email(email, f"New OTP for {otp_type}", body)
        cursor.close()
        conn.close()
        return sent
