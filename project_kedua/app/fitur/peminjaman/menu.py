from app import ui
from app.models import Transaksi

class PeminjamanMenu:

    def __init__(self, service):
        self._service = service

    def buat_transaksi(self):
        # Tampilkan alat yang tersedia agar user tahu kode yang boleh dipilih
        tersedia = self._service.daftar_alat_tersedia()
        ui.tabel(
            ["Kode", "Nama", "Kategori"],
            [[a.kode, a.nama, a.kategori] for a in tersedia],
        )

        nim = ui.input_wajib("NIM mahasiswa").upper()
        teks = ui.input_wajib("Kode alat (pisahkan dengan koma)")
        # Pecah teks pada koma, buang spasi, jadikan huruf besar, abaikan yang kosong
        daftar_kode = [k.strip().upper() for k in teks.split(",") if k.strip()]
        lama_hari = ui.input_angka("Lama pinjam (hari)", 1, Transaksi.MAKS_HARI)

        id_transaksi = self._service.buat_transaksi(nim, daftar_kode, lama_hari)
        ui.sukses(f"Transaksi {id_transaksi} berhasil dibuat.")

    def tampilkan_transaksi(self):
        daftar = self._service.daftar_transaksi()
        if not daftar:
            ui.info("Belum ada transaksi.")
            return

        for t in daftar:
            penanda = "  [TERLAMBAT]" if t.terlambat() else ""
            print(f"\n{t.id_transaksi} | {t.nim} - {t.nama_mahasiswa}")
            print(
                f"Pinjam: {t.tgl_pinjam} | Batas kembali: {t.batas_kembali}"
                f" | Status: {t.status.value}{penanda}"
            )
            ui.tabel(
                ["Kode", "Nama alat", "Status", "Kondisi kembali", "Tgl kembali"],
                [
                    [
                        i.kode_alat,
                        i.nama_alat,
                        i.status.value,
                        i.kondisi_kembali.value if i.kondisi_kembali else None,
                        i.tgl_kembali,
                    ]
                    for i in t.daftar_item
                ],
            )
