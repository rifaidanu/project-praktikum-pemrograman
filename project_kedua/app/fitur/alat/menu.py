"""Paket 2. Input dan tampilan alat (menu 2, 7, 8, 9)."""
from app import ui


class AlatMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def kelola(self):
        """Menu 2. Submenu sudah jadi, tinggal isi method di bawah."""
        ui.jalankan_menu("KELOLA ALAT", [
            ("Tambah alat", self.tambah),
            ("Edit alat", self.edit),
            ("Hapus alat", self.hapus),
            ("Cari alat", self.cari),
        ])

    def tambah(self):
        """TODO: input kode, nama, kategori, ui.input_enum(KondisiAlat) -> service.tambah."""
        raise NotImplementedError("Paket 2: AlatMenu.tambah")

    def edit(self):
        """TODO: minta kode -> service.ambil -> ui.input_opsional, ui.input_enum -> service.edit."""
        raise NotImplementedError("Paket 2: AlatMenu.edit")

    def hapus(self):
        """TODO: minta kode -> ui.konfirmasi -> service.hapus."""
        raise NotImplementedError("Paket 2: AlatMenu.hapus")

    def cari(self):
        """TODO: minta kata kunci -> service.cari -> ui.tabel."""
        raise NotImplementedError("Paket 2: AlatMenu.cari")

    def tampilkan_tersedia(self):
        """Menu 7. TODO: service.daftar_tersedia -> ui.tabel."""
        raise NotImplementedError("Paket 2: AlatMenu.tampilkan_tersedia")

    def tampilkan_dipinjam(self):
        """Menu 8. TODO: service.daftar_dipinjam -> ui.tabel."""
        raise NotImplementedError("Paket 2: AlatMenu.tampilkan_dipinjam")

    def tampilkan_rusak(self):
        """Menu 9. TODO: service.daftar_rusak -> ui.tabel."""
        raise NotImplementedError("Paket 2: AlatMenu.tampilkan_rusak")
