"""Repository alat: dict di memori + sinkron ke alat.txt lewat FileStorage.
Hanya urusan data: tidak ada aturan bisnis, input(), atau print() selain peringatan muat."""
from app.models.alat import Alat, KondisiAlat, StatusAlat
from app.errors import AppError, ValidasiError, PenyimpananError


class AlatRepository:
    FILE = "alat.txt"   # format: kode|nama|kategori|kondisi|status
    KOLOM = 5

    def __init__(self, storage):
        self._storage = storage
        self._data = {}  # {kode: Alat}
        self._muat()

    @staticmethod
    def _dari_baris(kolom):
        kode, nama, kategori, kondisi, status = kolom
        kode = kode.upper()
        if not kode or not nama or not kategori:
            raise ValidasiError("kode, nama, atau kategori kosong")
        try:
            kondisi = KondisiAlat(kondisi)
            status = StatusAlat(status)
        except ValueError:
            raise ValidasiError(f"kondisi/status tidak dikenal ('{kondisi}', '{status}')")
        if status is StatusAlat.TERSEDIA and kondisi is not KondisiAlat.BAIK:
            raise ValidasiError("alat rusak tidak boleh berstatus tersedia")
        return Alat(kode, nama, kategori.lower(), kondisi, status)

    @staticmethod
    def _ke_baris(alat):
        return [alat.kode, alat.nama, alat.kategori, alat.kondisi.value, alat.status.value]

    def _muat(self):
        for kolom in self._storage.load(self.FILE, self.KOLOM):
            try:
                alat = self._dari_baris(kolom)
            except AppError as e:
                print(f"[PERINGATAN] {self.FILE}: baris '{'|'.join(kolom)}' dilewati ({e})")
                continue
            if alat.kode in self._data:
                print(f"[PERINGATAN] {self.FILE}: kode ganda {alat.kode} dilewati")
                continue
            self._data[alat.kode] = alat

    def _komit(self, data_baru):
        """Tulis dulu ke file; memori baru diganti hanya jika file berhasil ditulis
        (Aturan 7: data program dan file selalu sama)."""
        baris = [self._ke_baris(a) for a in data_baru.values()]
        if not self._storage.save(self.FILE, baris):
            raise PenyimpananError("Gagal menyimpan ke alat.txt, perubahan dibatalkan")
        self._data = data_baru


        return sorted(self._data.values(), key=lambda a: a.kode)

    def get(self, kode):
        return self._data.get(kode)

    def ada(self, kode):
        return kode in self._data

    def simpan(self, *daftar_alat):
        """Tambah atau ganti satu/lebih alat sekaligus (atomik, satu kali tulis file)."""
        data_baru = dict(self._data)
        for alat in daftar_alat:
            data_baru[alat.kode] = alat
        self._komit(data_baru)

    def hapus(self, kode):
        data_baru = dict(self._data)
        del data_baru[kode]
        self._komit(data_baru)