"""Paket 1. Input dan tampilan mahasiswa (menu 1 dan 10)."""
from app import ui
from app.models import StatusMahasiswa


class MahasiswaMenu:
    """Hanya input dan print. Error ditangani ui.jalankan_aksi, tidak perlu try-except di sini."""

    def __init__(self, service):
        self._service = service

    def kelola(self):
        """Menu 1. Submenu sudah jadi, tinggal isi method di bawah."""
        ui.jalankan_menu("KELOLA MAHASISWA", [
            ("Tambah mahasiswa", self.tambah),
            ("Edit mahasiswa", self.edit),
            ("Hapus mahasiswa", self.hapus),
            ("Cari mahasiswa", self.cari),
        ])

    def tambah(self):
        """Menu 1 -> 1: Tambah mahasiswa."""
        nim = ui.input_wajib("NIM").upper()
        nama = ui.input_wajib("Nama")
        no_hp = ui.input_wajib("No HP")
        self._service.tambah(nim, nama, no_hp)
        ui.sukses(f"Mahasiswa '{nama}' ({nim}) berhasil ditambahkan.")

    def edit(self):
        """Menu 1 -> 2: Edit mahasiswa."""
        nim = ui.input_wajib("NIM").upper()
        mhs = self._service.ambil(nim)
        nama = ui.input_opsional("Nama", mhs.nama)
        no_hp = ui.input_opsional("No HP", mhs.no_hp)
        status_aktif = ui.input_enum(
            f"Status aktif (saat ini: {mhs.status_aktif.value})", StatusMahasiswa
        )
        self._service.edit(mhs.nim, nama, no_hp, status_aktif)
        ui.sukses(f"Data mahasiswa '{mhs.nim}' berhasil diperbarui.")

    def hapus(self):
        """Menu 1 -> 3: Hapus mahasiswa."""
        nim = ui.input_wajib("NIM").upper()
        mhs = self._service.ambil(nim)
        if ui.konfirmasi(f"Yakin ingin menghapus {mhs.nama} ({mhs.nim})?"):
            self._service.hapus(mhs.nim)
            ui.sukses(f"Mahasiswa '{mhs.nama}' ({mhs.nim}) berhasil dihapus.")
        else:
            ui.info("Penghapusan dibatalkan.")

    def cari(self):
        """Menu 1 -> 4: Cari mahasiswa."""
        kata_kunci = input("Kata kunci NIM/Nama (kosong = semua): ").strip()
        daftar = self._service.cari(kata_kunci)
        ui.tabel(
            ["NIM", "Nama", "No HP", "Status"],
            [[m.nim, m.nama, m.no_hp, m.status_aktif.value] for m in daftar],
        )

    def tampilkan_riwayat(self):
        """Menu 10: Riwayat peminjaman mahasiswa."""
        nim = ui.input_wajib("NIM").upper()
        daftar_trx = self._service.riwayat(nim)
        if not daftar_trx:
            ui.info("Mahasiswa ini belum memiliki riwayat peminjaman.")
            return
        for trx in daftar_trx:
            ket_terlambat = " [TERLAMBAT]" if trx.terlambat() else ""
            print(
                f"\n[{trx.id_transaksi}] {trx.nama_mahasiswa} ({trx.nim}) | "
                f"Pinjam: {trx.tgl_pinjam} | Batas: {trx.batas_kembali} | "
                f"Status: {trx.status.value}{ket_terlambat}"
            )
            ui.tabel(
                ["Kode Alat", "Nama Alat", "Status", "Kondisi Kembali", "Tgl Kembali"],
                [
                    [
                        item.kode_alat,
                        item.nama_alat,
                        item.status.value,
                        item.kondisi_kembali.value if item.kondisi_kembali else "-",
                        item.tgl_kembali,
                    ]
                    for item in trx.daftar_item
                ],
            )