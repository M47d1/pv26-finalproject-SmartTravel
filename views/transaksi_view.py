"""
SmartTravel - Transaksi View
Manajemen reservasi + cetak invoice PDF.
"""

import os
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QMessageBox, QComboBox, QSpinBox,
    QDateEdit, QTextEdit, QAbstractItemView, QFrame,
)
from PySide6.QtCore import Qt, QDate
from utils.theme import SECONDARY, ACCENT, DANGER, SUCCESS, WARNING, BG_MEDIUM, BG_CARD, TEXT_MUTED, BG_INPUT, BORDER, TEXT_PRIMARY, TEXT_SECONDARY
from controllers.controllers import TransaksiController, PelangganController, PaketController
from utils.csv_exporter import export_transaksi_to_csv


class ReservasiDialog(QDialog):
    """Dialog untuk membuat reservasi baru."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buat Reservasi Baru")
        self.setMinimumWidth(460)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_MEDIUM}; }}
            QLabel {{ color: {TEXT_PRIMARY}; font-size: 12px; }}
            QLineEdit, QComboBox, QSpinBox, QDateEdit, QTextEdit {{
                background-color: #162435; border: 1px solid {BORDER};
                border-radius: 6px; padding: 8px 12px; color: {TEXT_PRIMARY}; font-size: 13px;
            }}
            QComboBox::drop-down {{ border: none; padding-right: 8px; }}
            QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{ border: 1px solid {SECONDARY}; }}
            QPushButton {{
                background-color: {SECONDARY}; color: white; border: none;
                border-radius: 6px; padding: 9px 22px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #1976D2; }}
            QPushButton#btnCancel {{
                background-color: transparent; color: {TEXT_SECONDARY}; border: 1px solid {BORDER};
            }}
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

        is_valid, error_msg = self._validate_data()
        if not is_valid:
            QMessageBox.warning(self, "Validasi Gagal", error_msg)
            return

        if not cust_key or not paket_key:
            QMessageBox.warning(self, "Validasi Gagal", "Pelanggan dan Paket tidak boleh kosong.")
            return

        self.result_data = {
            "pelanggan_id":      self._cust_map[cust_key].id,
            "paket_id":          self._paket_map[paket_key].id,
            "tanggal_berangkat": self.inp_tgl_berangkat.date().toString("yyyy-MM-dd"),
            "jumlah_orang":      self.inp_jumlah.value(),
            "catatan":           self.inp_catatan.toPlainText().strip(),
        }
        self.accept()

    def _validate_data(self) -> tuple:
        tgl_berangkat_qdate = self.inp_tgl_berangkat.date()
        tgl_berangkat = date(tgl_berangkat_qdate.year(), tgl_berangkat_qdate.month(), tgl_berangkat_qdate.day())

        if tgl_berangkat < date.today():
            return False, "Tanggal berangkat harus >= hari ini."

        jumlah_orang = self.inp_jumlah.value()
        if jumlah_orang < 1 or jumlah_orang > 999:
            return False, "Jumlah orang harus antara 1-999."

        return True, ""

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

        # ── Search & Filter ──────────────────────────────────────────────────
        search_row = QHBoxLayout()
        self.search_input = QLineEdit(parent=self)
        self.search_input.setPlaceholderText("🔍  Cari invoice, pelanggan, paket, atau destinasi...")
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

        self.combo_status = QComboBox()
        self.combo_status.addItems(["Semua", "Pending", "Confirmed", "Cancelled"])
        self.combo_status.setStyleSheet(f"""
            QComboBox {{
                background-color: #162435;
                border: 1px solid #1E3A5F;
                border-radius: 6px;
                padding: 8px 12px;
                color: #F0F4F8;
                font-size: 12px;
            }}
            QComboBox:focus {{ border: 1px solid {SECONDARY}; }}
            QComboBox::drop-down {{ border: none; padding-right: 8px; }}
        """)
        self.combo_status.currentTextChanged.connect(self._on_status_filter)
        search_row.addWidget(self.combo_status)

        self.lbl_count = QLabel("0 transaksi", parent=self)
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; min-width: 120px;")
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        search_row.addWidget(self.lbl_count)
        main.addLayout(search_row)

        # ── Date Range Filter & Export ───────────────────────────────────────
        filter_row = QHBoxLayout()

        lbl_dari = QLabel("Dari:", parent=self)
        lbl_dari.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        filter_row.addWidget(lbl_dari)

        self.date_from = QDateEdit(parent=self)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setStyleSheet(f"""
            QDateEdit {{
                background-color: #162435;
                border: 1px solid #1E3A5F;
                border-radius: 6px;
                padding: 6px 10px;
                color: #F0F4F8;
                font-size: 11px;
            }}
            QDateEdit:focus {{ border: 1px solid {SECONDARY}; }}
            QDateEdit::drop-down {{ border: none; padding-right: 6px; }}
        """)
        self.date_from.dateChanged.connect(self._on_date_filter_changed)
        filter_row.addWidget(self.date_from)

        lbl_sampai = QLabel("Sampai:", parent=self)
        lbl_sampai.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: 600;")
        filter_row.addWidget(lbl_sampai)

        self.date_to = QDateEdit(parent=self)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setStyleSheet(f"""
            QDateEdit {{
                background-color: #162435;
                border: 1px solid #1E3A5F;
                border-radius: 6px;
                padding: 6px 10px;
                color: #F0F4F8;
                font-size: 11px;
            }}
            QDateEdit:focus {{ border: 1px solid {SECONDARY}; }}
            QDateEdit::drop-down {{ border: none; padding-right: 6px; }}
        """)
        self.date_to.dateChanged.connect(self._on_date_filter_changed)
        filter_row.addWidget(self.date_to)

        filter_row.addStretch()

        btn_csv = QPushButton("📊  Cetak Laporan CSV", parent=self)
        btn_csv.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS};
                color: #0D1B2A;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: #27AE60; }}
        """)
        btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_csv.clicked.connect(self._on_export_csv)
        filter_row.addWidget(btn_csv)

        main.addLayout(filter_row)

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

    def refresh_table(self, keyword: str = "", status: str = "Semua"):
        if status == "Semua":
            data = TransaksiController.search(keyword) if keyword else TransaksiController.get_all()
        else:
            data = TransaksiController.filter_by_status(status)
            if keyword:
                data = [t for t in data if keyword.lower() in t.kode_invoice.lower() or keyword.lower() in t.nama_pelanggan.lower() or keyword.lower() in t.nama_paket.lower() or keyword.lower() in t.destinasi.lower()]

        self.table.setRowCount(0)
        self.lbl_count.setText(f"{len(data)} transaksi")
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

    def _on_search(self, text: str):
        self.refresh_table(text, self.combo_status.currentText())

    def _on_status_filter(self, status: str):
        self.refresh_table(self.search_input.text(), status)

    def _on_date_filter_changed(self, _):
        """Refresh tabel ketika date range berubah."""
        self.refresh_table(self.search_input.text(), self.combo_status.currentText())

    def _on_export_csv(self):
        """Export data transaksi yang terfilter ke CSV."""
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        status = self.combo_status.currentText()

        # Filter data berdasarkan date range dan status
        all_data = TransaksiController.get_all()

        filtered_data = []
        for trx in all_data:
            trx_date = trx.tanggal_pesan[:10] if trx.tanggal_pesan else ""

            # Cek range tanggal
            if trx_date < date_from or trx_date > date_to:
                continue

            # Cek status
            if status != "Semua" and trx.status != status:
                continue

            # Cek keyword search jika ada
            keyword = self.search_input.text().strip()
            if keyword:
                if not (keyword.lower() in trx.kode_invoice.lower() or
                        keyword.lower() in trx.nama_pelanggan.lower() or
                        keyword.lower() in trx.nama_paket.lower() or
                        keyword.lower() in trx.destinasi.lower()):
                    continue

            filtered_data.append(trx)

        if not filtered_data:
            QMessageBox.warning(
                self,
                "Tidak Ada Data",
                "Tidak ada transaksi yang sesuai dengan filter yang dipilih.",
            )
            return

        try:
            filepath = export_transaksi_to_csv(filtered_data)
            QMessageBox.information(
                self,
                "Laporan CSV Berhasil",
                f"📊  Laporan CSV berhasil dibuat!\n\n📁  {filepath}\n\n"
                f"Total: {len(filtered_data)} transaksi",
            )
        except Exception as e:
            QMessageBox.warning(self, "Gagal Export CSV", f"Error: {str(e)}")

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