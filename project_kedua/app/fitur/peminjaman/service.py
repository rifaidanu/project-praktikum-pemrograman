"""Paket 3. Aturan bisnis peminjaman (menu 3 dan 4)."""


class PeminjamanService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def buat_transaksi(self, nim, daftar_kode, lama_hari):
        """Membuat peminjaman. Mengembalikan ID transaksi.

        TODO, tolak jika:
        - mahasiswa tidak ditemukan (self._pembaca.ambil_mahasiswa)
        - transaksi aktif sudah Mahasiswa.MAKS_TRANSAKSI_AKTIF (Aturan 2)
        - daftar_kode kosong atau berisi kode ganda
        - ada alat yang tidak ditemukan atau tidak tersedia (Aturan 1: ambil_alat, tersedia)
        - lama_hari di luar 1 sampai Transaksi.MAKS_HARI
        Batas kembali = date.today() + timedelta(days=lama_hari).
        Diskusikan: bolehkah mahasiswa berstatus 'tidak aktif' meminjam?
        """
        raise NotImplementedError("Paket 3: PeminjamanService.buat_transaksi")

    def daftar_alat_tersedia(self):
        """TODO: self._pembaca.daftar_alat_tersedia()."""
        raise NotImplementedError("Paket 3: PeminjamanService.daftar_alat_tersedia")

    def daftar_transaksi(self):
        """List objek Transaksi."""
        raise NotImplementedError("Paket 3: PeminjamanService.daftar_transaksi")
