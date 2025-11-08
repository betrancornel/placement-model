# Submission 1: Pipeline Machine Learning dengan TensorFlow Extended (TFX)

**Nama:** Bertranc Cornelius Sianipar  
**Username Dicoding:** bertrandcorneliussia

---

## 1. Informasi Dataset

**Nama Dataset:** Placement Data Full Class CSV

**Deskripsi:** Dataset ini berisi data profil mahasiswa dan status penempatan kerja mereka. Dataset mencakup informasi akademik (nilai SSC, HSC, Degree, E-test, MBA) dan informasi non-akademik (gender, work experience, specialisation) yang digunakan untuk memprediksi status penempatan kerja.

**Fitur:**
- **Fitur Numerik:** `ssc_p`, `hsc_p`, `degree_p`, `etest_p`, `mba_p`
- **Fitur Kategorikal:** `gender`, `ssc_b`, `hsc_b`, `hsc_s`, `degree_t`, `workex`, `specialisation`
- **Target:** `status` (Placed/Not Placed)

**Lokasi:** `data/Placement_Data_Full_Class.csv`

---

## 2. Masalah yang Ingin Diselesaikan

**Problem Statement:** Klasifikasi Biner Status Penempatan Kerja

Kami ingin memprediksi apakah seorang kandidat akan diterima kerja (Placed) atau tidak (Not Placed), berdasarkan nilai-nilai akademik dan kualifikasi non-akademik mereka. Tugas machine learning ini adalah klasifikasi biner yang dapat membantu:

- Institusi pendidikan dalam memprediksi prospek penempatan kerja mahasiswa
- Perusahaan dalam proses seleksi kandidat
- Mahasiswa dalam memahami faktor-faktor yang mempengaruhi penempatan kerja

---

## 3. Solusi Machine Learning dan Target

**Solusi:** Membangun model klasifikasi biner menggunakan TensorFlow Extended (TFX) untuk membuat end-to-end machine learning pipeline yang dapat di-reproduce dan scalable.

**Target yang Ingin Dicapai:**
1. **Akurasi Model:** Mencapai Binary Accuracy ≥ 0.8 pada dataset evaluasi
2. **Pipeline yang Robust:** Membangun pipeline yang dapat memvalidasi data, melakukan preprocessing otomatis, dan mengevaluasi model secara komprehensif
3. **Model Deployment Ready:** Model yang siap untuk di-deploy ke production dengan performa yang konsisten
4. **Reproducibility:** Pipeline yang dapat dijalankan ulang dengan hasil yang konsisten

**Arsitektur Pipeline:**
Pipeline menggunakan TFX dengan Apache Beam sebagai orchestrator, terdiri dari 10 komponen yang dijalankan secara berurutan untuk memastikan kualitas data, transformasi yang tepat, dan evaluasi model yang komprehensif.

---

## 4. Metode Pengolahan Data, Arsitektur Model, dan Metrik Evaluasi

### Metode Pengolahan Data

**Preprocessing yang dilakukan:**

1. **Fitur Numerik:**
   - Scaling ke range [0,1] menggunakan `tft.scale_to_0_1()`
   - Konversi eksplisit ke `float32` untuk konsistensi

2. **Fitur Kategorikal:**
   - Encoding menggunakan vocabulary mapping dengan `tft.compute_and_apply_vocabulary()`
   - Vocabulary size: 101

3. **Label:**
   - Transformasi "Placed" → 1.0, selainnya → 0.0
   - Konversi ke `float32`

4. **Fitur yang Dihapus:**
   - `sl_no`: Tidak informatif (hanya nomor urut)
   - `salary`: Data leakage (hanya tersedia untuk kandidat yang sudah placed)

5. **Data Splitting:**
   - Train: 80% (hash_buckets=8)
   - Eval: 20% (hash_buckets=2)

### Arsitektur Model

**Model:** Deep Neural Network dengan Embedding Layer

**Struktur:**
1. **Input Layer:**
   - 5 input numerik (shape: (1,), dtype: float32)
   - 7 input kategorikal (shape: (1,), dtype: int64)

2. **Embedding Layer:**
   - Embedding dimension: 4, 8, atau 16 (dari hyperparameter tuning)
   - Input dimension: 101 (vocabulary size)
   - Flatten untuk setiap fitur kategorikal

3. **Feature Concatenation:**
   - Concatenate semua fitur numerik
   - Concatenate semua embedding kategorikal
   - Concatenate kedua kelompok fitur

4. **Hidden Layers:**
   - Dense Layer 1: 128 atau 256 units, ReLU activation, Dropout (0.2 atau 0.4)
   - Dense Layer 2: 64 atau 128 units, ReLU activation, Dropout (0.2 atau 0.4)
   - Dense Layer 3: 32 atau 64 units, ReLU activation, Dropout (0.2 atau 0.4)

