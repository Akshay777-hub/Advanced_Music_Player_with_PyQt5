#!/usr/bin/python3

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import *
import sys
from supabase import create_client, Client

LoginUI, _ = loadUiType('login.ui')

# Supabase config
supabaseUrl = "https://mrxbxtuptrdmfgvdbofk.supabase.co"
supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1yeGJ4dHVwdHJkbWZndmRib2ZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjg5Mzc1OTQsImV4cCI6MjA0NDUxMzU5NH0.3v1kGzwEdV8CBql4kQ5iW4ep2cUDxdfdcKThEkuP3ew"

supabase: Client = create_client(supabaseUrl, supabaseKey)

class Login(QMainWindow, LoginUI):
    login_success = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.btn_login.clicked.connect(self.loginfunction)
        self.btn_to_create.clicked.connect(self.gotocreate)
        self.go_to_login.clicked.connect(self.backtologin)
        self.btn_creat.clicked.connect(self.create_account)

        self.btn_exit.clicked.connect(self.close)

    def create_account(self):
        email = self.creat_user.text()
        password = self.creat_passwd1.text()
        confirm_password = self.creat_passwd2.text()

        if not email:
            self.invalid1.setText("Email cannot be empty.")
            self.invalid1.setVisible(True)
            return

        if password != confirm_password:
            self.invalid1.setText("Passwords do not match.")
            self.invalid1.setVisible(True)
            return

        if len(password) < 6:
            self.invalid1.setText("Password must be at least 6 characters.")
            self.invalid1.setVisible(True)
            return

        try:
            # Insert new user into custom_users table
            response = supabase.table('custom_users').insert({
                'email': email,
                'password': password
            }).execute()

            print(f"Raw Supabase response: {response}")

            if 200 <= response.status_code < 300:  # Check for success status code
                print("Account created successfully!")
                self.invalid1.setText("Account created successfully!")
                self.invalid1.setStyleSheet("color: green;")
                self.invalid1.setVisible(True)
                self.backtologin()
            else:
                if 'message' in response.json():  # Check if message is in json
                    error_message = response.json()['message']
                elif 'error' in response.json():
                    error_message = response.json()['error']
                else:
                    error_message = "An unexpected error occurred during signup."
                self.invalid1.setText(str(error_message))
                self.invalid1.setVisible(True)
                print(f"Signup error: {error_message}")

        except Exception as e:
            self.invalid1.setText("An unexpected error occurred during signup.")
            self.invalid1.setVisible(True)
            print(f"An unexpected error during signup: {e}")

    def loginfunction(self):
        email = self.login_user.text()
        password = self.login_passwd.text()

        try:
            # Fetch the user by email
            response = supabase.table('custom_users').select('*').eq('email', email).execute()
            user_data = response.data

            if not user_data:
                self.invalid.setText("User not found.")
                self.invalid.setVisible(True)
                return

            user = user_data[0]
            stored_password = user['password']

            # Compare the stored password directly (no hashing)
            if password == stored_password:
                self.invalid.setText("Login Successful!")
                self.invalid.setStyleSheet("color: green;")
                self.invalid.setVisible(True)
                print("Login successful!")
                print("Emitting signal...")  # Add this
                self.login_success.emit(str(user['id']))  # Make sure uuid is a string
                print("Signal emitted")  # Add this
                self.close()
                # TODO:  Put your code here for what happens after a successful login (e.g., open a new window)
            else:
                self.invalid.setText("Invalid credentials.")
                self.invalid.setVisible(True)

        except Exception as e:
            self.invalid.setText("An unexpected error occurred.")
            self.invalid.setVisible(True)
            print(f"An unexpected error occurred: {e}")

    def gotocreate(self):
        self.stackedWidget.setCurrentWidget(self.pg_create)

    def backtologin(self):
        self.creat_user.clear()
        self.creat_passwd1.clear()
        self.creat_passwd2.clear()
        self.invalid1.setVisible(False)
        self.stackedWidget.setCurrentWidget(self.pg_login)

def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
