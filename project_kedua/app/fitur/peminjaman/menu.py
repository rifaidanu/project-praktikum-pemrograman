"""Paket 3. Input dan tampilan peminjaman (menu 3 dan 4)."""
from app import ui
from app.models import Transaksi


class PeminjamanMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def buat_transaksi(self):
        """Menu 3: Buat transaksi peminjaman."""
        daftar_alat = self._service.daftar_alat_tersedia()
        if not daftar_alat:
            ui.info("Tidak ada alat yang tersedia.")
            return
        ui.tabel(
            ["Kode", "Nama", "Kategori"],
            [[a.kode, a.nama, a.kategori] for a in daftar_alat],
        )
        nim = ui.input_wajib("NIM").upper()
        teks = ui.input_wajib("Kode alat (pisahkan dengan koma)")
        daftar_kode = [k.strip().upper() for k in teks.split(",") if k.strip()]
        lama_hari = ui.input_angka("Lama pinjam (hari)", 1, Transaksi.MAKS_HARI)
        id_transaksi = self._service.buat_transaksi(nim, daftar_kode, lama_hari)
        ui.sukses(f"Peminjaman berhasil. ID transaksi: {id_transaksi}")

    def tampilkan_transaksi(self):
        """Menu 4: Tampilkan transaksi."""
        daftar = self._service.daftar_transaksi()
        if not daftar:
            ui.info("Belum ada transaksi.")
            return
        for t in daftar:
            tanda = " [TERLAMBAT]" if t.terlambat() else ""
            print(
                f"\n[{t.id_transaksi}] {t.nama_mahasiswa} ({t.nim}) | Pinjam: {t.tgl_pinjam}"
                f" | Batas: {t.batas_kembali} | Status: {t.status.value}{tanda}"
            )
            ui.tabel(
                ["Kode", "Nama Alat", "Status", "Kondisi Kembali", "Tgl Kembali"],
                [
                    [
                        item.kode_alat,
                        item.nama_alat,
                        item.status.value,
                        item.kondisi_kembali.value if item.kondisi_kembali else None,
                        item.tgl_kembali,
                    ]
                    for item in t.daftar_item
                ],
            )
