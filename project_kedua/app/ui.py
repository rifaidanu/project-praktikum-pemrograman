"""Alat bantu tampilan terminal. Dipakai semua menu agar tampilannya seragam."""
from app.errors import AturanBisnisError, DatabaseError


def sukses(pesan):
    print(f"✅ {pesan}")


def gagal(pesan):
    print(f"❌ {pesan}")


def info(pesan):
    print(f"ℹ️  {pesan}")


def input_wajib(label):
    """Mengulang sampai user mengisi sesuatu."""
    while True:
        nilai = input(f"{label}: ").strip()
        if nilai:
            return nilai
        gagal("Tidak boleh kosong.")


def input_opsional(label, nilai_lama):
    """Enter tanpa mengetik berarti memakai nilai lama. Cocok untuk fitur edit."""
    return input(f"{label} [{nilai_lama or '-'}]: ").strip() or nilai_lama


def input_angka(label, minimal, maksimal):
    """Mengulang sampai user memasukkan bilangan bulat dalam rentang."""
    while True:
        try:
            angka = int(input(f"{label} ({minimal}-{maksimal}): ").strip())
        except ValueError:
            gagal("Masukkan angka.")
            continue
        if minimal <= angka <= maksimal:
            return angka
        gagal(f"Harus antara {minimal} dan {maksimal}.")


def input_enum(label, kelas_enum):
    """Menampilkan semua pilihan enum, mengembalikan anggota enum yang dipilih."""
    pilihan = list(kelas_enum)
    print(f"{label}:")
    for nomor, anggota in enumerate(pilihan, start=1):
        print(f"  {nomor}. {anggota.value}")
    return pilihan[input_angka("Pilih", 1, len(pilihan)) - 1]


def konfirmasi(pertanyaan):
    return input(f"{pertanyaan} (y/n): ").strip().lower() == "y"


def tabel(judul_kolom, daftar_baris):
    """Mencetak tabel. Contoh: tabel(["NIM", "Nama"], [["M001", "Andi"]])"""
    if not daftar_baris:
        info("Data kosong.")
        return
    teks = [["-" if sel is None else str(sel) for sel in baris] for baris in daftar_baris]
    lebar = [max(len(baris[i]) for baris in [judul_kolom] + teks) for i in range(len(judul_kolom))]
    print(" | ".join(sel.ljust(n) for sel, n in zip(judul_kolom, lebar)))
    print("-+-".join("-" * n for n in lebar))
    for baris in teks:
        print(" | ".join(sel.ljust(n) for sel, n in zip(baris, lebar)))


def jalankan_aksi(aksi):
    """Menjalankan satu fitur. Semua error ditampilkan ramah, program tidak berhenti."""
    try:
        aksi()
    except AturanBisnisError as e:
        gagal(e)
    except DatabaseError as e:
        gagal(f"Database bermasalah: {e}")
    except NotImplementedError as e:
        info(f"Fitur belum dikerjakan -> {e}")


def jalankan_menu(judul, daftar_pilihan, label_keluar="Kembali"):
    """Menampilkan menu berulang sampai user memilih 0.

    daftar_pilihan: list of (label, fungsi), nomor menu mengikuti urutan list.
    """
    while True:
        print(f"\n{'=' * 50}\n{judul.center(50)}\n{'=' * 50}")
        for nomor, (label, _) in enumerate(daftar_pilihan, start=1):
            print(f"{nomor:>2}. {label}")
        print(f" 0. {label_keluar}")
        pilihan = input("Pilih menu: ").strip()
        if pilihan == "0":
            return
        if pilihan.isdecimal() and 1 <= int(pilihan) <= len(daftar_pilihan):
            label, aksi = daftar_pilihan[int(pilihan) - 1]
            print(f"\n--- {label} ---")
            jalankan_aksi(aksi)
        else:
            gagal("Pilihan tidak valid.")
