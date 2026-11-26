from datetime import date, datetime
from typing import Dict, List, Optional, Set

from models.enums import KondisiAlat, StatusAlat, StatusTransaksi
from models.mahasiswa import Mahasiswa
from models.peralatan import Peralatan
from models.transaksi import ItemPeminjaman, Transaksi
from services.penyimpanan_txt import PEMISAH, PenyimpananTxt


class LabManager:
    """Pusat data dan pengatur logika bisnis sistem laboratorium."""

    def __init__(self, folder_data: Optional[str] = None) -> None:
        self._mahasiswa: Dict[str, Mahasiswa] = {}   # nim -> Mahasiswa
        self._alat: Dict[str, Peralatan] = {}        # kode_alat -> Peralatan
        self._transaksi: Dict[str, Transaksi] = {}   # id_transaksi -> Transaksi
        self._kategori: Set[str] = set()
        self._log: List[dict] = []

        # Tanpa folder_data, LabManager hanya bekerja di memori (berguna untuk pengujian)
        self._penyimpanan: Optional[PenyimpananTxt] = (
            PenyimpananTxt(folder_data) if folder_data else None
        )

    # ==================== PROPERTIES ====================
    @property
    def mahasiswa(self) -> Dict[str, Mahasiswa]:
        return self._mahasiswa

    @property
    def alat(self) -> Dict[str, Peralatan]:
        return self._alat

    @property
    def transaksi(self) -> Dict[str, Transaksi]:
        return self._transaksi

    @property
    def kategori(self) -> Set[str]:
        return self._kategori

    @property
    def log(self) -> List[dict]:
        return self._log

    # ==================== LOGGING ====================
    def catat_log(self, pesan: str) -> None:
        """Mencatat aktivitas ke dalam list log."""
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log.append({"waktu": waktu, "pesan": pesan})
        if self._penyimpanan:
            self._penyimpanan.tambah_log(waktu, pesan)

    # ==================== FILE HANDLING (.txt) ====================
    def muat_data(self) -> bool:
        """Memuat seluruh data dari file .txt ke Dictionary.

        Mengembalikan False jika file belum ada (program baru pertama kali dijalankan).
        """
        if not self._penyimpanan or not self._penyimpanan.sudah_ada_data():
            return False
        p = self._penyimpanan

        for b in p.baca(p.FILE_MAHASISWA):
            self._mahasiswa[b["nim"]] = Mahasiswa(b["nim"], b["nama"], b["nomor_hp"])

        for b in p.baca(p.FILE_ALAT):
            unit = Peralatan(b["kode_alat"], b["nama"], b["kategori"], KondisiAlat(b["kondisi"]))
            unit.status = StatusAlat(b["status"])   # status disimpan apa adanya (bisa DIPINJAM)
            self._alat[unit.kode_alat] = unit
            self._kategori.add(unit.kategori)

        # Kelompokkan detail per id_transaksi: {id_transaksi: [baris, baris, ...]}
        detail_per_transaksi: Dict[str, List[dict]] = {}
        for b in p.baca(p.FILE_DETAIL):
            detail_per_transaksi.setdefault(b["id_transaksi"], []).append(b)

        for b in p.baca(p.FILE_TRANSAKSI):
            # Mahasiswa yang sudah dihapus tetap ditampilkan di riwayat transaksi lamanya
            mhs = self._mahasiswa.get(b["nim"]) or Mahasiswa(b["nim"], b["nama_mahasiswa"], "-")
            items = [self._item_dari_baris(d) for d in detail_per_transaksi.get(b["id_transaksi"], [])]
            trx = Transaksi(
                b["id_transaksi"], mhs, items,
                date.fromisoformat(b["tgl_pinjam"]), date.fromisoformat(b["batas_kembali"]),
            )
            trx.hitung_status()   # status dihitung ulang dari item, tidak perlu disimpan
            if trx.masih_aktif():
                mhs.tambah_transaksi_aktif(trx)
            self._transaksi[trx.id_transaksi] = trx

        self._log = p.baca(p.FILE_LOG)
        return True

    def _item_dari_baris(self, b: dict) -> ItemPeminjaman:
        """Membuat ItemPeminjaman dari satu baris detail_transaksi.txt."""
        alat = self._alat.get(b["kode_alat"])
        if alat is None:
            # Alat sudah dihapus, tapi masih tercatat di riwayat transaksi yang selesai
            alat = Peralatan(b["kode_alat"], b["nama_alat"], b["kategori"])
            alat.status = StatusAlat.TIDAK_TERSEDIA
        sudah_kembali = b["sudah_kembali"] == "1"
        return ItemPeminjaman(
            alat,
            sudah_kembali,
            date.fromisoformat(b["tgl_kembali"]) if sudah_kembali else None,
            KondisiAlat(b["kondisi_kembali"]) if sudah_kembali else None,
        )

    def simpan_data(self) -> None:
        """Menulis ulang seluruh isi Dictionary ke file .txt."""
        if not self._penyimpanan:
            return
        p = self._penyimpanan

        p.tulis(p.FILE_MAHASISWA, [
            [m.nim, m.nama, m.nomor_hp] for m in self._mahasiswa.values()
        ])
        p.tulis(p.FILE_ALAT, [
            [a.kode_alat, a.nama, a.kategori, a.kondisi.value, a.status.value]
            for a in self._alat.values()
        ])
        p.tulis(p.FILE_TRANSAKSI, [
            [t.id_transaksi, t.mahasiswa.nim, t.mahasiswa.nama,
             t.tanggal_peminjaman.isoformat(), t.batas_pengembalian.isoformat()]
            for t in self._transaksi.values()
        ])
        p.tulis(p.FILE_DETAIL, [
            [t.id_transaksi, i.alat.kode_alat, i.alat.nama, i.alat.kategori,
             "1" if i.sudah_kembali else "0",
             i.tanggal_kembali.isoformat() if i.tanggal_kembali else "-",
             i.kondisi_kembali.value if i.kondisi_kembali else "-"]
            for t in self._transaksi.values() for i in t.daftar_item
        ])

    @staticmethod
    def _cek_teks(**isian: Optional[str]) -> None:
        """Menolak teks kosong atau yang mengandung karakter pemisah file ('|')."""
        for label, nilai in isian.items():
            if nilai is None:
                continue
            if not nilai.strip():
                raise ValueError(f"{label} tidak boleh kosong.")
            if PEMISAH in nilai:
                raise ValueError(f"{label} tidak boleh mengandung karakter '{PEMISAH}'.")

    # ==================== KELOLA MAHASISWA ====================
    def tambah_mahasiswa(self, nim: str, nama: str, nomor_hp: str) -> Mahasiswa:
        self._cek_teks(NIM=nim, Nama=nama, Nomor_HP=nomor_hp)
        if nim in self._mahasiswa:
            raise ValueError(f"Mahasiswa dengan NIM '{nim}' sudah terdaftar.")
        mhs = Mahasiswa(nim, nama, nomor_hp)
        self._mahasiswa[nim] = mhs
        self.simpan_data()
        self.catat_log(f"Tambah mahasiswa: {nim} - {nama}")
        return mhs

    def edit_mahasiswa(self, nim: str, nama: Optional[str] = None, nomor_hp: Optional[str] = None) -> Mahasiswa:
        if nim not in self._mahasiswa:
            raise ValueError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        self._cek_teks(Nama=nama or None, Nomor_HP=nomor_hp or None)
        mhs = self._mahasiswa[nim]
        if nama is not None and nama.strip():
            mhs.nama = nama
        if nomor_hp is not None and nomor_hp.strip():
            mhs.nomor_hp = nomor_hp
        self.simpan_data()
        self.catat_log(f"Edit mahasiswa: {nim}")
        return mhs

    def hapus_mahasiswa(self, nim: str) -> None:
        if nim not in self._mahasiswa:
            raise ValueError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        mhs = self._mahasiswa[nim]
        if mhs.punya_peminjaman_aktif():
            raise ValueError("Tidak dapat menghapus: Mahasiswa masih memiliki transaksi peminjaman aktif.")
        del self._mahasiswa[nim]
        self.simpan_data()
        self.catat_log(f"Hapus mahasiswa: {nim}")

    def cari_mahasiswa(self, keyword: str) -> List[Mahasiswa]:
        keyword = keyword.lower()
        return [
            m for m in self._mahasiswa.values()
            if keyword in m.nim.lower() or keyword in m.nama.lower()
        ]

    # ==================== KELOLA ALAT ====================
    def tambah_kategori(self, nama_kategori: str) -> None:
        kat = nama_kategori.strip()
        if kat:
            self._kategori.add(kat)

    def tambah_alat(
        self,
        kode_alat: str,
        nama: str,
        kategori: str,
        kondisi: KondisiAlat = KondisiAlat.BAIK
    ) -> Peralatan:
        self._cek_teks(Kode_alat=kode_alat, Nama_alat=nama, Kategori=kategori)
        if kode_alat in self._alat:
            raise ValueError(f"Alat dengan kode '{kode_alat}' sudah terdaftar.")
        self.tambah_kategori(kategori)
        unit = Peralatan(kode_alat, nama, kategori, kondisi)
        self._alat[kode_alat] = unit
        self.simpan_data()
        self.catat_log(f"Tambah alat: {kode_alat} - {nama} ({kategori})")
        return unit

    def edit_alat(
        self,
        kode_alat: str,
        nama: Optional[str] = None,
        kategori: Optional[str] = None,
        kondisi: Optional[KondisiAlat] = None
    ) -> Peralatan:
        if kode_alat not in self._alat:
            raise ValueError(f"Alat dengan kode '{kode_alat}' tidak ditemukan.")
        self._cek_teks(Nama_alat=nama or None, Kategori=kategori or None)
        unit = self._alat[kode_alat]
        if nama is not None and nama.strip():
            unit.nama = nama
        if kategori is not None and kategori.strip():
            unit.kategori = kategori
            self.tambah_kategori(kategori)
        if kondisi is not None:
            unit.kondisi = kondisi
            if not unit.sedang_dipinjam():
                unit.status = StatusAlat.TERSEDIA if kondisi == KondisiAlat.BAIK else StatusAlat.TIDAK_TERSEDIA
        self.simpan_data()
        self.catat_log(f"Edit alat: {kode_alat}")
        return unit

    def hapus_alat(self, kode_alat: str) -> None:
        if kode_alat not in self._alat:
            raise ValueError(f"Alat dengan kode '{kode_alat}' tidak ditemukan.")
        if self._alat_dipakai_transaksi_aktif(kode_alat):
            raise ValueError("Tidak dapat menghapus: Alat masih tercatat dalam transaksi yang sedang aktif.")
        del self._alat[kode_alat]
        self.simpan_data()
        self.catat_log(f"Hapus alat: {kode_alat}")

    def cari_alat(self, keyword: str) -> List[Peralatan]:
        keyword = keyword.lower()
        return [
            a for a in self._alat.values()
            if keyword in a.kode_alat.lower() or keyword in a.nama.lower() or keyword in a.kategori.lower()
        ]

    def _alat_dipakai_transaksi_aktif(self, kode_alat: str) -> bool:
        """Memeriksa apakah alat masih ada di dalam transaksi yang belum selesai."""
        for t in self._transaksi.values():
            if t.masih_aktif():
                for item in t.daftar_item:
                    if item.alat.kode_alat == kode_alat:
                        return True
        return False

    # ==================== KELOLA TRANSAKSI ====================
    def buat_transaksi(self, nim: str, daftar_kode_alat: List[str], batas: date) -> Transaksi:
        # --- Fase 1: Validasi (tanpa mengubah data apa pun) ---
        if nim not in self._mahasiswa:
            raise ValueError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        mhs = self._mahasiswa[nim]
        if not mhs.boleh_meminjam():
            raise ValueError(f"Mahasiswa '{mhs.nama}' sudah mencapai batas maksimal {Mahasiswa.MAKS_TRANSAKSI_AKTIF} transaksi aktif.")
        if not daftar_kode_alat:
            raise ValueError("Daftar alat tidak boleh kosong.")
        if len(set(daftar_kode_alat)) != len(daftar_kode_alat):
            raise ValueError("Ada kode alat yang dipilih lebih dari satu kali.")

        for kode in daftar_kode_alat:
            if kode not in self._alat:
                raise ValueError(f"Alat dengan kode '{kode}' tidak ditemukan.")
            if not self._alat[kode].tersedia():
                raise ValueError(f"Alat '{self._alat[kode].nama}' ({kode}) tidak tersedia untuk dipinjam (Status: {self._alat[kode].status.value}).")

        # --- Fase 2: Eksekusi Perubahan Data ---
        items = [ItemPeminjaman(self._alat[k]) for k in daftar_kode_alat]
        id_baru = f"T{len(self._transaksi) + 1:03d}"
        transaksi = Transaksi(id_baru, mhs, items, date.today(), batas)

        if not transaksi.validasi_batas():
            raise ValueError("Batas pengembalian tidak valid (maksimal 7 hari dari hari ini).")

        for item in items:
            item.alat.tandai_dipinjam()

        mhs.tambah_transaksi_aktif(transaksi)
        self._transaksi[id_baru] = transaksi
        self.simpan_data()
        self.catat_log(f"Buat transaksi {id_baru} untuk NIM {nim} ({len(items)} alat)")
        return transaksi

    def proses_pengembalian(self, id_transaksi: str, kode_alat: str, kondisi: KondisiAlat) -> Transaksi:
        if id_transaksi not in self._transaksi:
            raise ValueError(f"Transaksi dengan ID '{id_transaksi}' tidak ditemukan.")
        transaksi = self._transaksi[id_transaksi]
        if not transaksi.masih_aktif():
            raise ValueError(f"Transaksi '{id_transaksi}' sudah berstatus SELESAI.")

        transaksi.kembalikan_alat(kode_alat, kondisi, date.today())
        self.simpan_data()
        self.catat_log(f"Pengembalian alat {kode_alat} pada transaksi {id_transaksi} (Kondisi: {kondisi.value})")
        if not transaksi.masih_aktif():
            self.catat_log(f"Transaksi {id_transaksi} selesai")
        return transaksi

    def tampilkan_transaksi(self) -> List[Transaksi]:
        """Mengembalikan semua transaksi yang tercatat."""
        return list(self._transaksi.values())

    def cari_transaksi_by_mahasiswa(self, nim: str) -> List[Transaksi]:
        """Mencari transaksi aktif maupun selesai milik mahasiswa tertentu."""
        return [t for t in self._transaksi.values() if t.mahasiswa.nim == nim]

    def riwayat_mahasiswa(self, nim: str) -> List[Transaksi]:
        """Alias / fungsi untuk melihat seluruh riwayat peminjaman mahasiswa."""
        if nim not in self._mahasiswa:
            raise ValueError(f"Mahasiswa dengan NIM '{nim}' tidak ditemukan.")
        return self.cari_transaksi_by_mahasiswa(nim)

    # ==================== TAMPILAN & FILTER ALAT ====================
    def tampilkan_alat_tersedia(self) -> List[Peralatan]:
        return [a for a in self._alat.values() if a.status == StatusAlat.TERSEDIA]

    def tampilkan_alat_dipinjam(self) -> List[Peralatan]:
        return [a for a in self._alat.values() if a.status == StatusAlat.DIPINJAM]

    def tampilkan_alat_rusak(self) -> List[Peralatan]:
        return [
            a for a in self._alat.values()
            if a.kondisi in (KondisiAlat.RUSAK_RINGAN, KondisiAlat.RUSAK_BERAT)
        ]
