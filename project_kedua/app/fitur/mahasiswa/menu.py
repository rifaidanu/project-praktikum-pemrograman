"""Paket 1. Input dan tampilan mahasiswa (menu 1 dan 10)."""
from app import ui


class MahasiswaMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def kelola(self):
        """Menu 1. Submenu sudah jadi, tinggal isi method di bawah."""
        ui.jalankan_menu("KELOLA MAHASISWA", [
            ("Tambah mahasiswa", self.tambah),
            ("Edit mahasiswa", self.edit),
            ("Hapus mahasiswa", self.hapus),
            ("Cari mahasiswa", self.cari),
        ])

    def tambah(self):
        """TODO: ui.input_wajib untuk NIM, nama, no HP -> service.tambah -> ui.sukses."""
        raise NotImplementedError("Paket 1: MahasiswaMenu.tambah")

    def edit(self):
        """TODO: minta NIM -> service.ambil -> ui.input_opsional, ui.input_enum -> service.edit."""
        raise NotImplementedError("Paket 1: MahasiswaMenu.edit")

    def hapus(self):
        """TODO: minta NIM -> ui.konfirmasi -> service.hapus."""
        raise NotImplementedError("Paket 1: MahasiswaMenu.hapus")

    def cari(self):
        """TODO: minta kata kunci -> service.cari -> ui.tabel."""
        raise NotImplementedError("Paket 1: MahasiswaMenu.cari")

    def tampilkan_riwayat(self):
        """Menu 10. TODO: minta NIM -> service.riwayat -> tampilkan transaksi dan alatnya."""
        raise NotImplementedError("Paket 1: MahasiswaMenu.tampilkan_riwayat")