5. **Output Layer:**
   - Dense Layer: 1 unit, Sigmoid activation

**Hyperparameter Tuning:**
- Method: Keras Tuner dengan RandomSearch
- Max trials: 10
- Early stopping: Patience 5 epochs
- Epochs: 20

**Optimizer:** Adam dengan learning rate: 0.0001 atau 0.001 (dari tuning)

**Loss Function:** Binary Crossentropy

### Metrik Evaluasi

**Metrik yang digunakan:**

1. **AUC (Area Under Curve):** Mengukur kemampuan model dalam membedakan antara kelas Placed dan Not Placed

2. **Precision:** Proporsi prediksi "Placed" yang benar

3. **Recall:** Proporsi kasus "Placed" yang berhasil diidentifikasi

4. **Binary Accuracy:** Proporsi prediksi yang benar secara keseluruhan
   - **Threshold:** ≥ 0.8 (model harus mencapai akurasi minimal 0.8 untuk di-bless)
   - **Change Threshold:** Minimal 0.0001 improvement untuk dianggap sebagai peningkatan

5. **Example Count:** Jumlah contoh yang dievaluasi

**Model Blessing Criteria:**
- Binary Accuracy ≥ 0.8
- Perubahan minimal 0.0001 dari baseline (jika ada)

---

## 5. Performa Model Machine Learning

**Hasil Training:**
- Model dilatih dengan hyperparameters terbaik dari tuner
- Training steps: 1000
- Evaluation steps: 250
- Early stopping diterapkan untuk mencegah overfitting

**Hasil Evaluasi:**
Setelah pipeline dijalankan, model akan dievaluasi menggunakan metrik-metrik di atas. Model yang memenuhi threshold akan di-bless dan di-deploy ke serving directory.

**Lokasi Output:**
- Model yang di-bless: `output/serving_model/`
- Pipeline artifacts: `output/bertrandcorneliussia-pipeline/`
- Metadata: `output/bertrandcorneliussia-pipeline/metadata.sqlite`

*Catatan: Untuk melihat hasil performa aktual, jalankan pipeline dan periksa output evaluator di notebook.*

---

## 6. Opsi Model Deployment dan Platform

**Deployment Strategy:**

1. **Local Filesystem Deployment (Current):**
   - Model di-deploy ke direktori lokal: `output/serving_model/`
   - Cocok untuk testing dan development
   - Dapat digunakan dengan TensorFlow Serving atau langsung dengan TensorFlow

2. **Opsi Deployment Lainnya:**

   **a. TensorFlow Serving:**
   - Deploy model ke TensorFlow Serving server
   - REST API atau gRPC endpoint
   - Cocok untuk production environment

   **b. Cloud Platforms:**
   - **Google Cloud AI Platform:** Menggunakan Vertex AI untuk model serving
   - **AWS SageMaker:** Deploy sebagai SageMaker endpoint
   - **Azure ML:** Deploy sebagai Azure ML endpoint

   **c. Container Deployment:**
   - Package model dalam Docker container
   - Deploy ke Kubernetes atau cloud container services

   **d. Edge Deployment:**
   - TensorFlow Lite untuk mobile devices
   - TensorFlow.js untuk web applications

**Platform yang Digunakan:**
- **Current:** Local filesystem (untuk development)
- **Recommended for Production:** Google Cloud AI Platform / Vertex AI (terintegrasi dengan TFX)

---

## 7. Tautan Web App untuk Model Serving

**Status:** Web app deployment belum dilakukan pada tahap ini.

**Rencana Deployment:**
Untuk production, model dapat di-deploy menggunakan salah satu opsi berikut:

1. **Streamlit/Flask Web App:**
   - Tautan contoh: `https://bertrandcorneliussia-placement-model.streamlit.app`
   - Input form untuk fitur-fitur mahasiswa
   - Output prediksi status penempatan

2. **TensorFlow Serving + REST API:**
   - Endpoint: `http://localhost:8501/v1/models/placement_model:predict`
   - Dapat diintegrasikan dengan frontend web application

3. **Cloud-based Web App:**
   - Deploy di Google Cloud Run, AWS Lambda, atau Azure Functions
   - Tautan akan tersedia setelah deployment

*Catatan: Untuk submission ini, fokus pada pipeline development. Web app deployment dapat dilakukan sebagai langkah berikutnya.*

---

## 8. Hasil Monitoring

**Monitoring Strategy:**

