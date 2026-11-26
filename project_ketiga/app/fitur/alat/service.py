"""Paket 2. Aturan bisnis alat (menu 2, 7, 8, 9)."""
from app.errors import AturanBisnisError
from app.models import Alat, KondisiAlat, StatusAlat


class AlatService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def tambah(self, kode, nama, kategori, kondisi=KondisiAlat.BAIK):
        """Mendaftarkan alat baru. Aturan 5: alat rusak langsung tidak tersedia."""
        kode = kode.strip().upper()
        nama = nama.strip()
        kategori = kategori.strip()
        status = Alat.status_untuk_kondisi(kondisi)

        lama = self._pembaca.ambil_alat(kode, termasuk_dihapus=True)
        if lama is not None:
            if not lama.dihapus:
                raise AturanBisnisError(f"Alat dengan kode '{kode}' sudah terdaftar.")
            # Kode milik alat yang pernah dihapus: dipakai lagi agar riwayat tetap utuh
            lama.nama, lama.kategori = nama, kategori
            lama.kondisi, lama.status, lama.dihapus = kondisi, status, False
            self._repository.perbarui(lama)
            return lama

        baru = Alat(kode, nama, kategori, kondisi, status)
        self._repository.tambah(baru)
        return baru

    def ambil(self, kode):
        """Objek Alat untuk menu edit/hapus. Tolak jika tidak ditemukan."""
        kode = kode.strip().upper()
        alat = self._pembaca.ambil_alat(kode)
        if alat is None:
            raise AturanBisnisError(f"Alat dengan kode '{kode}' tidak ditemukan.")
        return alat

    def edit(self, kode, nama, kategori, kondisi):
        """Mengubah data alat. Kondisi alat yang dipinjam hanya berubah lewat pengembalian."""
        alat = self.ambil(kode)
        if alat.status == StatusAlat.DIPINJAM:
            if kondisi != alat.kondisi:
                raise AturanBisnisError(
                    "Kondisi alat yang sedang dipinjam hanya bisa berubah lewat pengembalian."
                )
        else:
            alat.status = Alat.status_untuk_kondisi(kondisi)
        alat.nama = nama.strip()
        alat.kategori = kategori.strip()
        alat.kondisi = kondisi
        self._repository.perbarui(alat)
        return alat

    def hapus(self, kode):
        """Aturan 6: tolak jika tidak ditemukan atau masih ada di transaksi aktif."""
        alat = self.ambil(kode)
        if self._pembaca.alat_di_transaksi_aktif(alat.kode):
            raise AturanBisnisError(
                f"Alat '{alat.nama}' ({alat.kode}) masih ada di transaksi aktif."
            )
        self._repository.tandai_dihapus(alat.kode)

    def cari(self, kata_kunci):
        """Tantangan A: cari berdasarkan kode, sebagian nama, atau kategori."""
        return self._repository.cari(kata_kunci.strip())

    def daftar_tersedia(self):
        return self._repository.daftar_tersedia()

    def daftar_dipinjam(self):
        return self._repository.daftar_dipinjam()

    def daftar_rusak(self):
        return self._repository.daftar_rusak()
