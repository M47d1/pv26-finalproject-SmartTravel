"""
SmartTravel - Login View
Halaman autentikasi admin dengan desain premium travel.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor, QFont, QPixmap, QPainter, QLinearGradient

from utils.theme import LOGIN_STYLE, ACCENT, SECONDARY, TEXT_MUTED, TEXT_SECONDARY


class LoginView(QWidget):
    """Emits login_requested(username, password) saat tombol login diklik."""

    login_requested = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(LOGIN_STYLE)
        self._build_ui()

    # ── UI Build ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Gunakan stretch 1:1 atau tanpa stretch eksplisit agar memori layout di Mac stabil
        root.addWidget(self._make_brand_panel())
        root.addWidget(self._make_form_panel())

    def _make_brand_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("brandPanel")
        panel.setStyleSheet(f"""
            QWidget#brandPanel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0A2342,
                    stop:0.5 #0D3B6E,
                    stop:1 #1565C0
                );
            }}
        """)

        # Layout vertikal utama panel kiri
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(50, 60, 50, 60)
        lay.setSpacing(20)

        # Mendorong konten utama agar turun pas ke tengah layar
        lay.addStretch()

        # Logo / Icon area
        icon_lbl = QLabel("✈", parent=panel)  # Eksplisit berikan parent agar aman di memori
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            font-size: 72px;
            color: white;
            background: rgba(255,255,255,0.08);
            border-radius: 30px;
            padding: 20px;
            border: none;
        """)
        icon_lbl.setFixedSize(130, 130)
        
        icon_wrap = QHBoxLayout()
        icon_wrap.addStretch()
        icon_wrap.addWidget(icon_lbl)
        icon_wrap.addStretch()
        lay.addLayout(icon_wrap)

        # Title
        title = QLabel("SmartTravel", parent=panel)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 38px;
            font-weight: 800;
            color: white;
            letter-spacing: -1px;
            background: transparent;
            border: none;
        """)
        lay.addWidget(title)

        # Tagline
        tagline = QLabel("Sistem Manajemen Reservasi\n& Paket Wisata", parent=panel)
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet(f"""
            font-size: 15px;
            color: rgba(255,255,255,0.65);
            line-height: 1.6;
            background: transparent;
            border: none;
        """)
        lay.addWidget(tagline)

        # Mendorong konten utama ke atas, memberikan ruang proporsional untuk credit
        lay.addStretch()

        # Footer credit
        credit = QLabel("Tugas Akhir Pemrograman Visual · 2024", parent=panel)
        credit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credit.setStyleSheet("color: rgba(255,255,255,0.30); font-size: 11px; background: transparent; border: none;")
        lay.addWidget(credit)

        return panel

    def _make_form_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("formPanel")
        panel.setStyleSheet("background-color: #0D1B2A;")

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(0, 0, 0, 0)

        # Centered card
        card_wrap = QHBoxLayout()
        card_wrap.addStretch()
        card_wrap.addWidget(self._make_card())
        card_wrap.addStretch()
        outer.addStretch()
        outer.addLayout(card_wrap)
        outer.addStretch()

        return panel

    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setFixedWidth(380)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #162435;
                border-radius: 16px;
                border: 1px solid #1E3A5F;
            }}
            QLineEdit {{
                background-color: #0D1B2A;
                border: 1px solid #1E3A5F;
                border-radius: 8px;
                padding: 0px 12px;
                color: #F0F4F8;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid #1565C0;
            }}
            QPushButton#btnLogin {{
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QPushButton#btnLogin:hover {{
                background-color: #1976D2;
            }}
            QPushButton#btnLogin:pressed {{
                background-color: #0D47A1;
            }}
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(36, 40, 36, 40)
        lay.setSpacing(0)

        # Header
        hello = QLabel("Selamat Datang 👋", parent=card)
        hello.setStyleSheet("font-size: 24px; font-weight: 700; color: #F0F4F8; background: transparent; border: none;")
        lay.addWidget(hello)

        sub = QLabel("Masuk ke panel admin SmartTravel", parent=card)
        sub.setStyleSheet("font-size: 13px; color: #8EADC1; margin-top: 6px; background: transparent; border: none;")
        lay.addWidget(sub)

        lay.addSpacing(32)

        # Username
        lbl_u = QLabel("USERNAME", parent=card)
        lbl_u.setStyleSheet("font-size: 11px; font-weight: 700; color: #4A6B80; letter-spacing: 1px; background: transparent; border: none;")
        lay.addWidget(lbl_u)
        lay.addSpacing(6)

        self.input_username = QLineEdit(parent=card)
        self.input_username.setPlaceholderText("Masukkan username...")
        self.input_username.setFixedHeight(46)
        lay.addWidget(self.input_username)

        lay.addSpacing(18)

        # Password
        lbl_p = QLabel("PASSWORD", parent=card)
        lbl_p.setStyleSheet("font-size: 11px; font-weight: 700; color: #4A6B80; letter-spacing: 1px; background: transparent; border: none;")
        lay.addWidget(lbl_p)
        lay.addSpacing(6)

        self.input_password = QLineEdit(parent=card)
        self.input_password.setPlaceholderText("Masukkan password...")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setFixedHeight(46)
        self.input_password.returnPressed.connect(self._on_login_clicked)
        lay.addWidget(self.input_password)

        lay.addSpacing(28)

        # Login button
        self.btn_login = QPushButton("MASUK  →", parent=card)
        self.btn_login.setObjectName("btnLogin")
        self.btn_login.setFixedHeight(50)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self._on_login_clicked)
        lay.addWidget(self.btn_login)

        lay.addSpacing(18)

        # Error label (hidden by default)
        self.lbl_error = QLabel("", parent=card)
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setStyleSheet(f"""
            color: #E74C3C;
            background: rgba(231,76,60,0.12);
            border: 1px solid rgba(231,76,60,0.3);
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        """)
        self.lbl_error.hide()
        lay.addWidget(self.lbl_error)

        lay.addSpacing(20)

        return card

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_login_clicked(self):
        username = self.input_username.text().strip()
        password = self.input_password.text()
        if not username or not password:
            self.show_error("Username dan password tidak boleh kosong.")
            return
        self.lbl_error.hide()
        self.login_requested.emit(username, password)

    def show_error(self, message: str):
        self.lbl_error.setText(f"⚠  {message}")
        self.lbl_error.show()
        self._shake(self.input_password)

    def _shake(self, widget):
        orig = widget.geometry()
        self._shake_anim = QPropertyAnimation(widget, b"geometry", self)
        self._shake_anim.setDuration(300)
        self._shake_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        dx = 8
        self._shake_anim.setKeyValueAt(0.0, QRect(orig.x(),      orig.y(), orig.width(), orig.height()))
        self._shake_anim.setKeyValueAt(0.2, QRect(orig.x() - dx, orig.y(), orig.width(), orig.height()))
        self._shake_anim.setKeyValueAt(0.4, QRect(orig.x() + dx, orig.y(), orig.width(), orig.height()))
        self._shake_anim.setKeyValueAt(0.6, QRect(orig.x() - dx, orig.y(), orig.width(), orig.height()))
        self._shake_anim.setKeyValueAt(0.8, QRect(orig.x() + dx, orig.y(), orig.width(), orig.height()))
        self._shake_anim.setKeyValueAt(1.0, QRect(orig.x(),      orig.y(), orig.width(), orig.height()))
        self._shake_anim.start()

    def clear_fields(self):
        self.input_username.clear()
        self.input_password.clear()
        self.lbl_error.hide()