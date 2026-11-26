"""
Modul Fitur 12: Tampilkan Log Aktivitas (Tantangan D)
Log dibaca dari list lab.log, yang dimuat dari data_txt/log.txt saat program dibuka.
"""


def menu_tampilkan_log(lab) -> None:
    print("\n=== LOG AKTIVITAS ===")
    if not lab.log:
        print("Belum ada aktivitas tercatat.")
        return
    jumlah = input("Tampilkan berapa log terakhir? (Enter = semua): ").strip()
    daftar = lab.log
    if jumlah.isdecimal() and int(jumlah) > 0:
        daftar = lab.log[-int(jumlah):]
    for entri in daftar:
        print(f"[{entri['waktu']}] {entri['pesan']}")
    print(f"\nMenampilkan {len(daftar)} dari {len(lab.log)} log.")
