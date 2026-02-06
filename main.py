# main.py
from flask import Flask, jsonify
from flask_cors import CORS
from signup import SignupHandler
from signin import signinHandler
from database import Database
import os

db = Database()
db.create_tables()

app = Flask(__name__)
CORS(app)

# Add health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'Secure Auth API'}), 200

# Signup Routes
@app.route('/api/signup', methods=['POST'])
def signup(): return SignupHandler.signup()

@app.route('/api/signup/verify', methods=['POST'])
def verify_signup(): return SignupHandler.verify_otp()

@app.route('/api/signup/resend', methods=['POST'])
def resend_signup(): return SignupHandler.resend_signup_otp()

# Signin & Reset Routes
@app.route('/api/signin', methods=['POST'])
def signin(): return signinHandler.signin()

@app.route('/api/forgot-password/request', methods=['POST'])
def forgot_req(): return signinHandler.request_password_reset()

@app.route('/api/forgot-password/reset', methods=['POST'])
def forgot_reset(): return signinHandler.reset_password()

print("Server is running...")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
