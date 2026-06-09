"""
SmartTravel - Transaksi View
Manajemen reservasi + cetak invoice PDF.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QMessageBox, QComboBox, QSpinBox,
    QDateEdit, QTextEdit, QAbstractItemView, QFrame,
)
from PySide6.QtCore import Qt, QDate
from utils.theme import SECONDARY, ACCENT, DANGER, SUCCESS, WARNING, BG_MEDIUM, BG_CARD, TEXT_MUTED
from controllers.controllers import TransaksiController, PelangganController, PaketController


class ReservasiDialog(QDialog):
    """Dialog untuk membuat reservasi baru."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buat Reservasi Baru")
        self.setMinimumWidth(460)
        self.setStyleSheet("""
            QDialog { background-color: #1B2A3B; }
            QLabel { color: #F0F4F8; font-size: 12px; }
            QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {
                background-color: #162435; border: 1px solid #1E3A5F;
                border-radius: 6px; padding: 8px 12px; color: #F0F4F8; font-size: 13px;
            }
            QComboBox::drop-down { border: none; padding-right: 8px; }
            QComboBox:focus, QDateEdit:focus, QSpinBox:focus { border: 1px solid #1565C0; }
            QPushButton {
                background-color: #1565C0; color: white; border: none;
                border-radius: 6px; padding: 9px 22px; font-weight: 600;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton#btnCancel {
                background-color: transparent; color: #8EADC1; border: 1px solid #1E3A5F;
            }
        """)
        self._paket_map = {}   # display_name -> paket obj
        self._cust_map  = {}   # display_name -> pelanggan obj
        self._build_ui()
        self._load_combos()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        title = QLabel("🗓️  Buat Reservasi Baru", parent=self)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #F0F4F8;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo_pelanggan = QComboBox()
        self.combo_paket     = QComboBox()
        self.combo_paket.currentTextChanged.connect(self._update_price_preview)

        self.inp_tgl_berangkat = QDateEdit(QDate.currentDate().addDays(7))
        self.inp_tgl_berangkat.setCalendarPopup(True)
        self.inp_tgl_berangkat.setDisplayFormat("dd MMMM yyyy")

        self.inp_jumlah = QSpinBox()
        self.inp_jumlah.setRange(1, 100)
        self.inp_jumlah.setSuffix(" orang")
        self.inp_jumlah.valueChanged.connect(self._update_price_preview)

        self.inp_catatan = QTextEdit()
        self.inp_catatan.setPlaceholderText("Catatan khusus (opsional)...")
        self.inp_catatan.setMaximumHeight(70)

        # Price preview
        self.lbl_total = QLabel("Total: Rp 0")
        self.lbl_total.setStyleSheet("""
            font-size: 18px; font-weight: 700; color: #FF6B35;
            background-color: #162435; border-radius: 8px; padding: 10px 16px;
        """)

        form.addRow("Pelanggan *",         self.combo_pelanggan)
        form.addRow("Paket Wisata *",      self.combo_paket)
        form.addRow("Tgl Berangkat",       self.inp_tgl_berangkat)
        form.addRow("Jumlah Orang",        self.inp_jumlah)
        form.addRow("Catatan",             self.inp_catatan)
        form.addRow("",                    self.lbl_total)
        lay.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_c = QPushButton("Batal", parent=self)
        btn_c.setObjectName("btnCancel")
        btn_c.clicked.connect(self.reject)
        btn_s = QPushButton("Buat Reservasi  →", parent=self)
        btn_s.clicked.connect(self._on_save)
        btn_row.addWidget(btn_c)
        btn_row.addWidget(btn_s)
        lay.addLayout(btn_row)

    def _load_combos(self):
        pelanggan_list = PelangganController.get_all()
        paket_list     = PaketController.get_available()

        for p in pelanggan_list:
            key = f"{p.nama} ({p.telepon or p.email or '—'})"
            self._cust_map[key] = p
            self.combo_pelanggan.addItem(key)

        for pk in paket_list:
            key = f"{pk.nama_paket} – {pk.destinasi}"
            self._paket_map[key] = pk
            self.combo_paket.addItem(key)

        self._update_price_preview()

    def _update_price_preview(self):
        key = self.combo_paket.currentText()
        paket = self._paket_map.get(key)
        if paket:
            total = paket.harga * self.inp_jumlah.value()
            self.lbl_total.setText(f"Total: Rp {total:,.0f}")
        else:
            self.lbl_total.setText("Total: Rp 0")

    def _on_save(self):
        cust_key  = self.combo_pelanggan.currentText()
        paket_key = self.combo_paket.currentText()
        if not cust_key or not paket_key:
            return
        self.result_data = {
            "pelanggan_id":      self._cust_map[cust_key].id,
            "paket_id":          self._paket_map[paket_key].id,
            "tanggal_berangkat": self.inp_tgl_berangkat.date().toString("yyyy-MM-dd"),
            "jumlah_orang":      self.inp_jumlah.value(),
            "catatan":           self.inp_catatan.toPlainText().strip(),
        }
        self.accept()

    def get_data(self):
        return self.result_data


