"""Paket 2. SQL untuk fitur alat (menu 2, 7, 8, 9)."""
from app.errors import AturanBisnisError
from app.models import Alat, KondisiAlat, StatusAlat, StatusTransaksi


class AlatRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def tambah(self, alat):
        """INSERT satu objek Alat."""
        self._db.execute(
            "INSERT INTO alat (kode, nama, kategori, kondisi, status, dihapus)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (alat.kode, alat.nama, alat.kategori, alat.kondisi, alat.status, alat.dihapus),
        )

    def perbarui(self, alat):
        """UPDATE nama, kategori, kondisi, status, dan dihapus berdasarkan kode."""
        return self._db.execute(
            "UPDATE alat SET nama = %s, kategori = %s, kondisi = %s, status = %s, dihapus = %s"
            " WHERE kode = %s",
            (alat.nama, alat.kategori, alat.kondisi, alat.status, alat.dihapus, alat.kode),
        )

    def tandai_dihapus(self, kode):
        """Mengisi dihapus = TRUE, hanya jika alat tidak ada di transaksi aktif (Aturan 6).
        Diperiksa ulang di dalam transaction agar aman dari komputer lain."""
        with self._db.transaksi() as trx:
            baris = trx.fetch_one(
                "SELECT kode FROM alat WHERE kode = %s AND dihapus = FALSE FOR UPDATE",
                (kode,),
            )
            if baris is None:
                raise AturanBisnisError(f"Alat dengan kode '{kode}' tidak ditemukan.")

            aktif = trx.fetch_one(
                "SELECT COUNT(*) AS jumlah FROM detail_transaksi d"
                " JOIN transaksi t ON t.id = d.id_transaksi"
                " WHERE d.kode_alat = %s AND t.status <> %s",
                (kode, StatusTransaksi.SELESAI),
            )
            if aktif["jumlah"] > 0:
                raise AturanBisnisError(
                    f"Alat '{kode}' tidak bisa dihapus karena masih ada di transaksi aktif."
                )

            trx.execute("UPDATE alat SET dihapus = TRUE WHERE kode = %s", (kode,))

    def cari(self, kata_kunci):
        """List objek Alat yang kode, nama, atau kategorinya mengandung kata_kunci."""
        pola = f"%{kata_kunci}%"
        baris = self._db.fetch_all(
            "SELECT * FROM alat"
            " WHERE dihapus = FALSE AND (kode LIKE %s OR nama LIKE %s OR kategori LIKE %s)"
            " ORDER BY kode",
            (pola, pola, pola),
        )
        return [Alat.dari_baris(b) for b in baris]

    def daftar_berdasarkan_status(self, status):
        """List objek Alat dengan status tertentu."""
        baris = self._db.fetch_all(
            "SELECT * FROM alat WHERE status = %s AND dihapus = FALSE ORDER BY kode",
            (status,),
        )
        return [Alat.dari_baris(b) for b in baris]

    def daftar_rusak(self):
        """List objek Alat yang kondisinya tidak baik."""
        baris = self._db.fetch_all(
            "SELECT * FROM alat WHERE kondisi <> %s AND dihapus = FALSE ORDER BY kode",
            (KondisiAlat.BAIK,),
        )
        return [Alat.dari_baris(b) for b in baris]

    def daftar_tersedia(self):
        return self.daftar_berdasarkan_status(StatusAlat.TERSEDIA)

    def daftar_dipinjam(self):
        return self.daftar_berdasarkan_status(StatusAlat.DIPINJAM)
