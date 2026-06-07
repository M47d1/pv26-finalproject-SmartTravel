"""
SmartTravel - Main Window
Window utama dengan sidebar navigasi dan stacked pages.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QSizePolicy, QMessageBox, QSpacerItem,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from utils.theme import (
    SIDEBAR_STYLE, MAIN_STYLE, PRIMARY, SECONDARY, ACCENT,
    BG_DARK, BG_MEDIUM, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    SIDEBAR_W,
)
from controllers.controllers import AuthController, TransaksiController
from views.dashboard_view  import DashboardView
from views.pelanggan_view  import PelangganView
from views.paket_view      import PaketView
from views.transaksi_view  import TransaksiView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartTravel – Sistem Manajemen Reservasi & Paket Wisata")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 780)
        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()

    # ── UI Build ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget(parent=self)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_sidebar())
        root.addWidget(self._make_content_area())

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _make_sidebar(self) -> QWidget:
        sidebar = QWidget(parent=self)
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(SIDEBAR_W)
        sidebar.setStyleSheet(SIDEBAR_STYLE + f"QWidget#sidebar {{ background-color: {PRIMARY}; }}")

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(12, 16, 12, 16)
        lay.setSpacing(4)

        # ── Logo area ────────────────────────────────────────────────────────
        logo_frame = QFrame(parent=sidebar)
        logo_frame.setFixedHeight(72)
        logo_frame.setStyleSheet("background: transparent; border-bottom: 1px solid #0D1F35;")
        logo_lay = QHBoxLayout(logo_frame)
        logo_lay.setContentsMargins(8, 0, 8, 0)

        icon_lbl = QLabel("✈", parent=logo_frame)
        icon_lbl.setStyleSheet(f"""
            font-size: 22px;
            background-color: {ACCENT};
            border-radius: 10px;
            padding: 6px;
            color: white;
        """)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lay.addWidget(icon_lbl)

        name_lay = QVBoxLayout()
        name_lay.setSpacing(0)
        t1 = QLabel("SmartTravel", parent=logo_frame)
        t1.setStyleSheet("font-size: 14px; font-weight: 800; color: #F0F4F8; background: transparent;")
        t2 = QLabel("Admin Panel", parent=logo_frame)
        t2.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; background: transparent;")
        name_lay.addWidget(t1)
        name_lay.addWidget(t2)
        logo_lay.addLayout(name_lay)
        logo_lay.addStretch()
        lay.addWidget(logo_frame)

        lay.addSpacing(10)

        # ── Section label ────────────────────────────────────────────────────
        # 🔥 PERBAIKAN 1: Hapus total background gelap pada balok "MENU UTAMA"
        sec_lbl = QLabel("MENU UTAMA", parent=sidebar)
        sec_lbl.setStyleSheet(f"""
            font-size: 9px; 
            font-weight: 700; 
            color: {TEXT_MUTED}; 
            padding-left: 8px; 
            letter-spacing: 1.2px;
            background: transparent;
            background-color: transparent;
        """)
        lay.addWidget(sec_lbl)
        lay.addSpacing(4)

        # ── Nav buttons ──────────────────────────────────────────────────────
        nav_items = [
            ("📊", "Dashboard",   0),
            ("👥", "Pelanggan",   1),
            ("🌴", "Paket Wisata", 2),
            ("🗓️", "Reservasi",   3),
        ]
        self._nav_btns = []
        for icon, label, page_idx in nav_items:
            btn = QPushButton(f"  {icon}  {label}", parent=sidebar)
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn.setStyleSheet(f"""
                QPushButton#navBtn {{
                    color: {TEXT_SECONDARY}; background: transparent; border: none;
                    border-radius: 8px; text-align: left; padding-left: 16px; font-size: 13px; font-weight: 500;
                }}
                QPushButton#navBtn:hover {{ background-color: #1A365D; color: white; }}
                QPushButton#navBtn:checked {{ background-color: #1565C0; color: white; font-weight: 700; }}
            """)
            
            btn.clicked.connect(lambda _, i=page_idx: self._switch_page(i))
            self._nav_btns.append(btn)
            lay.addWidget(btn)

        lay.addStretch()

        # ── User info + logout ────────────────────────────────────────────────
        sep = QFrame(parent=sidebar)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #0D1F35; max-height: 1px; border: none;")
        lay.addWidget(sep)
        lay.addSpacing(8)

        user = AuthController.get_current_user()
        uname = user.username if user else "admin"
        
        # 🔥 PERBAIKAN 2: Hapus total background gelap pada balok nama user "admin"
        user_lbl = QLabel(f"👤  {uname}", parent=sidebar)
        user_lbl.setStyleSheet(f"""
            color: {TEXT_SECONDARY}; 
            font-size: 12px; 
            padding: 6px 8px;
            background: transparent;
            background-color: transparent;
        """)
        lay.addWidget(user_lbl)

        btn_logout = QPushButton("  ⏻  Keluar", parent=sidebar)
        btn_logout.setObjectName("navBtn")
        btn_logout.setFixedHeight(40)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton#navBtn {{
                color: #E74C3C; background: transparent; border: none;
                border-radius: 8px; padding: 0 16px; text-align: left; font-size: 13px; font-weight: 600;
            }}
            QPushButton#navBtn:hover {{ background-color: rgba(231,76,60,0.15); }}
        """)
        btn_logout.clicked.connect(self._on_logout)
        lay.addWidget(btn_logout)

        return sidebar

    def _make_content_area(self) -> QWidget:
        """Stacked widget berisi semua halaman."""
        container = QWidget(parent=self)
        container.setStyleSheet(f"background-color: {BG_DARK};")

        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.stack = QStackedWidget(parent=container)

        self.page_dashboard  = DashboardView(parent=self)
        self.page_pelanggan  = PelangganView(parent=self)
        self.page_paket      = PaketView(parent=self)
        self.page_transaksi  = TransaksiView(parent=self)

        self.stack.addWidget(self.page_dashboard)   # 0
        self.stack.addWidget(self.page_pelanggan)   # 1
        self.stack.addWidget(self.page_paket)       # 2
        self.stack.addWidget(self.page_transaksi)   # 3

        lay.addWidget(self.stack)
        return container

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(i == index)
            
        if index == 0:
            stats = TransaksiController.get_stats()
            self.page_dashboard.refresh(stats)
        elif index == 1:
            self.page_pelanggan.refresh_table()
        elif index == 2:
            self.page_paket.refresh_table()
        elif index == 3:
            self.page_transaksi.refresh_table()

    def showEvent(self, event):
        super().showEvent(event)
        self._switch_page(0)

    def _on_logout(self):
        reply = QMessageBox.question(
            self, "Keluar",
            "Yakin ingin keluar dari sistem?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            AuthController.logout()
            self.close()
            from main import restart_to_login
            restart_to_login()