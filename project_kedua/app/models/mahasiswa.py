from app.models.enums import StatusMahasiswa


class Mahasiswa:
    """Satu baris tabel mahasiswa."""

    MAKS_TRANSAKSI_AKTIF = 2  # Aturan 2

    def __init__(self, nim, nama, no_hp=None, status_aktif=StatusMahasiswa.AKTIF, dihapus=False):
        self.nim = nim
        self.nama = nama
        self.no_hp = no_hp
        self.status_aktif = status_aktif
        self.dihapus = dihapus

    @classmethod
    def dari_baris(cls, baris):
        """Membuat objek dari hasil query (dict)."""
        return cls(baris["nim"], baris["nama"], baris["no_hp"],
                   StatusMahasiswa(baris["status_aktif"]), bool(baris["dihapus"]))
