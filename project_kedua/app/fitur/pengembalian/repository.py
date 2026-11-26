"""Paket 4. SQL untuk pengembalian (menu 5 dan 6)."""
from app.errors import AturanBisnisError
from app.models import Alat, StatusItem, StatusTransaksi


class PengembalianRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def simpan(self, id_transaksi, daftar_kembali, tgl_kembali):
        """Menyimpan pengembalian sebagai satu transaction. Mengembalikan StatusTransaksi baru.

        daftar_kembali: dict {kode_alat: KondisiAlat}
        """
        with self._db.transaksi() as trx:
            self._kunci_transaksi(trx, id_transaksi)
            for kode in sorted(daftar_kembali):
                self._kembalikan_alat(trx, id_transaksi, kode, daftar_kembali[kode], tgl_kembali)
            return self._perbarui_status(trx, id_transaksi)

    @staticmethod
    def _kunci_transaksi(trx, id_transaksi):
        """Mengunci baris transaksi agar dua pengembalian bersamaan diproses bergantian."""
        transaksi = trx.fetch_one(
            "SELECT status FROM transaksi WHERE id = %s FOR UPDATE", (id_transaksi,)
        )
        if transaksi is None:
            raise AturanBisnisError(f"Transaksi '{id_transaksi}' tidak ditemukan.")
        if transaksi["status"] == StatusTransaksi.SELESAI.value:
            raise AturanBisnisError(f"Transaksi {id_transaksi} sudah selesai.")

    @staticmethod
    def _kembalikan_alat(trx, id_transaksi, kode, kondisi, tgl_kembali):
        """Menandai item dikembalikan, lalu memperbarui alatnya (Aturan 5)."""
        jumlah = trx.execute(
            "UPDATE detail_transaksi SET status = %s, kondisi_kembali = %s, tgl_kembali = %s"
            " WHERE id_transaksi = %s AND kode_alat = %s AND status = %s",
            (StatusItem.DIKEMBALIKAN, kondisi, tgl_kembali, id_transaksi, kode,
             StatusItem.DIPINJAM),
        )
        if jumlah != 1:
            raise AturanBisnisError(f"Alat {kode} sudah dikembalikan atau bukan bagian transaksi ini.")
        trx.execute(
            "UPDATE alat SET kondisi = %s, status = %s WHERE kode = %s",
            (kondisi, Alat.status_untuk_kondisi(kondisi), kode),
        )

    @staticmethod
    def _perbarui_status(trx, id_transaksi):
        """Aturan 4: semua alat kembali -> selesai, sebagian -> sebagian dikembalikan."""
        baris = trx.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM detail_transaksi"
            " WHERE id_transaksi = %s AND status = %s",
            (id_transaksi, StatusItem.DIPINJAM),
        )
        status_baru = (
            StatusTransaksi.SELESAI if baris["jumlah"] == 0
            else StatusTransaksi.SEBAGIAN_DIKEMBALIKAN
        )
        trx.execute(
            "UPDATE transaksi SET status = %s WHERE id = %s", (status_baru, id_transaksi)
        )
        return status_baru

    def cari_per_mahasiswa(self, kata_kunci):
        """List objek Transaksi yang NIM atau nama mahasiswanya mengandung kata_kunci."""
        pola = f"%{kata_kunci}%"
        return self._pembaca.daftar_transaksi("t.nim LIKE %s OR m.nama LIKE %s", (pola, pola))
