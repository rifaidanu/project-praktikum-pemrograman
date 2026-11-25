"""Paket 4. Input dan tampilan pengembalian (menu 5 dan 6)."""
from app import ui


class PengembalianMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def proses_pengembalian(self):
        """Menu 5.

        TODO: minta ID transaksi -> service.ambil_transaksi_aktif -> tampilkan item_belum_kembali
        -> minta kode alat (boleh beberapa) -> ui.input_enum(KondisiAlat) untuk tiap alat
        -> service.kembalikan -> tampilkan status transaksi terbaru.
        """
        raise NotImplementedError("Paket 4: PengembalianMenu.proses_pengembalian")

    def cari_transaksi(self):
        """Menu 6. TODO: minta NIM/nama -> service.cari_per_mahasiswa -> tampilkan hasil."""
        raise NotImplementedError("Paket 4: PengembalianMenu.cari_transaksi")
