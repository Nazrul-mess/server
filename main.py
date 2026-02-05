from flask import Flask
from flask_cors import CORS
from signup import SignupHandler
from login import LoginHandler
from database import Database

db = Database()
db.create_tables()

app = Flask(__name__)
CORS(app)

# Signup Routes
@app.route('/api/signup', methods=['POST'])
def signup(): return SignupHandler.signup()

@app.route('/api/signup/verify', methods=['POST'])
def verify_signup(): return SignupHandler.verify_otp()

@app.route('/api/signup/resend', methods=['POST'])
def resend_signup(): return SignupHandler.resend_signup_otp()

# Login & Reset Routes
@app.route('/api/login', methods=['POST'])
def login(): return LoginHandler.login()

@app.route('/api/forgot-password/request', methods=['POST'])
def forgot_req(): return LoginHandler.request_password_reset()

@app.route('/api/forgot-password/reset', methods=['POST'])
def forgot_reset(): return LoginHandler.reset_password()

#print server is active 
print("Server is running...")

if __name__ == '__main__':
    app.run(debug=True)