# Proses Pengembalian (Vicko)

from models.enums import KondisiAlat

DAFTAR_PILIHAN = {
    "1": KondisiAlat.BAIK,
    "2": KondisiAlat.RUSAK_RINGAN,
    "3": KondisiAlat.RUSAK_BERAT,
}


def menu_pengembalian(lab):
    id_t = input("ID transaksi: ").strip().upper()
    t = lab.transaksi.get(id_t)
    if t is None:
        print("Gagal: transaksi tidak ditemukan.")
        return
    if not t.masih_aktif():
        print("Gagal: transaksi ini sudah selesai.")
        return

    print("Alat yang belum dikembalikan:")
    for item in t.alat_belum_kembali():
        print(f"  {item.alat.kode_alat} | {item.alat.nama}")

    kode = input("Kode alat yang dikembalikan: ").strip().upper()
    print("Kondisi: 1. Baik  2. Rusak ringan  3. Rusak berat")
    pilihan = input("Pilih (1/2/3): ").strip()
    if pilihan not in DAFTAR_PILIHAN:
        print("Gagal: pilihan kondisi tidak valid.")
        return
    try:
        lab.proses_pengembalian(id_t, kode, DAFTAR_PILIHAN[pilihan])
        print("Pengembalian berhasil dicatat. Status transaksi:", t.status.value)
    except ValueError as e:
        print("Gagal:", e)
