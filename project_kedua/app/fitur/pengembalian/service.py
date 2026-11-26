"""Paket 4. Aturan bisnis pengembalian (menu 5 dan 6)."""
from datetime import date

from app.errors import AturanBisnisError


class PengembalianService:
    """Validasi dulu, baru panggil repository. Penolakan memakai AturanBisnisError."""

    def __init__(self, repository, pembaca):
        self._repository = repository
        self._pembaca = pembaca

    def ambil_transaksi_aktif(self, id_transaksi):
        """Objek Transaksi. Tolak jika tidak ditemukan atau sudah selesai."""
        transaksi = self._pembaca.ambil_transaksi(id_transaksi)
        if transaksi is None:
            raise AturanBisnisError(f"Transaksi '{id_transaksi}' tidak ditemukan.")
        if not transaksi.masih_aktif():
            raise AturanBisnisError(f"Transaksi {id_transaksi} sudah selesai.")
        return transaksi

    @staticmethod
    def periksa_kode_kembali(transaksi, daftar_kode):
        """Tolak jika kosong, ganda, atau ada kode yang tidak sedang dipinjam di transaksi ini."""
        if not daftar_kode:
            raise AturanBisnisError("Pilih minimal satu alat.")
        if len(set(daftar_kode)) != len(daftar_kode):
            raise AturanBisnisError("Ada kode alat yang ditulis lebih dari sekali.")
        belum_kembali = {item.kode_alat for item in transaksi.item_belum_kembali()}
        for kode in daftar_kode:
            if kode not in belum_kembali:
                raise AturanBisnisError(
                    f"Alat {kode} tidak sedang dipinjam di transaksi {transaksi.id_transaksi}."
                )

    def kembalikan(self, id_transaksi, daftar_kembali):
        """Memproses pengembalian sebagian atau semua. Mengembalikan StatusTransaksi baru.

        daftar_kembali: dict {kode_alat: KondisiAlat}. Nilainya enum, bukan teks "baik".
        """
        transaksi = self.ambil_transaksi_aktif(id_transaksi)
        self.periksa_kode_kembali(transaksi, list(daftar_kembali))
        return self._repository.simpan(id_transaksi, daftar_kembali, date.today())

    def cari_per_mahasiswa(self, kata_kunci):
        """List objek Transaksi."""
        kata_kunci = kata_kunci.strip()
        if not kata_kunci:
            raise AturanBisnisError("Kata kunci tidak boleh kosong.")
        return self._repository.cari_per_mahasiswa(kata_kunci)
