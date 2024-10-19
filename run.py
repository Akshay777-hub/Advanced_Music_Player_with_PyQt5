from main import ModernMusicPlayer
from login_music import Login  # Import your login window
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtCore import pyqtSignal


class AppLauncher:  # Class to manage application flow
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        self.login_window = Login()
        self.login_window.login_success.connect(self.launch_main_app) # connect to the signal.
        self.login_window.show()
        self.app.exec_()
    
    def launch_main_app(self, user_uuid):
        self.main_window = ModernMusicPlayer(user_uuid)  # Pass uuid to main window
        self.main_window.show()
        self.login_window.close()


if __name__ == '__main__':
    launcher = AppLauncher()  # Create an instance of the launcher