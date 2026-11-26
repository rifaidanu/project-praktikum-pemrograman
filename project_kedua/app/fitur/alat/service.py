"""Service alat: validasi dan aturan bisnis (Aturan 1, 5, 6, 7, 8).
Tidak ada input()/print() dan tidak menyentuh file; penyimpanan lewat repository."""
from app.models.alat import Alat, KondisiAlat, StatusAlat
from app.errors import (ValidasiError, DataTidakDitemukanError,
                        DataDuplikatError, AturanBisnisError)


def _bersihkan(teks, label):
    """Teks bebas tidak boleh kosong dan tidak boleh merusak format file."""
    teks = (teks or "").strip()
    if not teks:
        raise ValidasiError(f"{label} tidak boleh kosong")
    if "|" in teks or "\n" in teks or "\r" in teks:
        raise ValidasiError(f"{label} tidak boleh mengandung karakter '|' atau baris baru")
    return teks


def _ke_kondisi(nilai):
    """Terima KondisiAlat atau string ('baik', 'rusak ringan', 'rusak berat')."""
    if isinstance(nilai, KondisiAlat):
        return nilai
    try:
        return KondisiAlat(str(nilai).strip().lower())
    except ValueError:
        raise ValidasiError("Kondisi harus: " + ", ".join(k.value for k in KondisiAlat))


def _status_untuk(kondisi):
    return StatusAlat.TERSEDIA if kondisi is KondisiAlat.BAIK else StatusAlat.TIDAK_TERSEDIA


def _salin(alat, **ubah):
    data = dict(kode=alat.kode, nama=alat.nama, kategori=alat.kategori,
                kondisi=alat.kondisi, status=alat.status)
    data.update(ubah)
    return Alat(**data)


class AlatService:
    def __init__(self, repo, alat_dipakai=None):
        self._repo = repo
        self._alat_dipakai = alat_dipakai

    def pasang_pemeriksa(self, alat_dipakai):
        """alat_dipakai(kode, hanya_aktif) -> bool, disediakan modul peminjaman.
        Dipasang lewat sini bila service peminjaman baru dibuat setelah service alat."""
        self._alat_dipakai = alat_dipakai

    def ambil(self, kode):
        alat = self._repo.get((kode or "").strip().upper())
        if alat is None:
            raise DataTidakDitemukanError(f"Alat dengan kode '{kode}' tidak ditemukan")
        return alat

    def tambah(self, kode, nama, kategori, kondisi=KondisiAlat.BAIK):
        kode = _bersihkan(kode, "Kode").upper()
        nama = _bersihkan(nama, "Nama")
        kategori = _bersihkan(kategori, "Kategori").lower()
        kondisi = _ke_kondisi(kondisi)
        if self._repo.ada(kode):
            raise DataDuplikatError(f"Kode alat '{kode}' sudah terdaftar")
        alat = Alat(kode, nama, kategori, kondisi, _status_untuk(kondisi))
        self._repo.simpan(alat)
        return alat

    def edit(self, kode, nama=None, kategori=None, kondisi=None):
        lama = self.ambil(kode)
        nama = _bersihkan(nama, "Nama") if nama else lama.nama
        kategori = _bersihkan(kategori, "Kategori").lower() if kategori else lama.kategori
        kondisi = _ke_kondisi(kondisi) if kondisi else lama.kondisi
        if lama.status is StatusAlat.DIPINJAM:
            if kondisi is not lama.kondisi:
                raise AturanBisnisError(
                    "Kondisi alat yang sedang dipinjam hanya bisa berubah lewat pengembalian")
            status = StatusAlat.DIPINJAM
        else:
            status = _status_untuk(kondisi)
        baru = _salin(lama, nama=nama, kategori=kategori, kondisi=kondisi, status=status)
        self._repo.simpan(baru)
        return baru

    def hapus(self, kode):
        alat = self.ambil(kode)
        if self._alat_dipakai is None:
            raise AturanBisnisError("Pemeriksaan transaksi belum dipasang, penghapusan ditolak")
        if self._alat_dipakai(alat.kode, True):
            raise AturanBisnisError("Alat masih ada di transaksi aktif, tidak boleh dihapus")
        if self._alat_dipakai(alat.kode, False):
            raise AturanBisnisError("Alat tercatat di riwayat transaksi, tidak boleh dihapus "
                                    "(agar kode alat di transaksi.txt tetap valid)")
        self._repo.hapus(alat.kode)

    def daftar(self):
        return self._repo.semua()

    def cari(self, kata):
        """Tantangan A: kode, sebagian nama, atau kategori."""
        kata = (kata or "").strip().lower()
        if not kata:
            raise ValidasiError("Kata kunci tidak boleh kosong")
        return [a for a in self._repo.semua()
                if kata in a.kode.lower() or kata in a.nama.lower() or kata in a.kategori]

    def daftar_tersedia(self):
        return [a for a in self._repo.semua() if a.status is StatusAlat.TERSEDIA]

    def daftar_dipinjam(self):
        return [a for a in self._repo.semua() if a.status is StatusAlat.DIPINJAM]

    def daftar_rusak(self):
        return [a for a in self._repo.semua() if a.kondisi is not KondisiAlat.BAIK]

    def pastikan_tersedia(self, daftar_kode):
        """Aturan 1."""
        for kode in daftar_kode:
            alat = self.ambil(kode)
            if alat.status is not StatusAlat.TERSEDIA:
                raise AturanBisnisError(
                    f"Alat {alat.kode} ({alat.nama}) tidak tersedia (status: {alat.status.value})")

    def tandai_dipinjam(self, daftar_kode):
        """Atomik: semua divalidasi dulu; bila satu gagal, tidak ada yang berubah."""
        kode_unik = list(dict.fromkeys(self.ambil(k).kode for k in daftar_kode))
        if not kode_unik:
            raise ValidasiError("Pilih minimal satu alat")
        self.pastikan_tersedia(kode_unik)
        self._repo.simpan(*[_salin(self.ambil(k), status=StatusAlat.DIPINJAM) for k in kode_unik])

    def tandai_kembali(self, kondisi_per_kode):
        """{kode: kondisi}. Aturan 5: baik -> tersedia; rusak -> tidak tersedia."""
        if not kondisi_per_kode:
            raise ValidasiError("Tidak ada alat yang dikembalikan")
        baru = []
        for kode, kondisi in kondisi_per_kode.items():
            alat = self.ambil(kode)
            if alat.status is not StatusAlat.DIPINJAM:
                raise AturanBisnisError(f"Alat {alat.kode} tidak sedang dipinjam")
            kondisi = _ke_kondisi(kondisi)
            baru.append(_salin(alat, kondisi=kondisi, status=_status_untuk(kondisi)))
        self._repo.simpan(*baru)