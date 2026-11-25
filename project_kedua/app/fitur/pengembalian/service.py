"""Paket 4. Aturan bisnis pengembalian (menu 5 dan 6)."""


class PengembalianService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def ambil_transaksi_aktif(self, id_transaksi):
        """Objek Transaksi. Tolak jika tidak ditemukan atau sudah selesai.

        TODO: self._pembaca.ambil_transaksi, transaksi.masih_aktif()
        """
        raise NotImplementedError("Paket 4: PengembalianService.ambil_transaksi_aktif")

    def kembalikan(self, id_transaksi, daftar_kembali):
        """Memproses pengembalian sebagian atau semua. Mengembalikan StatusTransaksi baru.

        daftar_kembali: dict {kode_alat: KondisiAlat}. Nilainya enum, bukan teks "baik".
        TODO: tolak jika kosong atau ada kode yang tidak ada di transaksi.item_belum_kembali().
        Tanggal kembali = date.today().
        """
        raise NotImplementedError("Paket 4: PengembalianService.kembalikan")

    def cari_per_mahasiswa(self, kata_kunci):
        """List objek Transaksi."""
        raise NotImplementedError("Paket 4: PengembalianService.cari_per_mahasiswa")
