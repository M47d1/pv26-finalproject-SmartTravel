"""
SmartTravel - CSV Exporter
Mengekspor data transaksi ke format CSV dengan filter range tanggal.
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List
from models.models import Transaksi


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "database" / "exports"


def export_transaksi_to_csv(transaksi_list: List[Transaksi], filename: str = None) -> str:
    """
    Mengekspor data transaksi ke file CSV.

    Parameters
    ----------
    transaksi_list : List[Transaksi]
        List objek Transaksi yang akan diekspor
    filename : str, optional
        Nama file (tanpa path). Jika None, akan generate dari timestamp

    Returns
    -------
    str – absolute path ke file CSV yang dihasilkan

    Raises
    ------
    Exception
        Jika gagal membuat direktori atau menulis file
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"laporan_transaksi_{timestamp}.csv"

    filepath = OUTPUT_DIR / filename

    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'No',
                'Invoice',
                'Pelanggan',
                'Paket',
                'Tanggal Berangkat',
                'Jumlah Orang',
                'Total Harga (Rp)',
                'Status',
                'Tanggal Pesan',
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for idx, trx in enumerate(transaksi_list, start=1):
                writer.writerow({
                    'No': idx,
                    'Invoice': trx.kode_invoice,
                    'Pelanggan': trx.nama_pelanggan or '-',
                    'Paket': trx.nama_paket or '-',
                    'Tanggal Berangkat': trx.tanggal_berangkat or '-',
                    'Jumlah Orang': trx.jumlah_orang,
                    'Total Harga (Rp)': f"{trx.total_harga:,.0f}",
                    'Status': trx.status,
                    'Tanggal Pesan': trx.tanggal_pesan or '-',
                })

        return str(filepath)
    except Exception as e:
        raise Exception(f"Gagal membuat file CSV: {str(e)}")
