-- Skema database Sistem Peminjaman Alat Lab
-- Urutan: tabel induk dulu (mahasiswa, alat), baru tabel anak (transaksi, detail_transaksi)
-- Catatan: teks di SQL wajib pakai kutip tunggal, karena server Aiven memakai mode ANSI_QUOTES
-- Kolom dihapus: data yang dihapus hanya ditandai TRUE agar riwayat peminjaman tetap ada

CREATE TABLE IF NOT EXISTS mahasiswa (
    nim          VARCHAR(20)  PRIMARY KEY,
    nama         VARCHAR(100) NOT NULL,
    no_hp        VARCHAR(20),
    status_aktif ENUM('aktif','tidak aktif') NOT NULL DEFAULT 'aktif',
    dihapus      BOOLEAN NOT NULL DEFAULT FALSE
);

-- Kategori berupa VARCHAR (bukan ENUM) agar kategori baru bisa ditambah tanpa mengubah tabel
-- CHECK: alat yang tidak baik tidak boleh berstatus tersedia (Aturan 5)
CREATE TABLE IF NOT EXISTS alat (
    kode     VARCHAR(20)  PRIMARY KEY,
    nama     VARCHAR(100) NOT NULL,
    kategori VARCHAR(50)  NOT NULL,
    kondisi  ENUM('baik','rusak ringan','rusak berat') NOT NULL DEFAULT 'baik',
    status   ENUM('tersedia','dipinjam','tidak tersedia') NOT NULL DEFAULT 'tersedia',
    dihapus  BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT cek_alat_tersedia CHECK (status <> 'tersedia' OR kondisi = 'baik')
);

-- CHECK: batas kembali 1 sampai 7 hari setelah tanggal pinjam
CREATE TABLE IF NOT EXISTS transaksi (
    id            VARCHAR(20) PRIMARY KEY,
    nim           VARCHAR(20) NOT NULL,
    tgl_pinjam    DATE NOT NULL,
    batas_kembali DATE NOT NULL,
    status        ENUM('dipinjam','sebagian dikembalikan','selesai') NOT NULL DEFAULT 'dipinjam',
    CONSTRAINT fk_transaksi_mahasiswa FOREIGN KEY (nim) REFERENCES mahasiswa(nim),
    CONSTRAINT cek_batas_kembali CHECK (DATEDIFF(batas_kembali, tgl_pinjam) BETWEEN 1 AND 7)
);

-- PRIMARY KEY dua kolom: satu alat hanya boleh muncul sekali di transaksi yang sama
-- CHECK: kondisi dan tanggal kembali kosong selama dipinjam, wajib terisi setelah dikembalikan
CREATE TABLE IF NOT EXISTS detail_transaksi (
    id_transaksi    VARCHAR(20) NOT NULL,
    kode_alat       VARCHAR(20) NOT NULL,
    status          ENUM('dipinjam','dikembalikan') NOT NULL DEFAULT 'dipinjam',
    kondisi_kembali ENUM('baik','rusak ringan','rusak berat'),
    tgl_kembali     DATE,
    PRIMARY KEY (id_transaksi, kode_alat),
    CONSTRAINT fk_detail_transaksi FOREIGN KEY (id_transaksi) REFERENCES transaksi(id),
    CONSTRAINT fk_detail_alat FOREIGN KEY (kode_alat) REFERENCES alat(kode),
    CONSTRAINT cek_data_kembali CHECK (
        (status = 'dipinjam' AND kondisi_kembali IS NULL AND tgl_kembali IS NULL)
        OR (status = 'dikembalikan' AND kondisi_kembali IS NOT NULL AND tgl_kembali IS NOT NULL)
    )
);