class TransaksiView(QWidget):
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
        title = QLabel("Reservasi & Transaksi", parent=self)
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F0F4F8;")
        hdr.addWidget(title)
        hdr.addStretch()

        btn_add = QPushButton("＋  Buat Reservasi", parent=self)
        btn_add.setStyleSheet(f"""
            QPushButton {{ background-color: {ACCENT}; color: white; border: none;
                border-radius: 6px; padding: 9px 18px; font-weight: 600; }}
            QPushButton:hover {{ background-color: #E55A25; }}
        """)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._on_add)
        hdr.addWidget(btn_add)
        main.addLayout(hdr)

        # Table
        self.table = QTableWidget(parent=self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Invoice", "Pelanggan", "Paket", "Destinasi",
            "Berangkat", "Pax", "Total", "Status", "Aksi"
        ])
        
        # 🔥 PERBAIKAN 1: Pengaturan ukuran kolom secara eksplisit & urut (Bebas teks terpotong '...')
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Invoice (Bisa di-resize manual)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Pelanggan
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)      # Paket
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)      # Destinasi
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Berangkat
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)        # Pax
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)  # Total
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)        # Status
        hh.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)        # Aksi
        
        # Alokasi lebar absolut piksel agar space tombol lega di macOS
        self.table.setColumnWidth(0, 110) # Invoice lebar ideal
        self.table.setColumnWidth(4, 100) # Tanggal berangkat
        self.table.setColumnWidth(5, 50)  # Pax kecil saja
        self.table.setColumnWidth(6, 120) # Total Rupiah
        self.table.setColumnWidth(7, 90)  # Status badge
        self.table.setColumnWidth(8, 270) # Ditambah ke 270px agar 4 tombol muat sejajar tanpa tumpang tindih
        
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ background-color: {BG_MEDIUM}; border: none; border-radius: 10px;
                alternate-background-color: {BG_CARD}; }}
            QTableWidget::item {{ padding: 8px 10px; }}
            QTableWidget::item:selected {{ background-color: #1565C055; color: #F0F4F8; }}
            QHeaderView::section {{ background-color: #0A2342; color: #4A6B80; padding: 10px 12px;
                border: none; font-size: 10px; font-weight: 700; letter-spacing: 1px; }}
        """)
        main.addWidget(self.table)

    def refresh_table(self):
        data = TransaksiController.get_all()
        self.table.setRowCount(0)
        for ri, t in enumerate(data):
            self.table.insertRow(ri)
            cells = [
                t.kode_invoice, t.nama_pelanggan, t.nama_paket,
                t.destinasi, t.tanggal_berangkat or "-",
                str(t.jumlah_orang), f"Rp {t.total_harga:,.0f}",
            ]
            for ci, val in enumerate(cells):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(ri, ci, item)

            # Status badge
            st_item = QTableWidgetItem(t.status)
            st_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            if t.status == "Confirmed":
                st_item.setForeground(Qt.GlobalColor.green)
            elif t.status == "Pending":
                st_item.setForeground(Qt.GlobalColor.yellow)
            else:
                st_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(ri, 7, st_item)

            # 🔥 PERBAIKAN 2: Gunakan widget aksi kustom dengan siklus penanganan memori Mac
            action_widget = self._make_btns(t)
            self.table.setCellWidget(ri, 8, action_widget)
            
            # 🔥 PERBAIKAN 3: Berikan tinggi baris seragam agar tombol vertikal tidak terhimpit
            self.table.setRowHeight(ri, 52)

    def _make_btns(self, t) -> QWidget:
        # 🔥 PERBAIKAN 4: Kaitkan objek penampung C++ langsung ke self.table sebagai parent
        w = QWidget(self.table)
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(6, 0, 6, 0)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def create_push_btn(label, color, slot):
            b = QPushButton(label, parent=w)
            b.setFixedHeight(30)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{ background-color: {color}; color: white; border: none;
                    border-radius: 5px; padding: 0 8px; font-size: 11px; font-weight: 600; }}
                QPushButton:hover {{ opacity: 0.85; }}
                QPushButton:disabled {{ background-color: #2C3E50; color: #7F8C8D; }}
            """)
            b.clicked.connect(slot)
            return b

        btn_confirm = create_push_btn("✓ Conf", SUCCESS, lambda _, obj=t: self._on_status(obj, "Confirmed"))
        btn_cancel  = create_push_btn("✗ Cancel", DANGER, lambda _, obj=t: self._on_status(obj, "Cancelled"))
        btn_pdf     = create_push_btn("🧾 PDF", SECONDARY, lambda _, obj=t: self._on_pdf(obj))
        btn_del     = create_push_btn("🗑", "#4A6B80", lambda _, obj=t: self._on_delete(obj))

        # Atur disabilitas tombol sesuai status
        if t.status == "Confirmed":
            btn_confirm.setEnabled(False)
        elif t.status == "Cancelled":
            btn_cancel.setEnabled(False)

        lay.addWidget(btn_confirm)
        lay.addWidget(btn_cancel)
        lay.addWidget(btn_pdf)
        lay.addWidget(btn_del)
        return w

    def _on_add(self):
        dlg = ReservasiDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            ok, msg, trx = TransaksiController.create(**d)
            self._msg(ok, msg)
            if ok:
                self.refresh_table()
                reply = QMessageBox.question(
                    self, "Cetak Invoice",
                    f"Reservasi berhasil!<br>Cetak invoice PDF sekarang?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes and trx:
                    self._on_pdf(trx)

    def _on_status(self, t, status: str):
        ok, msg = TransaksiController.update_status(t.id, status)
        self._msg(ok, msg)
        if ok:
            self.refresh_table()

    def _on_pdf(self, t):
        ok, result = TransaksiController.generate_invoice_pdf(t.id)
        if ok:
            mb = QMessageBox(self)
            mb.setWindowTitle("Invoice Dibuat")
            mb.setText(f"✅  Invoice PDF berhasil dibuat!\n\n📄  {result}")
            mb.setStyleSheet("QMessageBox { background-color: #1B2A3B; } QLabel { color: #F0F4F8; }")
            mb.setStandardButtons(QMessageBox.StandardButton.Ok)
            btn_open = mb.addButton("Buka File", QMessageBox.ButtonRole.ActionRole)
            mb.exec()
            if mb.clickedButton() == btn_open:
                os.startfile(result) if os.name == "nt" else os.system(f'xdg-open "{result}"')
        else:
            self._msg(False, result)

    def _on_delete(self, t):
        reply = QMessageBox.question(
            self, "Hapus Transaksi",
            f"Hapus transaksi <b>{t.kode_invoice}</b>?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = TransaksiController.delete(t.id)
            self._msg(ok, msg)
            if ok:
                self.refresh_table()

    def _msg(self, ok, msg):
        mb = QMessageBox(self)
        mb.setText(msg)
        mb.setIcon(QMessageBox.Icon.Information if ok else QMessageBox.Icon.Warning)
        mb.setStyleSheet("QMessageBox { background-color: #1B2A3B; } QLabel { color: #F0F4F8; }")
        mb.exec()