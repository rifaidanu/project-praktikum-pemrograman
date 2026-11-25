"""Paket 1. SQL untuk fitur mahasiswa (menu 1 dan 10)."""
from app.errors import AturanBisnisError
from app.models import Mahasiswa, StatusTransaksi


class MahasiswaRepository:
    """Hanya berisi SQL, tanpa input/print."""

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def tambah(self, mahasiswa):
        """INSERT satu objek Mahasiswa."""
        self._db.execute(
            "INSERT INTO mahasiswa (nim, nama, no_hp, status_aktif, dihapus)"
            " VALUES (%s, %s, %s, %s, %s)",
            (
                mahasiswa.nim,
                mahasiswa.nama,
                mahasiswa.no_hp,
                mahasiswa.status_aktif,
                mahasiswa.dihapus,
            ),
        )

    def perbarui(self, mahasiswa):
        """UPDATE nama, no_hp, status_aktif, dan dihapus berdasarkan nim."""
        return self._db.execute(
            "UPDATE mahasiswa SET nama = %s, no_hp = %s, status_aktif = %s, dihapus = %s"
            " WHERE nim = %s",
            (
                mahasiswa.nama,
                mahasiswa.no_hp,
                mahasiswa.status_aktif,
                mahasiswa.dihapus,
                mahasiswa.nim,
            ),
        )

    def tandai_dihapus(self, nim):
        """Mengisi dihapus = TRUE, hanya jika mahasiswa tidak punya transaksi aktif."""
        with self._db.transaksi() as trx:
            baris = trx.fetch_one(
                "SELECT nim FROM mahasiswa WHERE nim = %s AND dihapus = FALSE FOR UPDATE",
                (nim,),
            )
            if baris is None:
                raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")

            aktif = trx.fetch_one(
                "SELECT COUNT(*) AS jumlah FROM transaksi WHERE nim = %s AND status <> %s",
                (nim, StatusTransaksi.SELESAI),
            )
            if aktif["jumlah"] > 0:
                raise AturanBisnisError(
                    f"Mahasiswa tidak bisa dihapus karena masih memiliki {aktif['jumlah']} transaksi aktif."
                )

            trx.execute("UPDATE mahasiswa SET dihapus = TRUE WHERE nim = %s", (nim,))

    def cari(self, kata_kunci):
        """List objek Mahasiswa yang NIM atau namanya mengandung kata_kunci."""
        pola = f"%{kata_kunci}%"
        baris = self._db.fetch_all(
            "SELECT * FROM mahasiswa"
            " WHERE dihapus = FALSE AND (nim LIKE %s OR nama LIKE %s)"
            " ORDER BY nim",
            (pola, pola),
        )
        return [Mahasiswa.dari_baris(b) for b in baris]

    def riwayat(self, nim):
        """List objek Transaksi milik mahasiswa, aktif maupun selesai."""
        return self._pembaca.daftar_transaksi("t.nim = %s", (nim,))