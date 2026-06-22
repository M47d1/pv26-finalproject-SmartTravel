"""
SmartTravel - Controllers
Logika bisnis sebagai jembatan antara View dan Model.
"""

from __future__ import annotations
from typing import Optional, List, Tuple
from models.models import (
    UserModel, PelangganModel, PaketWisataModel, TransaksiModel,
    User, Pelanggan, PaketWisata, Transaksi,
)


# ═══════════════════════════════════════════════════════════════════════════
# AuthController
# ═══════════════════════════════════════════════════════════════════════════

class AuthController:
    _current_user: Optional[User] = None

    @classmethod
    def login(cls, username: str, password: str) -> Tuple[bool, str]:
        user = UserModel.authenticate(username, password)
        if user:
            cls._current_user = user
            return True, f"Selamat datang, {user.username}!"
        return False, "Username atau password salah."

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def get_current_user(cls) -> Optional[User]:
        return cls._current_user

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._current_user is not None


# ═══════════════════════════════════════════════════════════════════════════
# PelangganController
# ═══════════════════════════════════════════════════════════════════════════

class PelangganController:
    @staticmethod
    def get_all() -> List[Pelanggan]:
        return PelangganModel.get_all()

    @staticmethod
    def search(keyword: str) -> List[Pelanggan]:
        if not keyword.strip():
            return PelangganModel.get_all()
        return PelangganModel.search(keyword)

    @staticmethod
    def get_sorted(sort_by: str = "terbaru") -> List[Pelanggan]:
        """Dapatkan semua pelanggan dengan sorting."""
        return PelangganModel.get_sorted(sort_by)

    @staticmethod
    def search_sorted(keyword: str, sort_by: str = "terbaru") -> List[Pelanggan]:
        """Cari dengan sorting yang sesuai."""
        if not keyword.strip():
            return PelangganModel.get_sorted(sort_by)
        return PelangganModel.search_sorted(keyword, sort_by)

    @staticmethod
    def create(nama: str, email: str, telepon: str, alamat: str) -> Tuple[bool, str]:
        if not nama.strip():
            return False, "Nama pelanggan tidak boleh kosong."
        try:
            PelangganModel.create(nama.strip(), email.strip(), telepon.strip(), alamat.strip())
            return True, "Pelanggan berhasil ditambahkan."
        except Exception as e:
            if "UNIQUE" in str(e):
                return False, "Email sudah terdaftar."
            return False, f"Gagal: {e}"

    @staticmethod
    def update(pid: int, nama: str, email: str,
            telepon: str, alamat: str) -> Tuple[bool, str]:
        if not nama.strip():
            return False, "Nama pelanggan tidak boleh kosong."
        try:
            PelangganModel.update(pid, nama.strip(), email.strip(),
                                telepon.strip(), alamat.strip())
            return True, "Data pelanggan berhasil diperbarui."
        except Exception as e:
            return False, f"Gagal: {e}"

    @staticmethod
    def delete(pid: int) -> Tuple[bool, str]:
        try:
            PelangganModel.delete(pid)
            return True, "Pelanggan berhasil dihapus."
        except Exception as e:
            if "FOREIGN KEY" in str(e):
                return False, "Tidak bisa hapus: pelanggan memiliki transaksi aktif."
            return False, f"Gagal: {e}"


# ═══════════════════════════════════════════════════════════════════════════
# PaketController
# ═══════════════════════════════════════════════════════════════════════════

