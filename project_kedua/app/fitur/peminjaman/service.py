"""Paket 3. Aturan bisnis peminjaman (menu 3 dan 4)."""
from datetime import date, timedelta

from app.errors import AturanBisnisError
from app.models import Mahasiswa, StatusMahasiswa, Transaksi


class PeminjamanService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def buat_transaksi(self, nim, daftar_kode, lama_hari):
        """Membuat peminjaman. Mengembalikan ID transaksi."""
        self._periksa_mahasiswa(nim)
        self._periksa_daftar_kode(daftar_kode)
        if not 1 <= lama_hari <= Transaksi.MAKS_HARI:
            raise AturanBisnisError(f"Lama pinjam harus 1 sampai {Transaksi.MAKS_HARI} hari.")
        self._periksa_alat(daftar_kode)

        tgl_pinjam = date.today()
        batas_kembali = tgl_pinjam + timedelta(days=lama_hari)
        return self._repository.simpan(nim, daftar_kode, tgl_pinjam, batas_kembali)

    def _periksa_mahasiswa(self, nim):
        mahasiswa = self._pembaca.ambil_mahasiswa(nim)
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        if mahasiswa.status_aktif != StatusMahasiswa.AKTIF:
            raise AturanBisnisError(f"Mahasiswa {mahasiswa.nama} berstatus tidak aktif.")
        if self._pembaca.hitung_transaksi_aktif(nim) >= Mahasiswa.MAKS_TRANSAKSI_AKTIF:
            raise AturanBisnisError(
                f"{mahasiswa.nama} sudah punya {Mahasiswa.MAKS_TRANSAKSI_AKTIF} transaksi aktif."
            )

    @staticmethod
    def _periksa_daftar_kode(daftar_kode):
        if not daftar_kode:
            raise AturanBisnisError("Pilih minimal satu alat.")
        if len(set(daftar_kode)) != len(daftar_kode):
            raise AturanBisnisError("Ada kode alat yang ditulis lebih dari sekali.")

    def _periksa_alat(self, daftar_kode):
        for kode in daftar_kode:
            alat = self._pembaca.ambil_alat(kode)
            if alat is None:
                raise AturanBisnisError(f"Alat dengan kode '{kode}' tidak ditemukan.")
            if not alat.tersedia():
                raise AturanBisnisError(f"{alat.nama} ({kode}) berstatus {alat.status.value}.")

    def daftar_alat_tersedia(self):
        """List objek Alat yang siap dipinjam."""
        return self._pembaca.daftar_alat_tersedia()

    def daftar_transaksi(self):
        """List objek Transaksi."""
        return self._repository.daftar_transaksi()
