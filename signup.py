from flask import request, jsonify
import bcrypt
from function import RequirementFunctions
from database import Database
from datetime import datetime, timedelta

rec_fun = RequirementFunctions()
db = Database()

class SignupHandler:
    @staticmethod
    def signup():
            
            try:
                data = request.json
                full_name = data.get('fullName')
                dob_str = data.get('age') # Assuming this is 'YYYY-MM-DD'
                email = data.get('email')
                password = data.get('password')
                photo = data.get('photo') # Base64 string or URL

                # Validation
                if not all([full_name, dob_str, email, password]):
                    return jsonify({'success': False, 'message': 'Missing fields'}), 400
                
                age = rec_fun.calculate_age(dob_str)
                if age < 18:
                    return jsonify({'success': False, 'message': 'Must be 18+'}), 400
                
                if not rec_fun.validate_email(email):
                    return jsonify({'success': False, 'message': 'Invalid email format'}), 400

                # Database Check
                conn = db.connect()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': 'Email already registered'}), 400

                # Process Pending User
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,))
                cursor.execute("""
                    INSERT INTO pending_users (photo, full_name, date_of_birth, email, password) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (photo, full_name, dob_str, email, hashed_pw))

                # OTP Generation
                otp = rec_fun.generate_otp()
                expires_at = datetime.now() + timedelta(minutes=10)
                
                cursor.execute("DELETE FROM otp_verification WHERE email = %s", (email,))
                cursor.execute("""
                    INSERT INTO otp_verification (email, otp, type, expires_at) 
                    VALUES (%s, %s, %s, %s)
                """, (email, otp, 'signup', expires_at))
                
                conn.commit()

                # Send Email
                email_body = f"<h2>Verify Your Email</h2><p>Your code is: <b>{otp}</b></p>"
                if rec_fun.send_email(email, "Signup Verification", email_body):
                    return jsonify({'success': True, 'message': 'OTP sent to email'}), 200
                else:
                    return jsonify({'success': False, 'message': 'Email failed to send'}), 500

            except Exception as e:
                print(f"Signup Error: {e}")
                return jsonify({'success': False, 'message': str(e)}), 500
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

    def verify_otp():
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        
        # Verify OTP
        cursor.execute("""
            SELECT * FROM otp_verification 
            WHERE email = %s AND otp = %s AND type = 'signup' AND expires_at > NOW()
        """, (email, otp))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Invalid or expired OTP'}), 400

        # Move from pending to permanent
        cursor.execute("SELECT * FROM pending_users WHERE email = %s", (email,))
        pending = cursor.fetchone()
        
        if pending:
            cursor.execute("""
                INSERT INTO users (photo, full_name, date_of_birth, email, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (pending['photo'], pending['full_name'], pending['date_of_birth'], pending['email'], pending['password']))
            
            cursor.execute("DELETE FROM pending_users WHERE email = %s", (email,))
            cursor.execute("DELETE FROM otp_verification WHERE email = %s AND type = 'signup'", (email,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Account verified! You can now login.'}), 200
        
        return jsonify({'success': False, 'message': 'User data not found'}), 404

    @staticmethod
    def resend_signup_otp():
        email = request.json.get('email')
        if rec_fun.handle_resend_otp(email, 'signup'):
            return jsonify({'success': True, 'message': 'New OTP sent!'}), 200
        return jsonify({'success': False, 'message': 'Failed to send OTP'}), 500