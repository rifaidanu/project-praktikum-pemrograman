"""Jenis error milik aplikasi. Menu cukup mengenal error di file ini, bukan error MySQL."""


class AturanBisnisError(Exception):
    """Permintaan user ditolak aturan bisnis, misal alat sedang dipinjam."""


class DatabaseError(Exception):
    """Query atau koneksi database bermasalah."""


class DataGandaError(DatabaseError):
    """PRIMARY KEY sudah dipakai, misal NIM yang sama didaftarkan dua kali."""
