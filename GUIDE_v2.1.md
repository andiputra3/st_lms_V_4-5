# ST-LMS v2.1 — Panduan Pengguna CLI

## Instalasi
```bash
git clone https://github.com/andiputra3/st_lms_V_4-5.git
cd st_lms_V_4-5
python3 stlms.py setup
```

## Perintah Dasar
| Command | Fungsi |
|---------|--------|
| `python3 stlms.py` | Interactive menu (16 pilihan) |
| `python3 stlms.py version` | Versi sistem |
| `python3 stlms.py help` | Bantuan lengkap |
| `python3 stlms.py doctor` | Diagnostik sistem (10 cek) |
| `python3 stlms.py health` | Cek kesehatan cepat |

## Pipeline v2.1 — Artifact Production Line
| Command | Tahap | Fungsi |
|---------|-------|--------|
| `python3 stlms.py collect` | 01-02 | Kumpulkan data mentah + buat ID |
| `python3 stlms.py sync` | 02-03 | Sinkronisasi timeframe |
| `python3 stlms.py run` | 01-20 | Jalankan seluruh 20 tahap |
| `python3 stlms.py build` | Info | Lihat struktur pipeline |

## Market Intelligence Consumer (on-demand)
| Command | Consumer | Fungsi |
|---------|----------|--------|
| `python3 stlms.py statistics` | Statistics | Semua statistik (7 domain) |
| `python3 stlms.py knowledge` | Knowledge | Academy, Oracle, HiveMind |
| `python3 stlms.py prediction` | Prediction | Market Possibilities |
| `python3 stlms.py simulation` | Simulation | Professional Trader |
| `python3 stlms.py recommendation` | Recommendation | Market Intelligence Report |
| `python3 stlms.py replay` | Replay | Historical data |
| `python3 stlms.py snapshot` | Snapshot | Lihat snapshot |
| `python3 stlms.py timeline` | Timeline | Timeline observasi |
| `python3 stlms.py sqlite` | SQLite | Browser database |

## Web Dashboard
| Command | Fungsi |
|---------|--------|
| `python3 stlms.py dashboard` | Start web dashboard di :8082 |

## Pengujian
| Command | Fungsi |
|---------|--------|
| `python3 stlms.py test` | 276 unit tests |
| `python3 stlms.py benchmark` | WASIT 5-gate benchmark |

## Maintenance
| Command | Fungsi |
|---------|--------|
| `python3 stlms.py clean` | Bersihkan file sementara |
| `python3 stlms.py reset` | Reset database |
| `python3 stlms.py stop` | Stop web server |
| `python3 stlms.py export` | Export data |

## Arsitektur v2.1
20 tahap Artifact Production Line. Setiap tahap satu tugas:
01 Raw Collector → 02 Observation Builder → 03 Market → 04 Truth → 
05 Structure → 06 Evidence → 07 Clone → 08 Statistics Engine → 
09 BAG Engine → 10 Knowledge Repository → 11 Possibility Engine → 
12 Professional Trader → 13 Recommendation → 14 History Builder → 
15 Snapshot Builder → 16 Historical Enricher → 17 DNA Builder → 
18 Freeze Engine → 19 SQLite Writer → 20 Memory Window

6 Market Intelligence Consumers (terpisah dari pipeline):
Replay, Statistics, Knowledge, Prediction, Simulation, Recommendation