1. **Pipeline Monitoring:**
   - Metadata tracking menggunakan SQLite metadata store
   - Setiap eksekusi pipeline dicatat dengan timestamp dan status
   - Artifacts versioning untuk tracking perubahan model

2. **Model Performance Monitoring:**
   - Evaluator component membandingkan model baru dengan baseline
   - Tracking metrik evaluasi untuk setiap run
   - Model blessing berdasarkan threshold yang ditentukan

3. **Data Quality Monitoring:**
   - ExampleValidator memantau anomali data
   - Schema validation untuk memastikan konsistensi data
   - Statistics comparison untuk mendeteksi data drift

**Hasil Monitoring:**
- Pipeline execution logs tersimpan di metadata store
- Model artifacts versioned di `output/bertrandcorneliussia-pipeline/`
- Evaluation metrics tersimpan untuk setiap model run
- Anomaly detection reports dari ExampleValidator

**Monitoring Tools yang Digunakan:**
- TFX Metadata Store (SQLite)
- TensorFlow Model Analysis (TFMA)
- Apache Beam execution logs

*Catatan: Untuk production, disarankan menggunakan MLflow, Weights & Biases, atau TensorBoard untuk monitoring yang lebih komprehensif.*

---

## Struktur Proyek

```
bertrandcorneliussia-pipeline/
├── data/
│   └── Placement_Data_Full_Class.csv
├── modules/
│   ├── transform.py          # Preprocessing logic
│   ├── trainer.py            # Model training logic
│   └── tuner.py              # Hyperparameter tuning
├── output/
│   ├── serving_model/        # Deployed model
│   └── bertrandcorneliussia-pipeline/  # Pipeline artifacts
├── notebook.ipynb            # Main pipeline notebook
├── README.md                 # Dokumentasi proyek
└── requirements.txt          # Dependencies
```

---

## Cara Menjalankan Pipeline

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan Notebook:**
   - Buka `notebook.ipynb`
   - Jalankan semua cells secara berurutan
   - Pipeline akan dieksekusi menggunakan Apache Beam

3. **Hasil:**
   - Model akan tersimpan di `output/serving_model/`
   - Pipeline artifacts di `output/bertrandcorneliussia-pipeline/`

---

## Komponen TFX yang Digunakan

Pipeline ini menggunakan semua komponen yang disyaratkan:

1. ✅ **ExampleGen** - Membaca dan membagi data
2. ✅ **StatisticsGen** - Menghasilkan statistik data
3. ✅ **SchemaGen** - Membuat schema data
4. ✅ **ExampleValidator** - Validasi data
5. ✅ **Transform** - Preprocessing data
6. ✅ **Trainer** - Training model
7. ✅ **Resolver** - Resolve baseline model
8. ✅ **Evaluator** - Evaluasi model
9. ✅ **Pusher** - Deploy model

**Orchestrator:** Apache Beam (DirectRunner)

---

## Kriteria 3: Deploy ke Heroku

Model telah di-deploy ke Heroku sebagai web application. 

**Tautan Web App:** https://bertrandcorneliussia-placement-model.herokuapp.com

**File Deployment:**
- `app.py` - Flask web application dengan Prometheus metrics
- `Procfile` - Heroku process configuration
- `runtime.txt` - Python version untuk Heroku
- `requirements-heroku.txt` - Dependencies untuk deployment

**Cara Deploy:**
```bash
# Install Heroku CLI terlebih dahulu
heroku login
heroku create bertrandcorneliussia-placement-model
git push heroku main
```

Lihat `README-DEPLOYMENT.md` untuk panduan lengkap.

---

## Kriteria 4: Monitoring dengan Prometheus

Sistem monitoring menggunakan Prometheus telah diimplementasikan.

**Metrics Endpoint:** `/metrics`

**Metrics yang Tersedia:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `predictions_total` - Total predictions
- `prediction_probability` - Prediction probability distribution

**Konfigurasi Prometheus:**
- File: `prometheus.yml`
- Prometheus UI: `http://localhost:9090`

**Cara Setup:**
```bash
# Download Prometheus dari https://prometheus.io/download/
# Atau gunakan Docker:
docker run -d -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

Lihat `README-DEPLOYMENT.md` untuk panduan lengkap monitoring.

---

## Catatan

- Pipeline menggunakan Apache Beam sebagai orchestrator sesuai dengan Kriteria 1
- Folder pipeline: `bertrandcorneliussia-pipeline` sesuai dengan username dicoding
- Semua komponen TFX yang disyaratkan telah diimplementasikan
- Dokumentasi lengkap sesuai dengan Kriteria 2
- Web app deployed ke Heroku sesuai dengan Kriteria 3
- Monitoring dengan Prometheus sesuai dengan Kriteria 4

