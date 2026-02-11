from flask import request, jsonify
import bcrypt
from function import RequirementFunctions
from database import Database
import uuid

rec_fun = RequirementFunctions()
db = Database()

class SigninHandler:
    @staticmethod
    def signin():
        conn = None
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            
            conn = db.connect()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
        
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session_token = str(uuid.uuid4())
                cursor.execute("UPDATE users SET current_session = %s WHERE user_id = %s", (session_token, user['user_id']))
                conn.commit()
                return jsonify({
                    'success': True, 
                    'message': 'Login successful!', 
                    'user': {
                        'user_id': user['user_id'],
                        'name': user['full_name'],
                        'email': user['email'],
                        'gender': user['gender'],
                        'phone': user['phone_number'],
                        'dob': str(user['date_of_birth']), # Format for JSON
                        'join_date' : str(user['created_at']),
                        'photo': user['photo'] 
                    }
                }), 200
            
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            if conn:
                conn.close()

    @staticmethod
    def request_password_reset():
        try:
            email = request.json.get('email')
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Email not found'}), 404
                
            if rec_fun.handle_resend_otp(email, 'reset'):
                return jsonify({'success': True, 'message': 'Reset code sent to email'}), 200
            return jsonify({'success': False, 'message': 'Error sending code'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            if conn:
                conn.close()

    @staticmethod
    def reset_password():
        try:
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
                cursor.execute("DELETE FROM otp_verification WHERE email = %s AND otp = %s AND type = 'reset'", (email, otp))
                conn.commit()
                return jsonify({'success': True, 'message': 'Password updated!'}), 200
                
            return jsonify({'success': False, 'message': 'Invalid or expired code'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            if conn:
                conn.close()

    @staticmethod
    def update_profile():
        conn = None
        try:
            data = request.json
            user_id = data.get('user_id')
            email = data.get('email')
            
            # Password fields from frontend
            current_password = data.get('currentPassword')
            new_password = data.get('newPassword')

            conn = db.connect()
            cursor = conn.cursor(dictionary=True)

            # 1. Fetch the user's current record to verify identity and old password
            cursor.execute("SELECT password FROM users WHERE user_id = %s AND email = %s", (user_id, email))
            user = cursor.fetchone()

            if not user:
                return jsonify({'success': False, 'message': 'User verification failed'}), 401

            # 2. Determine the password to store
            final_password_hash = user['password'] # Default: keep the old one
            
            if new_password: # User wants to change password
                if not current_password:
                    return jsonify({'success': False, 'message': 'Current password required to set new password'}), 400
                
                # Verify the old password matches what's in the DB
                if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                    return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401
                
                # Hash the new password
                final_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 3. Update the database
            query = """
                UPDATE users 
                SET full_name = %s, date_of_birth = %s, gender = %s, phone_number = %s, photo = %s, password = %s
                WHERE user_id = %s AND email = %s
            """
            params = (
                data.get('fullName'), data.get('dob'), data.get('gender'), 
                data.get('phone'), data.get('photo'), final_password_hash, 
                user_id, email
            )
            
            cursor.execute(query, params)
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Profile updated successfully!'}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': 'Internal Server Error'}), 500
        finally:
            if conn: conn.close()