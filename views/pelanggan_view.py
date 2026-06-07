"""
SmartTravel - Pelanggan View
CRUD lengkap untuk manajemen data pelanggan.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QMessageBox, QFrame, QSizePolicy,
    QTextEdit, QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from utils.theme import (
    SECONDARY, ACCENT, DANGER, SUCCESS, BG_CARD, BG_MEDIUM,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, BORDER,
)
from controllers.controllers import PelangganController


class PelangganDialog(QDialog):
    """Dialog untuk tambah / edit pelanggan."""

    def __init__(self, parent=None, pelanggan=None):
        super().__init__(parent)
        self.pelanggan = pelanggan
        self.setWindowTitle("Edit Pelanggan" if pelanggan else "Tambah Pelanggan")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #1B2A3B;
            }}
            QLabel {{
                color: #F0F4F8;
                font-size: 12px;
            }}
            QLineEdit, QTextEdit {{
                background-color: #162435;
                border: 1px solid #1E3A5F;
                border-radius: 6px;
                padding: 8px 12px;
                color: #F0F4F8;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid #1565C0;
            }}
            QPushButton {{
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 22px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #1976D2; }}
            QPushButton#btnCancel {{
                background-color: transparent;
                color: #8EADC1;
                border: 1px solid #1E3A5F;
            }}
            QPushButton#btnCancel:hover {{
                background-color: #1B2A3B;
                color: #F0F4F8;
            }}
        """)
        self._build_ui()
        if pelanggan:
            self._fill(pelanggan)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        title = QLabel("✏️  Edit Pelanggan" if self.pelanggan else "➕  Tambah Pelanggan", parent=self)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F0F4F8;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.inp_nama    = QLineEdit()
        self.inp_nama.setPlaceholderText("Nama lengkap...")
        self.inp_email   = QLineEdit()
        self.inp_email.setPlaceholderText("email@example.com")
        self.inp_telepon = QLineEdit()
        self.inp_telepon.setPlaceholderText("+62...")
        self.inp_alamat  = QTextEdit()
        self.inp_alamat.setPlaceholderText("Alamat lengkap...")
        self.inp_alamat.setMaximumHeight(80)

        form.addRow("Nama *",    self.inp_nama)
        form.addRow("Email",     self.inp_email)
        form.addRow("Telepon",   self.inp_telepon)
        form.addRow("Alamat",    self.inp_alamat)
        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_cancel = QPushButton("Batal", parent=self)
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Simpan", parent=self)
        self.btn_save.clicked.connect(self._on_save)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        lay.addLayout(btn_row)

    def _fill(self, p):
        self.inp_nama.setText(p.nama)
        self.inp_email.setText(p.email or "")
        self.inp_telepon.setText(p.telepon or "")
        self.inp_alamat.setText(p.alamat or "")

    def _on_save(self):
        self.result_data = {
            "nama":    self.inp_nama.text().strip(),
            "email":   self.inp_email.text().strip(),
            "telepon": self.inp_telepon.text().strip(),
            "alamat":  self.inp_alamat.toPlainText().strip(),
        }
        self.accept()

    def get_data(self) -> dict:
        return self.result_data


