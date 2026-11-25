"""Paket 1. Aturan bisnis mahasiswa (menu 1 dan 10)."""
from app.errors import AturanBisnisError
from app.models import Mahasiswa, StatusMahasiswa


class MahasiswaService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def tambah(self, nim, nama, no_hp):
        """Mendaftarkan mahasiswa baru."""
        nim = nim.strip().upper()
        nama = nama.strip()
        no_hp = no_hp.strip() if no_hp else None

        lama = self._pembaca.ambil_mahasiswa(nim, termasuk_dihapus=True)
        if lama is not None:
            if not lama.dihapus:
                raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' sudah terdaftar.")
            lama.nama = nama
            lama.no_hp = no_hp
            lama.status_aktif = StatusMahasiswa.AKTIF
            lama.dihapus = False
            self._repository.perbarui(lama)
            return

        baru = Mahasiswa(nim, nama, no_hp)
        self._repository.tambah(baru)

    def ambil(self, nim):
        """Objek Mahasiswa untuk menu edit. Tolak jika tidak ditemukan."""
        nim = nim.strip().upper()
        mahasiswa = self._pembaca.ambil_mahasiswa(nim)
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        return mahasiswa

    def edit(self, nim, nama, no_hp, status_aktif):
        """Mengubah data mahasiswa. Tolak jika NIM tidak ditemukan."""
        mahasiswa = self.ambil(nim)
        mahasiswa.nama = nama.strip()
        mahasiswa.no_hp = no_hp.strip() if no_hp else None
        mahasiswa.status_aktif = status_aktif
        self._repository.perbarui(mahasiswa)

    def hapus(self, nim):
        """Aturan 6: tolak jika tidak ditemukan atau masih punya transaksi aktif."""
        mahasiswa = self.ambil(nim)
        jumlah_aktif = self._pembaca.hitung_transaksi_aktif(mahasiswa.nim)
        if jumlah_aktif > 0:
            raise AturanBisnisError(
                f"Mahasiswa '{mahasiswa.nama}' masih memiliki {jumlah_aktif} transaksi aktif."
            )
        self._repository.tandai_dihapus(mahasiswa.nim)

    def cari(self, kata_kunci):
        """List objek Mahasiswa."""
        return self._repository.cari(kata_kunci.strip())

    def riwayat(self, nim):
        """List objek Transaksi. Tolak jika mahasiswa tidak ditemukan."""
        nim = nim.strip().upper()
        mahasiswa = self._pembaca.ambil_mahasiswa(nim, termasuk_dihapus=True)
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        return self._repository.riwayat(nim)