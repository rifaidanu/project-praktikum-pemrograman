# Buat Transaksi (Vicko)

from datetime import date, timedelta

from models.transaksi import Transaksi


def menu_buat_transaksi(lab):
    # Tampilkan alat yang tersedia sebagai referensi
    tersedia = lab.tampilkan_alat_tersedia()
    if not tersedia:
        print("Tidak ada alat yang tersedia untuk dipinjam.")
        return
    print("Alat yang tersedia:")
    for alat in tersedia:
        print(f"  {alat.kode_alat} | {alat.nama} ({alat.kategori})")

    nim = input("NIM mahasiswa: ").strip().upper()
    teks = input("Kode alat (pisahkan dengan koma): ")
    daftar_kode = [k.strip().upper() for k in teks.split(",") if k.strip()]
    try:
        lama = int(input(f"Lama peminjaman (1-{Transaksi.MAKS_HARI} hari): "))
        if lama < 1 or lama > Transaksi.MAKS_HARI:
            raise ValueError(f"Lama peminjaman harus 1 sampai {Transaksi.MAKS_HARI} hari.")
        batas = date.today() + timedelta(days=lama)
        t = lab.buat_transaksi(nim, daftar_kode, batas)
        print("Berhasil! ID transaksi:", t.id_transaksi, "| Batas kembali:", t.batas_pengembalian)
    except ValueError as e:
        print("Gagal:", e)
