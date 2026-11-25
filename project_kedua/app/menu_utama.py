"""Merakit semua fitur dan menampilkan menu utama."""
from app import ui
from app.fitur.alat.menu import AlatMenu
from app.fitur.alat.repository import AlatRepository
from app.fitur.alat.service import AlatService
from app.fitur.mahasiswa.menu import MahasiswaMenu
from app.fitur.mahasiswa.repository import MahasiswaRepository
from app.fitur.mahasiswa.service import MahasiswaService
from app.fitur.peminjaman.menu import PeminjamanMenu
from app.fitur.peminjaman.repository import PeminjamanRepository
from app.fitur.peminjaman.service import PeminjamanService
from app.fitur.pengembalian.menu import PengembalianMenu
from app.fitur.pengembalian.repository import PengembalianRepository
from app.fitur.pengembalian.service import PengembalianService
from app.pembaca_data import PembacaData


class MenuUtama:
    def __init__(self, db):
        pembaca = PembacaData(db)
        mahasiswa = MahasiswaMenu(MahasiswaService(MahasiswaRepository(db, pembaca), pembaca))
        alat = AlatMenu(AlatService(AlatRepository(db, pembaca), pembaca))
        peminjaman = PeminjamanMenu(PeminjamanService(PeminjamanRepository(db, pembaca), pembaca))
        pengembalian = PengembalianMenu(
            PengembalianService(PengembalianRepository(db, pembaca), pembaca)
        )
        # Nomor menu mengikuti urutan list (bagian E di Group Project 2.docx).
        # Fitur tantangan ditambahkan di akhir list.
        self._daftar_menu = [
            ("Kelola data mahasiswa", mahasiswa.kelola),
            ("Kelola data alat", alat.kelola),
            ("Buat transaksi peminjaman", peminjaman.buat_transaksi),
            ("Tampilkan transaksi", peminjaman.tampilkan_transaksi),
            ("Proses pengembalian alat", pengembalian.proses_pengembalian),
            ("Cari transaksi berdasarkan mahasiswa", pengembalian.cari_transaksi),
            ("Tampilkan alat yang tersedia", alat.tampilkan_tersedia),
            ("Tampilkan alat yang sedang dipinjam", alat.tampilkan_dipinjam),
            ("Tampilkan alat yang rusak", alat.tampilkan_rusak),
            ("Riwayat peminjaman mahasiswa", mahasiswa.tampilkan_riwayat),
        ]

    def jalankan(self):
        ui.jalankan_menu("SISTEM PEMINJAMAN ALAT LAB", self._daftar_menu, "Keluar")
