"""Satu pintu akses ke database MySQL online."""
import os
from contextlib import contextmanager
from enum import Enum
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import ClientFlag, Error, errorcode

from app.errors import DatabaseError, DataGandaError

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _terjemahkan(error):
    """Mengubah error MySQL menjadi error milik aplikasi."""
    if error.errno == errorcode.ER_DUP_ENTRY:
        return DataGandaError("Data dengan kode/NIM/ID tersebut sudah ada.")
    return DatabaseError(str(error))


def _siapkan(params):
    """Enum diubah ke nilainya, misal KondisiAlat.BAIK menjadi 'baik'."""
    return tuple(p.value if isinstance(p, Enum) else p for p in params)


class SesiQuery:
    """Menjalankan query lewat satu cursor. Dipakai di dalam `with db.transaksi()`."""

    def __init__(self, cursor):
        self._cursor = cursor

    def fetch_all(self, sql, params=()):
        """SELECT banyak baris. Hasil: list of dict."""
        self._cursor.execute(sql, _siapkan(params))
        return self._cursor.fetchall()

    def fetch_one(self, sql, params=()):
        """SELECT satu baris. Hasil: dict, atau None jika tidak ada."""
        baris = self.fetch_all(sql, params)
        return baris[0] if baris else None

    def execute(self, sql, params=()):
        """INSERT/UPDATE/DELETE. Hasil: jumlah baris yang cocok."""
        self._cursor.execute(sql, _siapkan(params))
        return self._cursor.rowcount


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
                # SELECT selalu membaca data terbaru, termasuk perubahan anggota lain
                "autocommit": True,
                # UPDATE menghitung baris yang cocok, walaupun nilainya tidak berubah
                "client_flags": [ClientFlag.FOUND_ROWS],
            }
            ssl_ca = os.getenv("DB_SSL_CA")
            if ssl_ca:
                config["ssl_ca"] = str(ROOT / ssl_ca)
            self.conn = mysql.connector.connect(**config)
            return True
        except (Error, ValueError) as e:
            print(f"⚠️ Gagal terhubung ke database: {e}")
            return False

    @contextmanager
    def _sesi(self):
        """Membuka cursor, lalu menutupnya. Menyambung ulang jika koneksi terputus."""
        if self.conn is None:
            raise DatabaseError("Belum terhubung ke database.")
        cursor = None
        try:
            self.conn.ping(reconnect=True, attempts=3, delay=1)
            cursor = self.conn.cursor(dictionary=True)
            yield SesiQuery(cursor)
        except Error as e:
            raise _terjemahkan(e) from e
        finally:
            if cursor is not None:
                cursor.close()

    @contextmanager
    def transaksi(self):
        """Beberapa query sebagai SATU transaction.

        Blok selesai tanpa error -> commit. Ada error apa pun -> rollback semua.

            with db.transaksi() as trx:
                trx.execute("UPDATE ...", (...))
                trx.execute("INSERT ...", (...))
        """
        with self._sesi() as sesi:
            self.conn.start_transaction()
            try:
                yield sesi
                self.conn.commit()
            except BaseException:
                try:
                    self.conn.rollback()
                except Error:
                    pass  # koneksi putus: server rollback sendiri, error asli diteruskan
                raise

    def fetch_all(self, sql, params=()):
        """SELECT banyak baris. Hasil: list of dict."""
        with self._sesi() as sesi:
            return sesi.fetch_all(sql, params)

    def fetch_one(self, sql, params=()):
        """SELECT satu baris. Hasil: dict, atau None jika tidak ada."""
        with self._sesi() as sesi:
            return sesi.fetch_one(sql, params)

    def execute(self, sql, params=()):
        """Satu INSERT/UPDATE/DELETE, langsung tersimpan. Hasil: jumlah baris yang cocok."""
        with self._sesi() as sesi:
            return sesi.execute(sql, params)

    def close(self):
        """Menutup koneksi. Panggil saat user memilih menu Keluar."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
