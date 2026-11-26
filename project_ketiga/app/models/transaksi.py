from datetime import date

from app.models.enums import KondisiAlat, StatusItem, StatusTransaksi


class ItemPeminjaman:
    """Satu alat di dalam transaksi (satu baris tabel detail_transaksi)."""

    def __init__(self, kode_alat, nama_alat, status=StatusItem.DIPINJAM,
                 kondisi_kembali=None, tgl_kembali=None):
        self.kode_alat = kode_alat
        self.nama_alat = nama_alat
        self.status = status
        self.kondisi_kembali = kondisi_kembali
        self.tgl_kembali = tgl_kembali

    @classmethod
    def dari_baris(cls, baris):
        """Membuat objek dari hasil query (dict)."""
        kondisi = baris["kondisi_kembali"]
        return cls(baris["kode_alat"], baris["nama_alat"], StatusItem(baris["status_item"]),
                   KondisiAlat(kondisi) if kondisi else None, baris["tgl_kembali"])

    def sudah_kembali(self):
        return self.status == StatusItem.DIKEMBALIKAN


class Transaksi:
    """Satu transaksi peminjaman beserta daftar alatnya."""

    MAKS_HARI = 7

    def __init__(self, id_transaksi, nim, nama_mahasiswa, tgl_pinjam, batas_kembali,
                 status=StatusTransaksi.DIPINJAM, daftar_item=None):
        self.id_transaksi = id_transaksi
        self.nim = nim
        self.nama_mahasiswa = nama_mahasiswa
        self.tgl_pinjam = tgl_pinjam
        self.batas_kembali = batas_kembali
        self.status = status
        self.daftar_item = daftar_item if daftar_item is not None else []

    @classmethod
    def dari_baris(cls, baris):
        """Membuat transaksi dengan daftar item masih kosong."""
        return cls(baris["id"], baris["nim"], baris["nama_mahasiswa"], baris["tgl_pinjam"],
                   baris["batas_kembali"], StatusTransaksi(baris["status"]))

    def masih_aktif(self):
        return self.status != StatusTransaksi.SELESAI

    def item_belum_kembali(self):
        return [item for item in self.daftar_item if not item.sudah_kembali()]

    def terlambat(self):
        return self.masih_aktif() and date.today() > self.batas_kembali
