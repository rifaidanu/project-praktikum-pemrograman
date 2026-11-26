-- Data dummy. Aman dijalankan ulang: baris yang sudah ada dibiarkan apa adanya
-- (ON DUPLICATE KEY UPDATE kolom = kolom artinya tidak mengubah apa pun)

INSERT INTO mahasiswa (nim, nama, no_hp, status_aktif) VALUES
    ('M001', 'Andi Pratama',   '081234567801', 'aktif'),
    ('M002', 'Budi Santoso',   '081234567802', 'aktif'),
    ('M003', 'Citra Lestari',  '081234567803', 'aktif'),
    ('M004', 'Dewi Anggraini', '081234567804', 'aktif'),
    ('M005', 'Eko Prasetyo',   '081234567805', 'aktif'),
    ('M006', 'Fajar Hidayat',  '081234567806', 'tidak aktif')
ON DUPLICATE KEY UPDATE nim = mahasiswa.nim;

INSERT INTO alat (kode, nama, kategori, kondisi, status) VALUES
    ('ALT-001', 'Multimeter Digital Fluke',  'Elektronika', 'baik',         'dipinjam'),
    ('ALT-002', 'Oscilloscope Rigol',        'Elektronika', 'baik',         'dipinjam'),
    ('ALT-003', 'Crimping Tool RJ45',        'Jaringan',    'baik',         'tersedia'),
    ('ALT-004', 'LAN Tester Pro',            'Jaringan',    'baik',         'dipinjam'),
    ('ALT-005', 'Switch Cisco 24-Port',      'Jaringan',    'baik',         'tersedia'),
    ('ALT-006', 'Solder Station Hakko',      'Elektronika', 'rusak ringan', 'tidak tersedia'),
    ('ALT-007', 'Kamera DSLR Canon 80D',     'Multimedia',  'baik',         'tersedia'),
    ('ALT-008', 'Tripod Kamera Takara',      'Multimedia',  'baik',         'dipinjam'),
    ('ALT-009', 'Power Supply DC GW Instek', 'Elektronika', 'rusak berat',  'tidak tersedia'),
    ('ALT-010', 'Raspberry Pi 4 Model B',    'Komputasi',   'baik',         'tersedia')
ON DUPLICATE KEY UPDATE kode = alat.kode;

-- T001 + T004: M001 punya 2 transaksi aktif (uji Aturan 2), T004 sudah lewat batas kembali
-- T002: sebagian dikembalikan
-- T003 + T005: selesai, dengan alat kembali rusak ringan dan rusak berat
INSERT INTO transaksi (id, nim, tgl_pinjam, batas_kembali, status) VALUES
    ('T001', 'M001', '2026-11-24', '2026-11-29', 'dipinjam'),
    ('T002', 'M002', '2026-11-23', '2026-11-30', 'sebagian dikembalikan'),
    ('T003', 'M003', '2026-11-02', '2026-11-09', 'selesai'),
    ('T004', 'M001', '2026-11-10', '2026-11-17', 'dipinjam'),
    ('T005', 'M004', '2026-10-12', '2026-10-19', 'selesai')
ON DUPLICATE KEY UPDATE id = transaksi.id;

INSERT INTO detail_transaksi (id_transaksi, kode_alat, status, kondisi_kembali, tgl_kembali) VALUES
    ('T001', 'ALT-001', 'dipinjam',     NULL,           NULL),
    ('T001', 'ALT-002', 'dipinjam',     NULL,           NULL),
    ('T002', 'ALT-003', 'dikembalikan', 'baik',         '2026-11-24'),
    ('T002', 'ALT-004', 'dipinjam',     NULL,           NULL),
    ('T003', 'ALT-006', 'dikembalikan', 'rusak ringan', '2026-11-08'),
    ('T003', 'ALT-007', 'dikembalikan', 'baik',         '2026-11-06'),
    ('T004', 'ALT-008', 'dipinjam',     NULL,           NULL),
    ('T005', 'ALT-009', 'dikembalikan', 'rusak berat',  '2026-10-18')
ON DUPLICATE KEY UPDATE id_transaksi = detail_transaksi.id_transaksi;
