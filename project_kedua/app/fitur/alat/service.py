"""Paket 2. Aturan bisnis alat (menu 2, 7, 8, 9)."""


class AlatService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def tambah(self, kode, nama, kategori, kondisi):
        """Menambah alat baru. Kategori bebas diketik user, jangan dibatasi if/elif.

        TODO
        - Tolak jika kode sudah ada. Kode pernah dihapus? Aktifkan lagi lewat perbarui.
        - Status awal: Alat.status_untuk_kondisi(kondisi), agar alat rusak tidak tersedia.
        """
        raise NotImplementedError("Paket 2: AlatService.tambah")

    def ambil(self, kode):
        """Objek Alat untuk menu edit. Tolak jika tidak ditemukan."""
        raise NotImplementedError("Paket 2: AlatService.ambil")

    def edit(self, kode, nama, kategori, kondisi):
        """Mengubah data alat. Tolak jika kode tidak ditemukan.

        TODO
        - Tolak perubahan kondisi jika alat sedang dipinjam (dicatat saat pengembalian).
        - Kondisi berubah? Status ikut berubah: Alat.status_untuk_kondisi(kondisi).
        - perbarui mengembalikan 0? Tolak: data baru saja diubah anggota lain.
        """
        raise NotImplementedError("Paket 2: AlatService.edit")

    def hapus(self, kode):
        """Aturan 6: tolak jika tidak ditemukan atau ada di transaksi aktif.

        TODO: self._pembaca.alat_di_transaksi_aktif(kode) untuk pesan yang ramah.
        """
        raise NotImplementedError("Paket 2: AlatService.hapus")

    def cari(self, kata_kunci):
        """List objek Alat."""
        raise NotImplementedError("Paket 2: AlatService.cari")

    def daftar_tersedia(self):
        """TODO: self._pembaca.daftar_alat_tersedia()."""
        raise NotImplementedError("Paket 2: AlatService.daftar_tersedia")

    def daftar_dipinjam(self):
        """List dict alat yang sedang dipinjam."""
        raise NotImplementedError("Paket 2: AlatService.daftar_dipinjam")

    def daftar_rusak(self):
        """List objek Alat rusak ringan dan rusak berat."""
        raise NotImplementedError("Paket 2: AlatService.daftar_rusak")
