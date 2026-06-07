"""
SmartTravel - Database Configuration
Handles SQLite connection and schema initialization.
"""

import sqlite3
import os
from pathlib import Path

# Path ke file database
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "smarttravel.db"


def get_connection() -> sqlite3.Connection:
    """Mengembalikan koneksi SQLite dengan row_factory aktif."""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    """Membuat semua tabel jika belum ada dan mengisi data awal."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Tabel Users (login) ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'admin',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Tabel Pelanggan ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pelanggan (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nama       TEXT NOT NULL,
            email      TEXT UNIQUE,
            telepon    TEXT,
            alamat     TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Tabel Paket Wisata ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paket_wisata (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_paket  TEXT    NOT NULL,
            destinasi   TEXT    NOT NULL,
            durasi_hari INTEGER NOT NULL DEFAULT 1,
            harga       REAL    NOT NULL,
            deskripsi   TEXT,
            tersedia    INTEGER NOT NULL DEFAULT 1,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Tabel Transaksi (Reservasi) ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_invoice   TEXT    NOT NULL UNIQUE,
            pelanggan_id   INTEGER NOT NULL REFERENCES pelanggan(id),
            paket_id       INTEGER NOT NULL REFERENCES paket_wisata(id),
            tanggal_pesan  DATE    NOT NULL DEFAULT (date('now')),
            tanggal_berangkat DATE,
            jumlah_orang   INTEGER NOT NULL DEFAULT 1,
            total_harga    REAL    NOT NULL,
            status         TEXT    NOT NULL DEFAULT 'Pending',
            catatan        TEXT,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Seed: default admin ──────────────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin"),
        )

    # ── Seed: sample paket wisata ────────────────────────────────────────────
    cursor.execute("SELECT COUNT(*) FROM paket_wisata")
    if cursor.fetchone()[0] == 0:
        sample_packages = [
            ("Bali Paradise", "Bali", 5, 3_500_000, "Paket lengkap Bali 5 hari 4 malam"),
            ("Lombok Adventure", "Lombok", 4, 2_800_000, "Jelajahi keindahan Lombok"),
            ("Raja Ampat Dive", "Raja Ampat", 7, 8_500_000, "Diving eksklusif Raja Ampat"),
            ("Yogya Heritage", "Yogyakarta", 3, 1_500_000, "Wisata budaya Yogyakarta"),
            ("Labuan Bajo Explorer", "Labuan Bajo", 5, 6_000_000, "Komodo & Keajaiban NTT"),
        ]
        cursor.executemany(
            "INSERT INTO paket_wisata (nama_paket, destinasi, durasi_hari, harga, deskripsi) VALUES (?,?,?,?,?)",
            sample_packages,
        )

    conn.commit()
    conn.close()
    print(f"[DB] Database siap di: {DB_PATH}")
