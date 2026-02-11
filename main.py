from flask import Flask
from flask_cors import CORS
from signup import SignupHandler
from signin import SigninHandler
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

# signin & Reset Routes
@app.route('/api/signin', methods=['POST'])
def signin(): return SigninHandler.signin()

@app.route('/api/forgot-password/request', methods=['POST'])
def forgot_req(): return SigninHandler.request_password_reset()

@app.route('/api/forgot-password/reset', methods=['POST'])
def forgot_reset(): return SigninHandler.reset_password()

@app.route('/api/profile/update', methods=['POST'])
def update_profile(): return SigninHandler.update_profile()

@app.route('/')
def server_running(): return 'Server is running successfully!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)