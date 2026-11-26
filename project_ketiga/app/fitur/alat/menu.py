"""Paket 2. Input dan tampilan alat (menu 2, 7, 8, 9)."""
from app import ui
from app.models import KondisiAlat, StatusAlat


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
        """Menu 2 -> 1: Tambah alat."""
        kode = ui.input_wajib("Kode alat").upper()
        nama = ui.input_wajib("Nama alat")
        kategori = ui.input_wajib("Kategori")
        kondisi = ui.input_enum("Kondisi", KondisiAlat)
        alat = self._service.tambah(kode, nama, kategori, kondisi)
        ui.sukses(f"Alat '{alat.nama}' ({alat.kode}) berhasil ditambahkan "
                  f"dengan status {alat.status.value}.")

    def edit(self):
        """Menu 2 -> 2: Edit alat."""
        kode = ui.input_wajib("Kode alat").upper()
        alat = self._service.ambil(kode)  # error 'tidak ditemukan' muncul sebelum form diisi
        nama = ui.input_opsional("Nama", alat.nama)
        kategori = ui.input_opsional("Kategori", alat.kategori)
        if alat.status == StatusAlat.DIPINJAM:
            ui.info("Alat sedang dipinjam, kondisi hanya bisa berubah lewat pengembalian.")
            kondisi = alat.kondisi
        else:
            kondisi = ui.input_enum(f"Kondisi (saat ini: {alat.kondisi.value})", KondisiAlat)
        alat = self._service.edit(alat.kode, nama, kategori, kondisi)
        ui.sukses(f"Data alat '{alat.kode}' berhasil diperbarui.")

    def hapus(self):
        """Menu 2 -> 3: Hapus alat."""
        kode = ui.input_wajib("Kode alat").upper()
        alat = self._service.ambil(kode)
        if ui.konfirmasi(f"Yakin ingin menghapus {alat.nama} ({alat.kode})?"):
            self._service.hapus(alat.kode)
            ui.sukses(f"Alat '{alat.nama}' ({alat.kode}) berhasil dihapus.")
        else:
            ui.info("Penghapusan dibatalkan.")

    def cari(self):
        """Menu 2 -> 4: Cari alat."""
        kata_kunci = input("Kata kunci kode/nama/kategori (kosong = semua): ").strip()
        self._tampilkan(self._service.cari(kata_kunci))

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
        ui.tabel(self.KOLOM, [[a.kode, a.nama, a.kategori, a.kondisi.value, a.status.value]
                              for a in daftar])