class PelangganView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # ── Header ───────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("Kelola Pelanggan", parent=self)
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F0F4F8;")
        hdr.addWidget(title)
        hdr.addStretch()

        self.btn_add = QPushButton("＋  Tambah Pelanggan", parent=self)
        self.btn_add.setObjectName("btnAccent")
        self.btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #E55A25; }}
        """)
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self._on_add)
        hdr.addWidget(self.btn_add)
        main.addLayout(hdr)

        # ── Search bar ───────────────────────────────────────────────────────
        search_row = QHBoxLayout()
        self.search_input = QLineEdit(parent=self)
        self.search_input.setPlaceholderText("🔍  Cari nama, email, atau telepon...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #162435;
                border: 1px solid #1E3A5F;
                border-radius: 8px;
                padding: 10px 16px;
                color: #F0F4F8;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {SECONDARY}; }}
        """)
        self.search_input.textChanged.connect(self._on_search)
        search_row.addWidget(self.search_input)

        self.lbl_count = QLabel("0 pelanggan", parent=self)
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; min-width: 90px;")
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        search_row.addWidget(self.lbl_count)
        main.addLayout(search_row)

        # ── Table ────────────────────────────────────────────────────────────
        self.table = QTableWidget(parent=self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Email", "Telepon", "Alamat", "Aksi"])
        
        # Menggunakan setSectionResizeMode secara individual untuk kestabilan grafik Mac
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(5, 190) # Lebar aman setelah fungsi penggantung dibersihkan
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_MEDIUM};
                border: none;
                border-radius: 10px;
                alternate-background-color: {BG_CARD};
            }}
            QTableWidget::item {{
                padding: 10px 12px;
            }}
            QTableWidget::item:selected {{
                background-color: #1565C055;
                color: #F0F4F8;
            }}
            QHeaderView::section {{
                background-color: #0A2342;
                color: #4A6B80;
                padding: 10px 12px;
                border: none;
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        main.addWidget(self.table)

    # ── Data ──────────────────────────────────────────────────────────────────
    def refresh_table(self, keyword: str = ""):
        data = PelangganController.search(keyword) if keyword else PelangganController.get_all()
        self._populate(data)

    def _populate(self, data):
        self.table.setRowCount(0)
        self.lbl_count.setText(f"{len(data)} pelanggan")
        for row_idx, p in enumerate(data):
            self.table.insertRow(row_idx)
            for col, val in enumerate([p.id, p.nama, p.email, p.telepon, p.alamat]):
                item = QTableWidgetItem(str(val or ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row_idx, col, item)
            
            # Pasang widget aksi kustom secara aman
            action_widget = self._make_action_btns(p)
            self.table.setCellWidget(row_idx, 5, action_widget)
            
            # Set tinggi baris secara eksplisit di dalam loop dengan benar
            self.table.setRowHeight(row_idx, 52)

    def _make_action_btns(self, p) -> QWidget:
        # Ikat langsung ke self.table sebagai induk objek C++
        w = QWidget(self.table)
        w.setStyleSheet("background: transparent;")
        
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_edit = QPushButton("✏️ Edit", parent=w)
        btn_edit.setFixedHeight(32)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {SECONDARY};
                color: white; border: none; border-radius: 6px;
                padding: 0 14px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #1976D2; }}
        """)
        btn_edit.clicked.connect(lambda _, obj=p: self._on_edit(obj))

        btn_del = QPushButton("🗑️ Hapus", parent=w)
        btn_del.setFixedHeight(32)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {DANGER}; border: 1px solid {DANGER}; border-radius: 6px;
                padding: 0 14px; font-size: 12px; font-weight: 600;
            }}
            QPushButton:hover {{ 
                background-color: {DANGER}1A; 
                color: #FF6B6B;
                border-color: #FF6B6B;
            }}
        """)
        btn_del.clicked.connect(lambda _, obj=p: self._on_delete(obj))

        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)
        return w

    # ── Slots ─────────────────────────────────────────────────────────────────
    def _on_search(self, text: str):
        self.refresh_table(text)

    def _on_add(self):
        dlg = PelangganDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = PelangganController.create(d["nama"], d["email"], d["telepon"], d["alamat"])
            self._show_msg(ok, msg)
            if ok:
                self.refresh_table()

    def _on_edit(self, p):
        dlg = PelangganDialog(self, pelanggan=p)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = PelangganController.update(p.id, d["nama"], d["email"], d["telepon"], d["alamat"])
            self._show_msg(ok, msg)
            if ok:
                self.refresh_table()

    def _on_delete(self, p):
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus pelanggan <b>{p.nama}</b>?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = PelangganController.delete(p.id)
            self._show_msg(ok, msg)
            if ok:
                self.refresh_table()

    def _show_msg(self, ok: bool, msg: str):
        mb = QMessageBox(self)
        mb.setWindowTitle("Info")
        mb.setText(msg)
        mb.setIcon(QMessageBox.Icon.Information if ok else QMessageBox.Icon.Warning)
        mb.setStyleSheet("QMessageBox { background-color: #1B2A3B; } QLabel { color: #F0F4F8; }")
        mb.exec()