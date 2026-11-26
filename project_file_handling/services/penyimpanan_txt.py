"""
Penyimpanan data ke file .txt (pengganti database).

Selama program berjalan, data tetap disimpan di Dictionary/List milik LabManager.
File .txt hanya dipakai untuk:
  - MEMUAT data saat program dibuka   (mode 'r')
  - MENYIMPAN data setiap ada perubahan (mode 'w')
  - MENAMBAH baris log aktivitas        (mode 'a')

Format setiap file: satu baris = satu data, kolom dipisah tanda '|'.
Baris yang diawali '#' adalah keterangan kolom dan diabaikan saat dibaca.

    data_txt/mahasiswa.txt         nim|nama|nomor_hp
    data_txt/alat.txt              kode_alat|nama|kategori|kondisi|status
    data_txt/transaksi.txt         id_transaksi|nim|nama_mahasiswa|tgl_pinjam|batas_kembali
    data_txt/detail_transaksi.txt  id_transaksi|kode_alat|nama_alat|kategori|sudah_kembali|tgl_kembali|kondisi_kembali
    data_txt/log.txt               waktu|pesan
"""
import os
from typing import Dict, List

PEMISAH = "|"


class PenyimpananTxt:
    """Membaca dan menulis data ke beberapa file .txt di dalam satu folder."""

    FILE_MAHASISWA = "mahasiswa.txt"
    FILE_ALAT = "alat.txt"
    FILE_TRANSAKSI = "transaksi.txt"
    FILE_DETAIL = "detail_transaksi.txt"
    FILE_LOG = "log.txt"

    KOLOM: Dict[str, List[str]] = {
        FILE_MAHASISWA: ["nim", "nama", "nomor_hp"],
        FILE_ALAT: ["kode_alat", "nama", "kategori", "kondisi", "status"],
        FILE_TRANSAKSI: ["id_transaksi", "nim", "nama_mahasiswa", "tgl_pinjam", "batas_kembali"],
        FILE_DETAIL: ["id_transaksi", "kode_alat", "nama_alat", "kategori",
                      "sudah_kembali", "tgl_kembali", "kondisi_kembali"],
        FILE_LOG: ["waktu", "pesan"],
    }

    def __init__(self, folder: str) -> None:
        self._folder = folder
        os.makedirs(self._folder, exist_ok=True)

    def _path(self, nama_file: str) -> str:
        return os.path.join(self._folder, nama_file)

    def sudah_ada_data(self) -> bool:
        """True jika file data utama sudah pernah dibuat (bukan pertama kali program dijalankan)."""
        return os.path.exists(self._path(self.FILE_MAHASISWA))

    # ==================== BACA ====================
    def baca(self, nama_file: str) -> List[Dict[str, str]]:
        """Membaca satu file .txt menjadi list of dict. File belum ada -> list kosong."""
        path = self._path(nama_file)
        if not os.path.exists(path):
            return []

        kolom = self.KOLOM[nama_file]
        hasil: List[Dict[str, str]] = []
        with open(path, "r", encoding="utf-8") as f:
            for nomor_baris, baris in enumerate(f, start=1):
                baris = baris.rstrip("\n")
                if not baris.strip() or baris.startswith("#"):
                    continue
                nilai = baris.split(PEMISAH, len(kolom) - 1)
                if len(nilai) != len(kolom):
                    print(f"[PERINGATAN] {nama_file} baris {nomor_baris} rusak, dilewati.")
                    continue
                hasil.append(dict(zip(kolom, nilai)))
        return hasil

    # ==================== TULIS ====================
    def tulis(self, nama_file: str, daftar_baris: List[List[str]]) -> None:
        """Menimpa seluruh isi file dengan data terbaru.

        Data ditulis ke file sementara (.tmp) dulu, lalu menggantikan file asli,
        sehingga file tidak rusak setengah jalan jika program tiba-tiba berhenti.
        """
        path = self._path(nama_file)
        path_tmp = path + ".tmp"
        with open(path_tmp, "w", encoding="utf-8") as f:
            f.write("# " + PEMISAH.join(self.KOLOM[nama_file]) + "\n")
            for baris in daftar_baris:
                f.write(PEMISAH.join(str(n) for n in baris) + "\n")
        os.replace(path_tmp, path)

    def tambah_log(self, waktu: str, pesan: str) -> None:
        """Menambahkan satu baris log di akhir file (mode append)."""
        path = self._path(self.FILE_LOG)
        file_baru = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as f:
            if file_baru:
                f.write("# " + PEMISAH.join(self.KOLOM[self.FILE_LOG]) + "\n")
            f.write(f"{waktu}{PEMISAH}{pesan}\n")
