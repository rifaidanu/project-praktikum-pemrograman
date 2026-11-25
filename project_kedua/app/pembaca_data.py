"""Pembacaan data yang dipakai lintas fitur, agar satu paket tidak menunggu paket lain."""
from app.models import Alat, ItemPeminjaman, Mahasiswa, StatusAlat, StatusTransaksi, Transaksi


class PembacaData:
    """Hanya membaca (SELECT). Tidak pernah mengubah data."""

    def __init__(self, db):
        self._db = db

    def ambil_mahasiswa(self, nim, termasuk_dihapus=False):
        """Objek Mahasiswa, atau None jika tidak ada."""
        baris = self._db.fetch_one(
            "SELECT * FROM mahasiswa WHERE nim = %s AND (dihapus = FALSE OR %s)",
            (nim, termasuk_dihapus),
        )
        return Mahasiswa.dari_baris(baris) if baris else None

    def ambil_alat(self, kode, termasuk_dihapus=False):
        """Objek Alat, atau None jika tidak ada."""
        baris = self._db.fetch_one(
            "SELECT * FROM alat WHERE kode = %s AND (dihapus = FALSE OR %s)",
            (kode, termasuk_dihapus),
        )
        return Alat.dari_baris(baris) if baris else None

    def daftar_alat_tersedia(self):
        """List objek Alat yang siap dipinjam."""
        baris = self._db.fetch_all(
            "SELECT * FROM alat WHERE status = %s AND dihapus = FALSE ORDER BY kode",
            (StatusAlat.TERSEDIA,),
        )
        return [Alat.dari_baris(b) for b in baris]

    def ambil_transaksi(self, id_transaksi):
        """Objek Transaksi lengkap dengan itemnya, atau None jika tidak ada."""
        hasil = self.daftar_transaksi("t.id = %s", (id_transaksi,))
        return hasil[0] if hasil else None

    def daftar_transaksi(self, kondisi="TRUE", params=()):
        """List objek Transaksi lengkap dengan itemnya, hanya dengan satu query.

        `kondisi` adalah isi WHERE yang ditulis di repository, BUKAN input user. Input user
        masuk lewat `params`. Pakai kolom tabel t (transaksi) atau m (mahasiswa) saja, misal:
            daftar_transaksi("t.nim = %s", (nim,))
        """
        baris = self._db.fetch_all(
            "SELECT t.id, t.nim, m.nama AS nama_mahasiswa, t.tgl_pinjam, t.batas_kembali,"
            " t.status, d.kode_alat, a.nama AS nama_alat, d.status AS status_item,"
            " d.kondisi_kembali, d.tgl_kembali"
            " FROM transaksi t"
            " JOIN mahasiswa m ON m.nim = t.nim"
            " JOIN detail_transaksi d ON d.id_transaksi = t.id"
            " JOIN alat a ON a.kode = d.kode_alat"
            f" WHERE {kondisi}"
            " ORDER BY t.tgl_pinjam, t.id, d.kode_alat",
            params,
        )
        return self._susun_transaksi(baris)

    @staticmethod
    def _susun_transaksi(daftar_baris):
        """Mengelompokkan baris hasil JOIN menjadi objek Transaksi."""
        hasil = {}
        for baris in daftar_baris:
            if baris["id"] not in hasil:
                hasil[baris["id"]] = Transaksi.dari_baris(baris)
            hasil[baris["id"]].daftar_item.append(ItemPeminjaman.dari_baris(baris))
        return list(hasil.values())

    def hitung_transaksi_aktif(self, nim):
        """Jumlah transaksi mahasiswa yang belum selesai (Aturan 2 dan 6)."""
        baris = self._db.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM transaksi WHERE nim = %s AND status <> %s",
            (nim, StatusTransaksi.SELESAI),
        )
        return baris["jumlah"]

    def alat_di_transaksi_aktif(self, kode):
        """True jika alat tercatat di transaksi yang belum selesai (Aturan 6).

        Termasuk alat yang sudah kembali, selama transaksinya sendiri belum selesai.
        """
        baris = self._db.fetch_one(
            "SELECT COUNT(*) AS jumlah FROM detail_transaksi d"
            " JOIN transaksi t ON t.id = d.id_transaksi"
            " WHERE d.kode_alat = %s AND t.status <> %s",
            (kode, StatusTransaksi.SELESAI),
        )
        return baris["jumlah"] > 0
