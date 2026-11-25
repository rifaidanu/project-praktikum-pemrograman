"""Paket 3. Input dan tampilan peminjaman (menu 3 dan 4)."""
from app import ui


class PeminjamanMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def buat_transaksi(self):
        """Menu 3.

        TODO: tampilkan alat tersedia -> minta NIM -> minta kode alat dipisah koma (jadikan
        list, strip, upper) -> ui.input_angka lama hari -> service.buat_transaksi -> tampilkan ID.
        """
        raise NotImplementedError("Paket 3: PeminjamanMenu.buat_transaksi")

    def tampilkan_transaksi(self):
        """Menu 4.

        TODO: service.daftar_transaksi -> tampilkan tiap transaksi dan alatnya.
        Tandai yang terlambat dengan transaksi.terlambat().
        """
        raise NotImplementedError("Paket 3: PeminjamanMenu.tampilkan_transaksi")
