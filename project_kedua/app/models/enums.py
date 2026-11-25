"""Pilihan status. Nilainya harus sama persis dengan ENUM di database/schema.sql."""
from enum import Enum


class StatusMahasiswa(Enum):
    AKTIF = "aktif"
    TIDAK_AKTIF = "tidak aktif"


class KondisiAlat(Enum):
    BAIK = "baik"
    RUSAK_RINGAN = "rusak ringan"
    RUSAK_BERAT = "rusak berat"


class StatusAlat(Enum):
    TERSEDIA = "tersedia"
    DIPINJAM = "dipinjam"
    TIDAK_TERSEDIA = "tidak tersedia"


class StatusTransaksi(Enum):
    DIPINJAM = "dipinjam"
    SEBAGIAN_DIKEMBALIKAN = "sebagian dikembalikan"
    SELESAI = "selesai"


class StatusItem(Enum):
    DIPINJAM = "dipinjam"
    DIKEMBALIKAN = "dikembalikan"
