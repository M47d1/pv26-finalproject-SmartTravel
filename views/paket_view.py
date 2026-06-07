"""
SmartTravel - Paket Wisata View
CRUD untuk manajemen paket wisata.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QMessageBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit, QAbstractItemView,
)
from PySide6.QtCore import Qt
from utils.theme import SECONDARY, ACCENT, DANGER, SUCCESS, BG_MEDIUM, BG_CARD, TEXT_MUTED
from controllers.controllers import PaketController


class PaketDialog(QDialog):
    def __init__(self, parent=None, paket=None):
        super().__init__(parent)
        self.paket = paket
        self.setWindowTitle("Edit Paket" if paket else "Tambah Paket Wisata")
        self.setMinimumWidth(440)
        self.setStyleSheet("""
            QDialog { background-color: #1B2A3B; }
            QLabel { color: #F0F4F8; font-size: 12px; }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #162435; border: 1px solid #1E3A5F;
                border-radius: 6px; padding: 8px 12px; color: #F0F4F8; font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #1565C0;
            }
            QPushButton {
                background-color: #1565C0; color: white; border: none;
                border-radius: 6px; padding: 9px 22px; font-weight: 600;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton#btnCancel {
                background-color: transparent; color: #8EADC1;
                border: 1px solid #1E3A5F;
            }
            QPushButton#btnCancel:hover { background-color: #1B2A3B; color: #F0F4F8; }
            QCheckBox { color: #F0F4F8; }
        """)
        self._build_ui()
        if paket:
            self._fill(paket)

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        title = QLabel("🌴  Edit Paket" if self.paket else "🌴  Tambah Paket Wisata", parent=self)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F0F4F8;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.inp_nama      = QLineEdit()
        self.inp_nama.setPlaceholderText("Nama paket wisata")
        self.inp_destinasi = QLineEdit()
        self.inp_destinasi.setPlaceholderText("Kota / destinasi")

        self.inp_durasi = QSpinBox()
        self.inp_durasi.setRange(1, 365)
        self.inp_durasi.setSuffix(" hari")
        self.inp_durasi.setValue(3)

        self.inp_harga = QDoubleSpinBox()
        self.inp_harga.setRange(0, 999_999_999)
        self.inp_harga.setSingleStep(100_000)
        self.inp_harga.setPrefix("Rp ")
        self.inp_harga.setDecimals(0)

        self.inp_deskripsi = QTextEdit()
        self.inp_deskripsi.setPlaceholderText("Deskripsi singkat paket...")
        self.inp_deskripsi.setMaximumHeight(80)

        self.chk_tersedia = QCheckBox("Paket tersedia untuk dijual")
        self.chk_tersedia.setChecked(True)

        form.addRow("Nama Paket *",   self.inp_nama)
        form.addRow("Destinasi *",    self.inp_destinasi)
        form.addRow("Durasi",         self.inp_durasi)
        form.addRow("Harga/Pax *",    self.inp_harga)
        form.addRow("Deskripsi",      self.inp_deskripsi)
        form.addRow("",               self.chk_tersedia)
        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Batal", parent=self)
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Simpan", parent=self)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        lay.addLayout(btn_row)

    def _fill(self, p):
        self.inp_nama.setText(p.nama_paket)
        self.inp_destinasi.setText(p.destinasi)
        self.inp_durasi.setValue(p.durasi_hari)
        self.inp_harga.setValue(p.harga)
        self.inp_deskripsi.setText(p.deskripsi or "")
        self.chk_tersedia.setChecked(bool(p.tersedia))

    def _on_save(self):
        self.result_data = {
            "nama_paket":  self.inp_nama.text().strip(),
            "destinasi":   self.inp_destinasi.text().strip(),
            "durasi_hari": self.inp_durasi.value(),
            "harga":       self.inp_harga.value(),
            "deskripsi":   self.inp_deskripsi.toPlainText().strip(),
            "tersedia":    1 if self.chk_tersedia.isChecked() else 0,
        }
        self.accept()

    def get_data(self):
        return self.result_data


class PaketView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Paket Wisata", parent=self)
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F0F4F8;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_add = QPushButton("＋  Tambah Paket", parent=self)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: white; border: none;
                border-radius: 6px; padding: 9px 18px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #E55A25; }}
        """)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._on_add)
        hdr.addWidget(btn_add)
        main.addLayout(hdr)

        # Table
        self.table = QTableWidget(parent=self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nama Paket", "Destinasi", "Durasi", "Harga/Pax", "Status", "Aksi"
        ])
        
        # 🔥 PERBAIKAN 1: Definisikan resize mode kolom demi kolom secara berurutan
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)        # ID
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Nama Paket
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)      # Destinasi
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)        # Durasi
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)      # Harga
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)        # Status
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)        # Aksi
        
        # Atur lebar absolut piksel
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(5, 90)
        self.table.setColumnWidth(6, 190) # Ditambah ke 190px agar tombol aksi punya ruang lega dan tidak gepeng
        
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_MEDIUM}; border: none; border-radius: 10px;
                alternate-background-color: {BG_CARD};
            }}
            QTableWidget::item {{ padding: 10px 12px; }}
            QTableWidget::item:selected {{ background-color: #1565C055; color: #F0F4F8; }}
            QHeaderView::section {{
                background-color: #0A2342; color: #4A6B80; padding: 10px 12px;
                border: none; font-size: 10px; font-weight: 700; letter-spacing: 1px;
            }}
        """)
        main.addWidget(self.table)

    def refresh_table(self):
        data = PaketController.get_all()
        self.table.setRowCount(0)
        for ri, p in enumerate(data):
            self.table.insertRow(ri)
            cells = [p.id, p.nama_paket, p.destinasi, f"{p.durasi_hari}H", f"Rp {p.harga:,.0f}"]
            for ci, val in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(ri, ci, item)
            
            # Status badge
            status_txt = "Tersedia" if p.tersedia else "Nonaktif"
            status_item = QTableWidgetItem(status_txt)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            status_item.setForeground(Qt.GlobalColor.green if p.tersedia else Qt.GlobalColor.gray)
            self.table.setItem(ri, 5, status_item)
            
            # 🔥 PERBAIKAN 2: Gunakan widget aksi kustom dengan siklus penanganan memori Mac
            action_widget = self._make_btns(p)
            self.table.setCellWidget(ri, 6, action_widget)
            
            # 🔥 PERBAIKAN 3: Berikan tinggi baris seragam di dalam loop (52px)
            self.table.setRowHeight(ri, 52)

    def _make_btns(self, p) -> QWidget:
        # 🔥 PERBAIKAN 4: Kaitkan induk kontainer langsung ke objek self.table
        w = QWidget(self.table)
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_e = QPushButton("✏️ Edit", parent=w)
        btn_e.setFixedHeight(32)
        btn_e.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_e.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {SECONDARY}; color: white; border: none;
                border-radius: 6px; padding: 0 14px; font-size: 12px; font-weight: 600; 
            }}
            QPushButton:hover {{ background-color: #1976D2; }}
        """)
        btn_e.clicked.connect(lambda _, obj=p: self._on_edit(obj))

        btn_d = QPushButton("🗑️ Hapus", parent=w)
        btn_d.setFixedHeight(32)
        btn_d.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_d.setStyleSheet(f"""
            QPushButton {{ 
                background-color: transparent; color: {DANGER};
                border: 1px solid {DANGER}; border-radius: 6px;
                padding: 0 14px; font-size: 12px; font-weight: 600; 
            }}
            QPushButton:hover {{ background-color: {DANGER}1A; }}
        """)
        btn_d.clicked.connect(lambda _, obj=p: self._on_delete(obj))

        lay.addWidget(btn_e)
        lay.addWidget(btn_d)
        return w

    def _on_add(self):
        dlg = PaketDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = PaketController.create(**d)
            self._msg(ok, msg)
            if ok:
                self.refresh_table()

    def _on_edit(self, p):
        dlg = PaketDialog(self, paket=p)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg = PaketController.update(p.id, **d)
            self._msg(ok, msg)
            if ok:
                self.refresh_table()

    def _on_delete(self, p):
        reply = QMessageBox.question(
            self, "Hapus Paket",
            f"Yakin hapus paket <b>{p.nama_paket}</b>?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = PaketController.delete(p.id)
            self._msg(ok, msg)
            if ok:
                self.refresh_table()

    def _msg(self, ok, msg):
        mb = QMessageBox(self)
        mb.setText(msg)
        mb.setIcon(QMessageBox.Icon.Information if ok else QMessageBox.Icon.Warning)
        mb.setStyleSheet("QMessageBox { background-color: #1B2A3B; } QLabel { color: #F0F4F8; }")
        mb.exec()