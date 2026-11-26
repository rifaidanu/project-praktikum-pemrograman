from datetime import date, timedelta
from app.errors import AturanBisnisError
from app.models import Mahasiswa, StatusMahasiswa, Transaksi

class PeminjamanService:
    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def buat_transaksi(self, nim, daftar_kode, lama_hari):
        nim = nim.strip().upper()

        # Lama pinjam: 1 sampai 7 hari
        if lama_hari < 1 or lama_hari > Transaksi.MAKS_HARI:
            raise AturanBisnisError(f"Lama pinjam harus 1 sampai {Transaksi.MAKS_HARI} hari.")

        # Daftar alat: tidak boleh kosong dan tidak boleh ada kode ganda
        if len(daftar_kode) == 0:
            raise AturanBisnisError("Pilih minimal satu alat.")
        if len(set(daftar_kode)) != len(daftar_kode):
            raise AturanBisnisError("Kode alat tidak boleh ganda.")

        # Mahasiswa harus ada dan berstatus aktif
        mahasiswa = self._pembaca.ambil_mahasiswa(nim)
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        if mahasiswa.status_aktif != StatusMahasiswa.AKTIF:
            raise AturanBisnisError(f"Mahasiswa '{mahasiswa.nama}' berstatus tidak aktif.")

        # Aturan 2: maksimal 2 transaksi aktif
        jumlah_aktif = self._pembaca.hitung_transaksi_aktif(nim)
        if jumlah_aktif >= Mahasiswa.MAKS_TRANSAKSI_AKTIF:
            raise AturanBisnisError(
                f"Mahasiswa sudah memiliki {jumlah_aktif} transaksi aktif "
                f"(maksimal {Mahasiswa.MAKS_TRANSAKSI_AKTIF})."
            )

        # Aturan 1: semua alat harus ada dan tersedia
        for kode in daftar_kode:
            alat = self._pembaca.ambil_alat(kode)
            if alat is None:
                raise AturanBisnisError(f"Alat '{kode}' tidak ditemukan.")
            if not alat.tersedia():
                raise AturanBisnisError(f"Alat '{kode}' tidak bisa dipinjam (status: {alat.status.value}).")

        # Semua aturan lolos, hitung tanggal lalu simpan
        hari_ini = date.today()
        batas_kembali = hari_ini + timedelta(days=lama_hari)
        return self._repository.simpan(nim, daftar_kode, hari_ini, batas_kembali)

    def daftar_alat_tersedia(self):
        return self._pembaca.daftar_alat_tersedia()

    def daftar_transaksi(self):
        return self._repository.daftar_transaksi()
