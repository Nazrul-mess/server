from flask import request, jsonify
import bcrypt
from function import RequirementFunctions
from database import Database
from datetime import datetime, timedelta

rec_fun = RequirementFunctions()
db = Database()

class SigninHandler:
    @staticmethod
    def signin():
        
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        conn = db.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        # if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        #     return jsonify({'success': True, 'message': 'sign in successful!', 'user': {'name': user['full_name']}}), 200

        # Inside login.py -> LoginHandler.login()
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({
                'success': True, 
                'message': 'Login successful!', 
                'user': {
                    'name': user['full_name'],
                    'email': user['email'],
                    'dob': str(user['date_of_birth']), # Format for JSON
                    'photo': user['photo'] 
                }
            }), 200
        
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    @staticmethod
    def request_password_reset():
        email = request.json.get('email')
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Email not found'}), 404
            
        if rec_fun.handle_resend_otp(email, 'reset'):
            return jsonify({'success': True, 'message': 'Reset code sent to email'}), 200
        return jsonify({'success': False, 'message': 'Error sending code'}), 500

    @staticmethod
    def reset_password():
        data = request.json
        email, otp, new_password = data.get('email'), data.get('otp'), data.get('password')
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM otp_verification WHERE email = %s AND otp = %s AND type = 'reset' AND expires_at > NOW()", (email, otp))
        
        if cursor.fetchone():
            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_pw, email))
            # FIX: This is more explicit and matches the OTP we verified
            cursor.execute("DELETE FROM otp_verification WHERE email = %s AND otp = %s AND type = 'reset'", (email, otp))
            conn.commit()
            return jsonify({'success': True, 'message': 'Password updated!'}), 200
            
        return jsonify({'success': False, 'message': 'Invalid or expired code'}), 400
