"""
SmartTravel - Entry Point
Titik masuk aplikasi. Menginisialisasi database, menampilkan login,
lalu main window setelah autentikasi berhasil.

Cara jalankan:
    python main.py

Requirements:
    pip install -r requirements.txt
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

# Bootstrap
from config.database import initialize_database
from controllers.controllers import AuthController
from views.login_view import LoginView
from views.main_window import MainWindow


# ── Module-level references ──────────────────────────────────────────────────
_app: QApplication | None = None
_login_window: LoginView  | None = None
_main_window:  MainWindow | None = None


def restart_to_login():
    """Dipanggil dari MainWindow saat logout agar kembali ke LoginView."""
    global _main_window, _login_window
    if _main_window:
        _main_window.close()
        _main_window = None
    show_login()


def show_login():
    global _login_window
    _login_window = LoginView()
    _login_window.setWindowTitle("SmartTravel – Login")
    _login_window.resize(1100, 680)
    _login_window.login_requested.connect(_handle_login)
    _login_window.show()


def _handle_login(username: str, password: str):
    global _login_window, _main_window

    ok, msg = AuthController.login(username, password)
    if ok:
        # 🔥 PERBAIKAN 1: Buat dan tampilkan MainWindow terlebih dahulu
        _main_window = MainWindow()
        _main_window.show()

        # 🔥 PERBAIKAN 2: Sembunyikan login window, lalu jadwalkan penghapusan objek 
        # dari memori secara aman menggunakan deleteLater() agar event loop Qt tidak putus.
        if _login_window:
            _login_window.hide()
            _login_window.deleteLater()
            _login_window = None
    else:
        if _login_window:
            _login_window.show_error(msg)


def main():
    global _app

    # 1. Init database (buat tabel + seed jika belum ada)
    initialize_database()

    # 2. QApplication
    _app = QApplication(sys.argv)
    _app.setApplicationName("SmartTravel")
    _app.setApplicationVersion("1.0.0")
    _app.setOrganizationName("SmartTravel Team")

    # 🔥 PERBAIKAN 3: Gunakan array font-family fallback agar tidak memicu crash font di Mac
    font = QFont()
    font.setFamilies(["-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Helvetica", "Arial"])
    font.setPointSize(10)
    _app.setFont(font)

    # 🔥 PERBAIKAN 4: Matikan atau komentari baris berat atribut deprecated ini 
    # karena di PySide6 High DPI Pixmaps sudah otomatis menyala secara bawaan.
    # _app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # 3. Tampilkan login
    show_login()

    # 4. Event loop
    sys.exit(_app.exec())


if __name__ == "__main__":
    main()