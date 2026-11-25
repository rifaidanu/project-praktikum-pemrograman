from app.models.enums import KondisiAlat, StatusAlat


class Alat:
    """Satu baris tabel alat."""

    def __init__(self, kode, nama, kategori, kondisi=KondisiAlat.BAIK,
                 status=StatusAlat.TERSEDIA, dihapus=False):
        self.kode = kode
        self.nama = nama
        self.kategori = kategori
        self.kondisi = kondisi
        self.status = status
        self.dihapus = dihapus

    @classmethod
    def dari_baris(cls, baris):
        """Membuat objek dari hasil query (dict)."""
        return cls(baris["kode"], baris["nama"], baris["kategori"],
                   KondisiAlat(baris["kondisi"]), StatusAlat(baris["status"]),
                   bool(baris["dihapus"]))

    def tersedia(self):
        return self.status == StatusAlat.TERSEDIA

    @staticmethod
    def status_untuk_kondisi(kondisi):
        """Aturan 5: hanya alat berkondisi baik yang tersedia."""
        return StatusAlat.TERSEDIA if kondisi == KondisiAlat.BAIK else StatusAlat.TIDAK_TERSEDIA
