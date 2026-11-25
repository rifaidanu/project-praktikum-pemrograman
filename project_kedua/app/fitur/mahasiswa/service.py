"""Paket 1. Aturan bisnis mahasiswa (menu 1 dan 10)."""


class MahasiswaService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def tambah(self, nim, nama, no_hp):
        """Mendaftarkan mahasiswa baru.

        TODO
        - Tolak jika NIM sudah ada (self._pembaca.ambil_mahasiswa).
        - NIM pernah dihapus? Baca dengan termasuk_dihapus=True, lalu aktifkan lagi (perbarui).
        """
        raise NotImplementedError("Paket 1: MahasiswaService.tambah")

    def ambil(self, nim):
        """Objek Mahasiswa untuk menu edit. Tolak jika tidak ditemukan."""
        raise NotImplementedError("Paket 1: MahasiswaService.ambil")

    def edit(self, nim, nama, no_hp, status_aktif):
        """Mengubah data mahasiswa. Tolak jika NIM tidak ditemukan."""
        raise NotImplementedError("Paket 1: MahasiswaService.edit")

    def hapus(self, nim):
        """Aturan 6: tolak jika tidak ditemukan atau masih punya transaksi aktif.

        TODO: self._pembaca.hitung_transaksi_aktif(nim) untuk pesan yang ramah.
        """
        raise NotImplementedError("Paket 1: MahasiswaService.hapus")

    def cari(self, kata_kunci):
        """List objek Mahasiswa."""
        raise NotImplementedError("Paket 1: MahasiswaService.cari")

    def riwayat(self, nim):
        """List objek Transaksi. Tolak jika mahasiswa tidak ditemukan.

        Diskusikan: bolehkah riwayat mahasiswa yang sudah dihapus dilihat (termasuk_dihapus)?
        """
        raise NotImplementedError("Paket 1: MahasiswaService.riwayat")
