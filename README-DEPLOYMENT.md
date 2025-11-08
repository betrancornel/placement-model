# Deployment Guide: Heroku + Prometheus

Panduan lengkap untuk deploy model ke Heroku dan setup monitoring dengan Prometheus.

## Kriteria 3: Deploy ke Heroku

### Prerequisites

1. **Install Heroku CLI**
   ```bash
   # Windows: Download dari https://devcenter.heroku.com/articles/heroku-cli
   # Atau gunakan installer
   ```

2. **Login ke Heroku**
   ```bash
   heroku login
   ```

### Langkah-langkah Deployment

#### 1. Siapkan Model untuk Heroku

Heroku memiliki batas slug size (500MB untuk free tier). Model TensorFlow bisa besar, jadi kita perlu optimasi:

**Opsi A: Upload model ke cloud storage (Recommended)**
```bash
# Upload model ke Google Cloud Storage atau S3
# Kemudian download saat app start
```

**Opsi B: Gunakan model yang sudah di-compress**
```bash
# Model sudah ada di output/serving_model/
# Pastikan ukurannya < 500MB
```

#### 2. Setup Git Repository

```bash
# Initialize git (jika belum)
git init

# Add files
git add app.py Procfile runtime.txt requirements-heroku.txt .gitignore
git commit -m "Initial deployment setup"
```

#### 3. Create Heroku App

```bash
# Create app dengan nama unik
heroku create bertrandcorneliussia-placement-model

# Atau gunakan nama custom
heroku create your-app-name
```

#### 4. Set Environment Variables (jika perlu)

```bash
# Set model path jika model di cloud storage
heroku config:set MODEL_PATH=gs://your-bucket/model

# Atau set environment lainnya
heroku config:set FLASK_ENV=production
```

#### 5. Deploy ke Heroku

```bash
# Push ke Heroku
git push heroku main

# Atau jika menggunakan master branch
git push heroku master
```

#### 6. Check Logs

```bash
# View logs
heroku logs --tail

# Check app status
heroku ps
```

#### 7. Open App

```bash
# Buka app di browser
heroku open

# Atau akses langsung
# https://bertrandcorneliussia-placement-model.herokuapp.com
```

### Troubleshooting

**Error: Slug size terlalu besar**
```bash
# Check slug size
heroku builds:info

# Solusi:
# 1. Hapus dependencies yang tidak perlu
# 2. Upload model ke cloud storage
# 3. Download model saat app start
```

**Error: Model tidak ditemukan**
```bash
# Pastikan model path benar
heroku run python -c "import os; print(os.listdir('.'))"

# Atau set MODEL_PATH environment variable
heroku config:set MODEL_PATH=output/serving_model/1762435641
```

**Error: Port binding**
- Heroku otomatis set PORT environment variable
- Pastikan app.py menggunakan `os.environ.get('PORT', 5000)`

---

## Kriteria 4: Monitoring dengan Prometheus

### Setup Prometheus Lokal

#### 1. Download Prometheus

**Windows:**
```bash
# Download dari https://prometheus.io/download/
# Extract ke folder prometheus/
```

**Atau gunakan Docker:**
```bash
docker pull prom/prometheus
```

#### 2. Konfigurasi Prometheus

File `prometheus.yml` sudah dibuat. Update target URL sesuai kebutuhan:

```yaml
scrape_configs:
  - job_name: 'placement-model-local'
    static_configs:
      - targets: ['localhost:5000']  # Update dengan port app Anda
```

#### 3. Jalankan Prometheus

**Windows (Manual):**
```bash
cd prometheus
prometheus.exe --config.file=prometheus.yml
```

**Docker:**
```bash
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

#### 4. Akses Prometheus UI

Buka browser: `http://localhost:9090`

### Metrics yang Tersedia

Setelah app berjalan, metrics berikut tersedia di `/metrics`:

1. **http_requests_total**
   - Total HTTP requests
   - Labels: method, endpoint, status
   - Query: `rate(http_requests_total[5m])`

2. **http_request_duration_seconds**
   - Latency HTTP requests
   - Labels: method, endpoint
   - Query: `histogram_quantile(0.95, http_request_duration_seconds_bucket)`

