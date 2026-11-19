"""Satu pintu akses ke database MySQL online."""
import os

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()  # membaca file .env di root repo


class Database:
    """Mengelola koneksi, query, dan transaction ke MySQL."""

    def __init__(self):
        self.conn = None

    def connect(self):
        """Membuka koneksi. Mengembalikan True jika berhasil, False jika gagal."""
        try:
            config = {
                "host": os.getenv("DB_HOST"),
                "port": int(os.getenv("DB_PORT", "3306")),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
                "connection_timeout": 10,
            }
            ssl_ca = os.getenv("DB_SSL_CA")
            if ssl_ca:
                config["ssl_ca"] = ssl_ca
            self.conn = mysql.connector.connect(**config)
            return True
        except (Error, ValueError) as e:
            print(f"⚠️ Gagal terhubung ke database: {e}")
            return False

    def _pastikan_terhubung(self):
        """Menyambung ulang jika koneksi terputus karena lama tidak dipakai."""
        self.conn.ping(reconnect=True, attempts=3, delay=1)

    def fetch_all(self, sql, params=()):
        """SELECT banyak baris. Hasil: list of dict, misal [{'kode': 'A001', ...}]."""
        self._pastikan_terhubung()
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            cur.close()

    def fetch_one(self, sql, params=()):
        """SELECT satu baris. Hasil: dict, atau None jika tidak ada."""
        self._pastikan_terhubung()
        cur = self.conn.cursor(dictionary=True)
        try:
            cur.execute(sql, params)
            return cur.fetchone()
        finally:
            cur.close()

    def execute(self, sql, params=()):
        """INSERT/UPDATE/DELETE satu perintah, langsung commit."""
        return self.run_transaction([(sql, params)])

    def run_transaction(self, langkah):
        """Menjalankan beberapa perintah sebagai SATU transaction.

        langkah: list of (sql, params).
        Semua berhasil -> commit. Satu gagal -> rollback semua, lalu error diteruskan.
        """
        self._pastikan_terhubung()
        cur = self.conn.cursor()
        try:
            for sql, params in langkah:
                cur.execute(sql, params)
            self.conn.commit()
            return cur.rowcount
        except Error:
            self.conn.rollback()
            raise
        finally:
            cur.close()

    def close(self):
        """Menutup koneksi. Panggil saat user memilih menu Keluar."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
