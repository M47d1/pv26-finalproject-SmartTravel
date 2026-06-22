"""
SmartTravel - Models
Data-access layer untuk semua entitas (User, Pelanggan, Paket, Transaksi).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from config.database import get_connection


# ═══════════════════════════════════════════════════════════════════════════
# Dataclasses
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class User:
    id: int
    username: str
    role: str


@dataclass
class Pelanggan:
    id: int
    nama: str
    email: str
    telepon: str
    alamat: str
    created_at: str


@dataclass
class PaketWisata:
    id: int
    nama_paket: str
    destinasi: str
    durasi_hari: int
    harga: float
    deskripsi: str
    tersedia: int
    created_at: str


@dataclass
class Transaksi:
    id: int
    kode_invoice: str
    pelanggan_id: int
    paket_id: int
    tanggal_pesan: str
    tanggal_berangkat: str
    jumlah_orang: int
    total_harga: float
    status: str
    catatan: str
    created_at: str
    # join fields (opsional)
    nama_pelanggan: str = ""
    nama_paket: str = ""
    destinasi: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# UserModel
# ═══════════════════════════════════════════════════════════════════════════

class UserModel:
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        conn = get_connection()
        row = conn.execute(
            "SELECT id, username, role FROM users WHERE username=? AND password=?",
            (username, password),
        ).fetchone()
        conn.close()
        if row:
            return User(id=row["id"], username=row["username"], role=row["role"])
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PelangganModel
# ═══════════════════════════════════════════════════════════════════════════

class PelangganModel:
    @staticmethod
    def get_all() -> List[Pelanggan]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM pelanggan ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [Pelanggan(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(pid: int) -> Optional[Pelanggan]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM pelanggan WHERE id=?", (pid,)).fetchone()
        conn.close()
        return Pelanggan(**dict(row)) if row else None

    @staticmethod
    def create(nama: str, email: str, telepon: str, alamat: str) -> int:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO pelanggan (nama, email, telepon, alamat) VALUES (?,?,?,?)",
            (nama, email, telepon, alamat),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(pid: int, nama: str, email: str, telepon: str, alamat: str):
        conn = get_connection()
        conn.execute(
            "UPDATE pelanggan SET nama=?, email=?, telepon=?, alamat=? WHERE id=?",
            (nama, email, telepon, alamat, pid),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(pid: int):
        conn = get_connection()
        conn.execute("DELETE FROM pelanggan WHERE id=?", (pid,))
        conn.commit()
        conn.close()

    @staticmethod
    def search(keyword: str) -> List[Pelanggan]:
        conn = get_connection()
        like = f"%{keyword}%"
        rows = conn.execute(
            "SELECT * FROM pelanggan WHERE nama LIKE ? OR email LIKE ? OR telepon LIKE ?",
            (like, like, like),
        ).fetchall()
        conn.close()
        return [Pelanggan(**dict(r)) for r in rows]

    @staticmethod
    def get_sorted(sort_by: str = "terbaru") -> List[Pelanggan]:
        """Dapatkan semua pelanggan dengan sorting yang sesuai.

        Args:
            sort_by: "nama_az", "nama_za", "terbaru"
        """
        conn = get_connection()
        if sort_by == "nama_az":
            query = "SELECT * FROM pelanggan ORDER BY nama ASC"
        elif sort_by == "nama_za":
            query = "SELECT * FROM pelanggan ORDER BY nama DESC"
        else:  # terbaru
            query = "SELECT * FROM pelanggan ORDER BY created_at DESC"

        rows = conn.execute(query).fetchall()
        conn.close()
        return [Pelanggan(**dict(r)) for r in rows]

    @staticmethod
    def search_sorted(keyword: str, sort_by: str = "terbaru") -> List[Pelanggan]:
        """Cari pelanggan dengan sorting yang sesuai."""
        conn = get_connection()
        like = f"%{keyword}%"

        if sort_by == "nama_az":
            query = "SELECT * FROM pelanggan WHERE nama LIKE ? OR email LIKE ? OR telepon LIKE ? ORDER BY nama ASC"
        elif sort_by == "nama_za":
            query = "SELECT * FROM pelanggan WHERE nama LIKE ? OR email LIKE ? OR telepon LIKE ? ORDER BY nama DESC"
        else:  # terbaru
            query = "SELECT * FROM pelanggan WHERE nama LIKE ? OR email LIKE ? OR telepon LIKE ? ORDER BY created_at DESC"

        rows = conn.execute(query, (like, like, like)).fetchall()
        conn.close()
        return [Pelanggan(**dict(r)) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════
# PaketWisataModel
# ═══════════════════════════════════════════════════════════════════════════

class PaketWisataModel:
    @staticmethod
    def get_all() -> List[PaketWisata]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM paket_wisata ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [PaketWisata(**dict(r)) for r in rows]

    @staticmethod
    def get_available() -> List[PaketWisata]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM paket_wisata WHERE tersedia=1 ORDER BY nama_paket"
        ).fetchall()
        conn.close()
        return [PaketWisata(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(pid: int) -> Optional[PaketWisata]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM paket_wisata WHERE id=?", (pid,)).fetchone()
        conn.close()
        return PaketWisata(**dict(row)) if row else None

    @staticmethod
    def create(nama_paket: str, destinasi: str, durasi_hari: int,
               harga: float, deskripsi: str, tersedia: int = 1) -> int:
        conn = get_connection()
        cur = conn.execute(
            """INSERT INTO paket_wisata
               (nama_paket, destinasi, durasi_hari, harga, deskripsi, tersedia)
               VALUES (?,?,?,?,?,?)""",
            (nama_paket, destinasi, durasi_hari, harga, deskripsi, tersedia),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def update(pid: int, nama_paket: str, destinasi: str, durasi_hari: int,
               harga: float, deskripsi: str, tersedia: int):
        conn = get_connection()
        conn.execute(
            """UPDATE paket_wisata
               SET nama_paket=?, destinasi=?, durasi_hari=?, harga=?, deskripsi=?, tersedia=?
               WHERE id=?""",
            (nama_paket, destinasi, durasi_hari, harga, deskripsi, tersedia, pid),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(pid: int):
        conn = get_connection()
        conn.execute("DELETE FROM paket_wisata WHERE id=?", (pid,))
        conn.commit()
        conn.close()

    @staticmethod
    def search(keyword: str) -> List[PaketWisata]:
        conn = get_connection()
        like = f"%{keyword}%"
        rows = conn.execute(
            "SELECT * FROM paket_wisata WHERE nama_paket LIKE ? OR destinasi LIKE ? ORDER BY created_at DESC",
            (like, like),
        ).fetchall()
        conn.close()
        return [PaketWisata(**dict(r)) for r in rows]

    @staticmethod
    def filter_by_status(tersedia: int) -> List[PaketWisata]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM paket_wisata WHERE tersedia = ? ORDER BY created_at DESC",
            (tersedia,),
        ).fetchall()
        conn.close()
        return [PaketWisata(**dict(r)) for r in rows]


# ═══════════════════════════════════════════════════════════════════════════
# TransaksiModel
# ═══════════════════════════════════════════════════════════════════════════

class TransaksiModel:
    @staticmethod
    def _generate_invoice_code() -> str:
        conn = get_connection()
        count = conn.execute("SELECT COUNT(*) FROM transaksi").fetchone()[0]
        conn.close()
        ts = datetime.now().strftime("%y%m%d")
        return f"INV-{ts}-{count+1:04d}"

    @staticmethod
    def get_all() -> List[Transaksi]:
        conn = get_connection()
        rows = conn.execute("""
            SELECT t.*, p.nama AS nama_pelanggan,
                   pw.nama_paket, pw.destinasi
            FROM transaksi t
            JOIN pelanggan p  ON t.pelanggan_id = p.id
            JOIN paket_wisata pw ON t.paket_id  = pw.id
            ORDER BY t.created_at DESC
        """).fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            trx = Transaksi(
                id=d["id"], kode_invoice=d["kode_invoice"],
                pelanggan_id=d["pelanggan_id"], paket_id=d["paket_id"],
                tanggal_pesan=d["tanggal_pesan"],
                tanggal_berangkat=d["tanggal_berangkat"],
                jumlah_orang=d["jumlah_orang"], total_harga=d["total_harga"],
                status=d["status"], catatan=d["catatan"],
                created_at=d["created_at"],
                nama_pelanggan=d["nama_pelanggan"],
                nama_paket=d["nama_paket"], destinasi=d["destinasi"],
            )
            result.append(trx)
        return result

    @staticmethod
    def get_by_id(tid: int) -> Optional[Transaksi]:
        conn = get_connection()
        r = conn.execute("""
            SELECT t.*, p.nama AS nama_pelanggan,
                   pw.nama_paket, pw.destinasi
            FROM transaksi t
            JOIN pelanggan p  ON t.pelanggan_id = p.id
            JOIN paket_wisata pw ON t.paket_id  = pw.id
            WHERE t.id=?
        """, (tid,)).fetchone()
        conn.close()
        if not r:
            return None
        d = dict(r)
        return Transaksi(
            id=d["id"], kode_invoice=d["kode_invoice"],
            pelanggan_id=d["pelanggan_id"], paket_id=d["paket_id"],
            tanggal_pesan=d["tanggal_pesan"],
            tanggal_berangkat=d["tanggal_berangkat"],
            jumlah_orang=d["jumlah_orang"], total_harga=d["total_harga"],
            status=d["status"], catatan=d["catatan"],
            created_at=d["created_at"],
            nama_pelanggan=d["nama_pelanggan"],
            nama_paket=d["nama_paket"], destinasi=d["destinasi"],
        )

    @staticmethod
    def create(pelanggan_id: int, paket_id: int, tanggal_berangkat: str,
               jumlah_orang: int, total_harga: float,
               catatan: str = "") -> Transaksi:
        kode = TransaksiModel._generate_invoice_code()
        conn = get_connection()
        cur = conn.execute("""
            INSERT INTO transaksi
            (kode_invoice, pelanggan_id, paket_id, tanggal_berangkat,
             jumlah_orang, total_harga, catatan)
            VALUES (?,?,?,?,?,?,?)
        """, (kode, pelanggan_id, paket_id, tanggal_berangkat,
              jumlah_orang, total_harga, catatan))
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return TransaksiModel.get_by_id(new_id)

    @staticmethod
    def update_status(tid: int, status: str):
        conn = get_connection()
        conn.execute("UPDATE transaksi SET status=? WHERE id=?", (status, tid))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(tid: int):
        conn = get_connection()
        conn.execute("DELETE FROM transaksi WHERE id=?", (tid,))
        conn.commit()
        conn.close()

    @staticmethod
    def search(keyword: str) -> List[Transaksi]:
        conn = get_connection()
        like = f"%{keyword}%"
        rows = conn.execute("""
            SELECT t.*, p.nama AS nama_pelanggan,
                   pw.nama_paket, pw.destinasi
            FROM transaksi t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            JOIN paket_wisata pw ON t.paket_id = pw.id
            WHERE t.kode_invoice LIKE ? OR p.nama LIKE ? OR pw.nama_paket LIKE ? OR pw.destinasi LIKE ?
            ORDER BY t.created_at DESC
        """, (like, like, like, like)).fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            trx = Transaksi(
                id=d["id"], kode_invoice=d["kode_invoice"],
                pelanggan_id=d["pelanggan_id"], paket_id=d["paket_id"],
                tanggal_pesan=d["tanggal_pesan"],
                tanggal_berangkat=d["tanggal_berangkat"],
                jumlah_orang=d["jumlah_orang"], total_harga=d["total_harga"],
                status=d["status"], catatan=d["catatan"],
                created_at=d["created_at"],
                nama_pelanggan=d["nama_pelanggan"],
                nama_paket=d["nama_paket"], destinasi=d["destinasi"],
            )
            result.append(trx)
        return result

    @staticmethod
    def filter_by_status(status: str) -> List[Transaksi]:
        conn = get_connection()
        rows = conn.execute("""
            SELECT t.*, p.nama AS nama_pelanggan,
                   pw.nama_paket, pw.destinasi
            FROM transaksi t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            JOIN paket_wisata pw ON t.paket_id = pw.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
        """, (status,)).fetchall()
        conn.close()
        result = []
        for r in rows:
            d = dict(r)
            trx = Transaksi(
                id=d["id"], kode_invoice=d["kode_invoice"],
                pelanggan_id=d["pelanggan_id"], paket_id=d["paket_id"],
                tanggal_pesan=d["tanggal_pesan"],
                tanggal_berangkat=d["tanggal_berangkat"],
                jumlah_orang=d["jumlah_orang"], total_harga=d["total_harga"],
                status=d["status"], catatan=d["catatan"],
                created_at=d["created_at"],
                nama_pelanggan=d["nama_pelanggan"],
                nama_paket=d["nama_paket"], destinasi=d["destinasi"],
            )
            result.append(trx)
        return result

    @staticmethod
    def get_stats() -> dict:
        """Statistik ringkasan untuk dashboard."""
        conn = get_connection()
        total_trx    = conn.execute("SELECT COUNT(*) FROM transaksi").fetchone()[0]
        total_rev    = conn.execute("SELECT COALESCE(SUM(total_harga),0) FROM transaksi WHERE status='Confirmed'").fetchone()[0]
        total_cust   = conn.execute("SELECT COUNT(*) FROM pelanggan").fetchone()[0]
        total_paket  = conn.execute("SELECT COUNT(*) FROM paket_wisata WHERE tersedia=1").fetchone()[0]
        pending      = conn.execute("SELECT COUNT(*) FROM transaksi WHERE status='Pending'").fetchone()[0]

        # Transaksi per bulan (6 bulan terakhir)
        monthly = conn.execute("""
            SELECT strftime('%Y-%m', tanggal_pesan) AS bulan,
                   COUNT(*) AS jumlah,
                   SUM(total_harga) AS revenue
            FROM transaksi
            GROUP BY bulan
            ORDER BY bulan DESC
            LIMIT 6
        """).fetchall()

        # Top paket
        top_paket = conn.execute("""
            SELECT pw.nama_paket, COUNT(*) AS cnt
            FROM transaksi t
            JOIN paket_wisata pw ON t.paket_id = pw.id
            GROUP BY pw.nama_paket
            ORDER BY cnt DESC
            LIMIT 5
        """).fetchall()

        conn.close()
        return {
            "total_transaksi": total_trx,
            "total_revenue": total_rev,
            "total_pelanggan": total_cust,
            "total_paket": total_paket,
            "pending": pending,
            "monthly": [dict(r) for r in monthly],
            "top_paket": [dict(r) for r in top_paket],
        }
