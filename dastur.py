import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox
)

def setup_database():
    conn = sqlite3.connect("telegram.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS whatsapp (
        login VARCHAR(50),
        parol VARCHAR(50),
        inchat TEXT,
        outchat TEXT
    )
    ''')
    cursor.execute("INSERT OR IGNORE INTO whatsapp (login, parol, inchat, outchat) VALUES ('Admin', '12345', '', '')")
    cursor.execute("INSERT OR IGNORE INTO whatsapp (login, parol, inchat, outchat) VALUES ('User', '54321', '', '')")
    conn.commit()
    conn.close()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Form")
        self.setGeometry(100, 100, 300, 200)

        self.login_label = QLabel("Login:")
        self.login_input = QLineEdit()

        self.password_label = QLabel("Parol:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.check_credentials)

        layout = QVBoxLayout()
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def check_credentials(self):
        login = self.login_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect("telegram.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM whatsapp WHERE login=? AND parol=?", (login, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.open_second_window(login)
        else:
            QMessageBox.warning(self, "Xato", "Login yoki parol noto'g'ri!")

    def open_second_window(self, login):
        self.second_window = ChatWindow(login)
        self.second_window.show()
        self.close()

class ChatWindow(QWidget):
    def __init__(self, user_login):
        super().__init__()
        self.setWindowTitle("Chat Oynasi")
        self.setGeometry(200, 200, 400, 400)
        self.user_login = user_login

        # Elementlar
        self.to_label = QLabel("Kimga (Login):")
        self.to_input = QLineEdit()

        self.inchat_label = QLabel("Kiruvchi xabar:")
        self.inchat_display = QTextEdit()
        self.inchat_display.setReadOnly(True)

        self.outchat_label = QLabel("Yuboriluvchi xabar:")
        self.outchat_input = QTextEdit()

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.to_label)
        layout.addWidget(self.to_input)
        layout.addWidget(self.inchat_label)
        layout.addWidget(self.inchat_display)
        layout.addWidget(self.outchat_label)
        layout.addWidget(self.outchat_input)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

        self.load_inchat()

    def load_inchat(self):
        conn = sqlite3.connect("telegram.db")
        cursor = conn.cursor()

        cursor.execute("SELECT inchat FROM whatsapp WHERE login=?", (self.user_login,))
        result = cursor.fetchone()
        conn.close()

        self.inchat_display.setText(result[0] if result else "")

    def send_message(self):
        to_login = self.to_input.text()
        message = self.outchat_input.toPlainText()

        if not to_login or not message:
            QMessageBox.warning(self, "Xato", "Login va xabar maydonlarini to'ldiring!")
            return

        conn = sqlite3.connect("telegram.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM whatsapp WHERE login=?", (to_login,))
        recipient = cursor.fetchone()

        if recipient:
            cursor.execute("UPDATE whatsapp SET inchat=? WHERE login=?", (message, to_login))
            conn.commit()
            QMessageBox.information(self, "Yuborildi", "Xabar muvaffaqiyatli yuborildi!")
        else:
            QMessageBox.warning(self, "Xato", "Foydalanuvchi topilmadi!")

        conn.close()

if __name__ == "__main__":
    setup_database()
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())