class PaketController:
    @staticmethod
    def get_all() -> List[PaketWisata]:
        return PaketWisataModel.get_all()

    @staticmethod
    def get_available() -> List[PaketWisata]:
        return PaketWisataModel.get_available()

    @staticmethod
    def search(keyword: str) -> List[PaketWisata]:
        if not keyword.strip():
            return PaketWisataModel.get_all()
        return PaketWisataModel.search(keyword)

    @staticmethod
    def filter_by_status(tersedia: int) -> List[PaketWisata]:
        return PaketWisataModel.filter_by_status(tersedia)

    @staticmethod
    def create(nama_paket: str, destinasi: str, durasi_hari: int,
               harga: float, deskripsi: str,
               tersedia: int = 1) -> Tuple[bool, str]:
        if not nama_paket.strip() or not destinasi.strip():
            return False, "Nama paket dan destinasi tidak boleh kosong."
        if harga <= 0:
            return False, "Harga harus lebih dari 0."
        try:
            PaketWisataModel.create(nama_paket, destinasi, durasi_hari,
                                    harga, deskripsi, tersedia)
            return True, "Paket wisata berhasil ditambahkan."
        except Exception as e:
            return False, f"Gagal: {e}"

    @staticmethod
    def update(pid: int, nama_paket: str, destinasi: str, durasi_hari: int,
               harga: float, deskripsi: str,
               tersedia: int) -> Tuple[bool, str]:
        if not nama_paket.strip() or not destinasi.strip():
            return False, "Nama paket dan destinasi tidak boleh kosong."
        try:
            PaketWisataModel.update(pid, nama_paket, destinasi, durasi_hari,
                                    harga, deskripsi, tersedia)
            return True, "Paket wisata berhasil diperbarui."
        except Exception as e:
            return False, f"Gagal: {e}"

    @staticmethod
    def delete(pid: int) -> Tuple[bool, str]:
        try:
            PaketWisataModel.delete(pid)
            return True, "Paket wisata berhasil dihapus."
        except Exception as e:
            if "FOREIGN KEY" in str(e):
                return False, "Tidak bisa hapus: paket digunakan dalam transaksi."
            return False, f"Gagal: {e}"


# ═══════════════════════════════════════════════════════════════════════════
# TransaksiController
# ═══════════════════════════════════════════════════════════════════════════

class TransaksiController:
    @staticmethod
    def get_all() -> List[Transaksi]:
        return TransaksiModel.get_all()

    @staticmethod
    def search(keyword: str) -> List[Transaksi]:
        if not keyword.strip():
            return TransaksiModel.get_all()
        return TransaksiModel.search(keyword)

    @staticmethod
    def filter_by_status(status: str) -> List[Transaksi]:
        if not status or status == "Semua":
            return TransaksiModel.get_all()
        return TransaksiModel.filter_by_status(status)

    @staticmethod
    def create(pelanggan_id: int, paket_id: int, tanggal_berangkat: str,
               jumlah_orang: int, catatan: str = "") -> Tuple[bool, str, Optional[Transaksi]]:
        if jumlah_orang < 1:
            return False, "Jumlah orang minimal 1.", None
        paket = PaketWisataModel.get_by_id(paket_id)
        if not paket:
            return False, "Paket tidak ditemukan.", None
        total = paket.harga * jumlah_orang
        try:
            trx = TransaksiModel.create(
                pelanggan_id, paket_id, tanggal_berangkat,
                jumlah_orang, total, catatan,
            )
            return True, f"Reservasi berhasil! Invoice: {trx.kode_invoice}", trx
        except Exception as e:
            return False, f"Gagal: {e}", None

    @staticmethod
    def update_status(tid: int, status: str) -> Tuple[bool, str]:
        valid = {"Pending", "Confirmed", "Cancelled"}
        if status not in valid:
            return False, f"Status tidak valid. Pilih: {', '.join(valid)}"
        TransaksiModel.update_status(tid, status)
        return True, f"Status diperbarui menjadi {status}."

    @staticmethod
    def delete(tid: int) -> Tuple[bool, str]:
        try:
            TransaksiModel.delete(tid)
            return True, "Transaksi berhasil dihapus."
        except Exception as e:
            return False, f"Gagal: {e}"

    @staticmethod
    def get_stats() -> dict:
        return TransaksiModel.get_stats()

    @staticmethod
    def generate_invoice_pdf(tid: int) -> Tuple[bool, str]:
        from utils.pdf_generator import generate_invoice
        from models.models import PelangganModel, PaketWisataModel
        trx = TransaksiModel.get_by_id(tid)
        if not trx:
            return False, "Transaksi tidak ditemukan."
        pelanggan = PelangganModel.get_by_id(trx.pelanggan_id)
        paket = PaketWisataModel.get_by_id(trx.paket_id)
        try:
            path = generate_invoice(trx, pelanggan, paket)
            return True, path
        except Exception as e:
            return False, f"Gagal membuat PDF: {e}"
