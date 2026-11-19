-- Skema database Sistem Peminjaman Alat Lab
-- Urutan: tabel induk dulu (mahasiswa, alat), baru tabel anak (transaksi, detail_transaksi)

CREATE TABLE IF NOT EXISTS mahasiswa (
    nim          VARCHAR(20)  PRIMARY KEY,
    nama         VARCHAR(100) NOT NULL,
    no_hp        VARCHAR(20),
    status_aktif ENUM('aktif','nonaktif') NOT NULL DEFAULT 'aktif'
);

-- TODO: tabel alat
-- TODO: tabel transaksi
-- TODO: tabel detail_transaksi