3. **predictions_total**
   - Total predictions
   - Labels: prediction_class
   - Query: `sum(predictions_total) by (prediction_class)`

4. **prediction_probability**
   - Distribution probability prediksi
   - Labels: prediction_class
   - Query: `avg(prediction_probability)`

### Query Examples

**Request rate per endpoint:**
```
rate(http_requests_total[5m])
```

**95th percentile latency:**
```
histogram_quantile(0.95, http_request_duration_seconds_bucket)
```

**Total predictions:**
```
sum(predictions_total)
```

**Average prediction probability:**
```
avg(prediction_probability)
```

### Monitoring Heroku App

Untuk monitoring app di Heroku:

1. **Update prometheus.yml:**
```yaml
scrape_configs:
  - job_name: 'placement-model-heroku'
    scheme: https
    static_configs:
      - targets: ['bertrandcorneliussia-placement-model.herokuapp.com']
    metrics_path: '/metrics'
```

2. **Pastikan app di Heroku accessible:**
```bash
# Test metrics endpoint
curl https://bertrandcorneliussia-placement-model.herokuapp.com/metrics
```

3. **Setup Prometheus Cloud (Opsional):**
   - Daftar di https://prometheus.io/cloud/
   - Setup remote write untuk push metrics ke cloud

### Alert Rules (Opsional)

Buat file `alert_rules.yml`:

```yaml
groups:
  - name: placement_model_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 2
        for: 5m
        annotations:
          summary: "High latency detected"
```

Tambahkan ke `prometheus.yml`:
```yaml
rule_files:
  - "alert_rules.yml"
```

---

## Testing

### Test Lokal

1. **Start app:**
```bash
python app.py
```

2. **Test endpoints:**
```bash
# Health check
curl http://localhost:5000/health

# Metrics
curl http://localhost:5000/metrics

# Prediction (POST)
curl -X POST http://localhost:5000/predict \
  -d "gender=M&ssc_p=67&ssc_b=Central&hsc_p=91&hsc_b=Central&hsc_s=Commerce&degree_p=58&degree_t=Comm&Mgmt&workex=No&etest_p=55&specialisation=Mkt&Fin&mba_p=58.8"
```

### Test Heroku

```bash
# Health check
curl https://bertrandcorneliussia-placement-model.herokuapp.com/health

# Metrics
curl https://bertrandcorneliussia-placement-model.herokuapp.com/metrics
```

---

## Struktur File

```
bertrandcorneliussia-pipeline/
├── app.py                      # Flask web app
├── Procfile                    # Heroku process file
├── runtime.txt                 # Python version
├── requirements-heroku.txt     # Dependencies untuk Heroku
├── prometheus.yml              # Prometheus config
├── README-DEPLOYMENT.md        # This file
├── .gitignore                  # Git ignore
└── ...
```

---

## Checklist

### Kriteria 3 (Heroku):
- [x] Buat `app.py` dengan Flask
- [x] Buat `Procfile`
- [x] Buat `runtime.txt`
- [x] Buat `requirements-heroku.txt`
- [ ] Test lokal: `python app.py`
- [ ] Deploy ke Heroku
- [ ] Verifikasi app berjalan di Heroku

### Kriteria 4 (Prometheus):
- [x] Install Prometheus
- [x] Buat `prometheus.yml`
- [x] Pastikan `/metrics` endpoint di app.py
- [ ] Jalankan Prometheus
- [ ] Verifikasi metrics muncul di Prometheus UI
- [ ] Buat query untuk monitoring

---

## Catatan Penting

1. **Model Size:** Heroku free tier memiliki batas 500MB. Jika model terlalu besar, pertimbangkan:
   - Upload model ke cloud storage (GCS, S3)
   - Download model saat app start
   - Gunakan model compression

2. **Transform Graph:** Untuk production, pastikan preprocessing menggunakan transform graph yang benar dari TFX pipeline.

3. **Security:** Tambahkan authentication untuk `/metrics` endpoint di production.

4. **Scaling:** Heroku free tier memiliki batas. Pertimbangkan upgrade untuk production.


