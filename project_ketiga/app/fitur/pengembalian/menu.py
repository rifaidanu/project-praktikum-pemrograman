"""Paket 4. Input dan tampilan pengembalian (menu 5 dan 6)."""
from app import ui
from app.models import KondisiAlat


class PengembalianMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def proses_pengembalian(self):
        """Menu 5: Proses pengembalian alat."""
        id_transaksi = ui.input_wajib("ID transaksi").upper()
        transaksi = self._service.ambil_transaksi_aktif(id_transaksi)

        print(f"\n{transaksi.id_transaksi} | {transaksi.nim} - {transaksi.nama_mahasiswa}"
              f" | Batas kembali: {transaksi.batas_kembali}")
        ui.tabel(
            ["Kode", "Nama alat"],
            [[i.kode_alat, i.nama_alat] for i in transaksi.item_belum_kembali()],
        )

        teks = ui.input_wajib("Kode alat yang dikembalikan (pisahkan dengan koma)")
        daftar_kode = [k.strip().upper() for k in teks.split(",") if k.strip()]
        # Periksa kode dulu, supaya user tidak mengisi kondisi untuk kode yang salah
        self._service.periksa_kode_kembali(transaksi, daftar_kode)

        daftar_kembali = {}
        for kode in daftar_kode:
            daftar_kembali[kode] = ui.input_enum(f"Kondisi {kode}", KondisiAlat)

        status = self._service.kembalikan(id_transaksi, daftar_kembali)
        ui.sukses(f"Pengembalian tersimpan. Status transaksi {id_transaksi}: {status.value}")

    def cari_transaksi(self):
        """Menu 6: Cari transaksi berdasarkan NIM atau nama mahasiswa."""
        kata_kunci = ui.input_wajib("NIM atau nama mahasiswa")
        daftar = self._service.cari_per_mahasiswa(kata_kunci)
        if not daftar:
            ui.info(f"Tidak ada transaksi untuk '{kata_kunci}'.")
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
