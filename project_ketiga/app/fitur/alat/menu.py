"""Paket 2. Input dan tampilan alat (menu 2, 7, 8, 9)."""
from app import ui
from app.models.alat import KondisiAlat


class AlatMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    KOLOM = ["Kode", "Nama", "Kategori", "Kondisi", "Status"]

    def __init__(self, service):
        self._service = service

    def kelola(self):
        """Menu 2."""
        ui.jalankan_menu("KELOLA ALAT", [
            ("Tambah alat", self.tambah),
            ("Edit alat", self.edit),
            ("Hapus alat", self.hapus),
            ("Cari alat", self.cari),
        ])

    def tambah(self):
        kode = ui.input_teks("Kode alat")
        nama = ui.input_teks("Nama alat")
        kategori = ui.input_teks("Kategori")
        kondisi = ui.input_enum(KondisiAlat)
        alat = self._service.tambah(kode, nama, kategori, kondisi)
        print(f"Alat {alat.kode} berhasil ditambahkan.")

    def edit(self):
        kode = ui.input_teks("Kode alat yang diedit")
        alat = self._service.ambil(kode)  # error 'tidak ditemukan' muncul sebelum form diisi
        print("Kosongkan untuk tetap memakai nilai lama.")
        nama = ui.input_opsional("Nama", alat.nama)
        kategori = ui.input_opsional("Kategori", alat.kategori)
        kondisi = ui.input_enum(KondisiAlat)
        alat = self._service.edit(alat.kode, nama, kategori, kondisi)
        print(f"Alat {alat.kode} berhasil diperbarui.")

    def hapus(self):
        kode = ui.input_teks("Kode alat yang dihapus")
        alat = self._service.ambil(kode)
        if not ui.konfirmasi(f"Hapus alat {alat.kode} ({alat.nama})?"):
            print("Penghapusan dibatalkan.")
            return
        self._service.hapus(alat.kode)
        print(f"Alat {alat.kode} berhasil dihapus.")

    def cari(self):
        kata = ui.input_teks("Cari berdasarkan kode / nama / kategori")
        self._tampilkan(self._service.cari(kata))

    def tampilkan_tersedia(self):
        """Menu 7."""
        self._tampilkan(self._service.daftar_tersedia())

    def tampilkan_dipinjam(self):
        """Menu 8."""
        self._tampilkan(self._service.daftar_dipinjam())

    def tampilkan_rusak(self):
        """Menu 9."""
        self._tampilkan(self._service.daftar_rusak())

    def _tampilkan(self, daftar):
        if not daftar:
            print("(tidak ada data)")
            return
        ui.tabel(self.KOLOM, [[a.kode, a.nama, a.kategori, a.kondisi.value, a.status.value]
                              for a in daftar])