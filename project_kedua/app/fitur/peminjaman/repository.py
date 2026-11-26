from app.errors import AturanBisnisError, DataGandaError
from app.models import Mahasiswa, StatusAlat, StatusItem, StatusTransaksi

class PeminjamanRepository:
    MAKS_PERCOBAAN = 3

    def __init__(self, db, pembaca):
        self._db = db
        self._pembaca = pembaca

    def simpan(self, nim, daftar_kode, tgl_pinjam, batas_kembali):
        for _ in range(self.MAKS_PERCOBAAN):
            try:
                return self._simpan_sekali(nim, daftar_kode, tgl_pinjam, batas_kembali)
            except DataGandaError:
                continue  # ID sudah dipakai anggota lain, coba lagi dengan ID baru
        raise AturanBisnisError("Sistem sedang sibuk, silakan coba lagi.")

    def _simpan_sekali(self, nim, daftar_kode, tgl_pinjam, batas_kembali):
        with self._db.transaksi() as trx:
            self._kunci_mahasiswa(trx, nim)
            id_baru = self._buat_id(trx)
            trx.execute(
                "INSERT INTO transaksi (id, nim, tgl_pinjam, batas_kembali, status)"
                " VALUES (%s, %s, %s, %s, %s)",
                (id_baru, nim, tgl_pinjam, batas_kembali, StatusTransaksi.DIPINJAM),
            )
            for kode in sorted(daftar_kode):
                self._pinjam_alat(trx, id_baru, kode)
            return id_baru

    @staticmethod
    def _kunci_mahasiswa(trx, nim):
        mahasiswa = trx.fetch_one(
            "SELECT nim FROM mahasiswa WHERE nim = %s AND dihapus = FALSE FOR UPDATE",
            (nim,),
        )
        if mahasiswa is None:
            raise AturanBisnisError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        aktif = trx.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM transaksi WHERE nim = %s AND status <> %s",
            (nim, StatusTransaksi.SELESAI),
        )
        if aktif["jumlah"] >= Mahasiswa.MAKS_TRANSAKSI_AKTIF:
            raise AturanBisnisError(
                f"Sudah mencapai batas {Mahasiswa.MAKS_TRANSAKSI_AKTIF} transaksi aktif."
            )

    @staticmethod
    def _buat_id(trx):
        baris = trx.fetch_one(
            "SELECT MAX(CAST(SUBSTRING(id, 2) AS UNSIGNED)) AS nomor FROM transaksi"
        )
        return f"T{(baris['nomor'] or 0) + 1:03d}"

    @staticmethod
    def _pinjam_alat(trx, id_transaksi, kode):
        jumlah = trx.execute(
            "UPDATE alat SET status = %s WHERE kode = %s AND status = %s AND dihapus = FALSE",
            (StatusAlat.DIPINJAM, kode, StatusAlat.TERSEDIA),
        )
        if jumlah != 1:
            raise AturanBisnisError(f"Alat {kode} baru saja tidak tersedia.")
        trx.execute(
            "INSERT INTO detail_transaksi (id_transaksi, kode_alat, status) VALUES (%s, %s, %s)",
            (id_transaksi, kode, StatusItem.DIPINJAM),
        )

    def daftar_transaksi(self):
        return self._pembaca.daftar_transaksi()
