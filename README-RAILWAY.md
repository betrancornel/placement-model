# Deployment Guide: Railway.app

Panduan lengkap untuk deploy model ke Railway.app (alternatif Heroku yang tidak memerlukan kartu kredit).

## Keuntungan Railway

- ✅ **Tidak perlu kartu kredit** untuk mulai
- ✅ **Gratis $5 credit** setiap bulan
- ✅ **Auto-deploy** dari GitHub
- ✅ **Lebih mudah** daripada Heroku
- ✅ **Built-in monitoring**

## Prerequisites

1. Akun GitHub (untuk deploy dari repo)
2. Akun Railway (gratis di https://railway.app)

## Langkah-langkah Deployment

### 1. Buat Akun Railway

1. Buka https://railway.app
2. Klik **"Start a New Project"** atau **"Login"**
3. Login dengan GitHub (recommended) atau email
4. Tidak perlu kartu kredit!

### 2. Siapkan GitHub Repository

#### A. Initialize Git (jika belum)

```powershell
# Di folder project
cd C:\bertrandcorneliussia-pipeline

# Initialize git
git init

# Add files
git add .
git commit -m "Initial commit for Railway deployment"
```

#### B. Push ke GitHub

1. Buat repository baru di GitHub:
   - Buka https://github.com/new
   - Buat repository baru (misalnya: `placement-model`)
   - Jangan initialize dengan README

2. Push ke GitHub:

```powershell
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/placement-model.git

# Push
git branch -M main
git push -u origin main
```

**Catatan:** Ganti `YOUR_USERNAME` dengan username GitHub Anda.

### 3. Deploy ke Railway

#### A. Via Railway Dashboard (Recommended)

1. Buka https://railway.app
2. Klik **"New Project"**
3. Pilih **"Deploy from GitHub repo"**
4. Authorize Railway untuk akses GitHub (jika pertama kali)
5. Pilih repository yang sudah dibuat
6. Railway akan otomatis:
   - Detect Python app
   - Install dependencies dari `requirements.txt`
   - Deploy aplikasi

#### B. Via Railway CLI (Opsional)

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway init

# Deploy
railway up
```

### 4. Configure Environment Variables (Jika Perlu)

1. Di Railway dashboard, pilih project Anda
2. Klik **"Variables"**
3. Tambahkan environment variables jika perlu:
   - `PORT` - Railway otomatis set
   - `MODEL_PATH` - Jika model di cloud storage

### 5. Deploy Model Files

**Masalah:** Model files terlalu besar untuk GitHub.

**Solusi:**

#### Opsi A: Upload Model ke Railway Volume (Recommended)

1. Di Railway dashboard, tambahkan **Volume**
2. Upload model files ke volume
3. Update `app.py` untuk load dari volume

#### Opsi B: Upload Model ke Cloud Storage

1. Upload model ke Google Cloud Storage / AWS S3
2. Download saat app start
3. Set environment variable `MODEL_URL`

#### Opsi C: Include Model di Git (Jika Kecil)

Jika model < 100MB, bisa di-commit ke Git:
```powershell
git add output/serving_model
git commit -m "Add model files"
git push
```

### 6. Get App URL

1. Di Railway dashboard, pilih service
2. Klik **"Settings"** → **"Networking"**
3. Generate domain atau tambahkan custom domain
4. Copy URL (contoh: `https://placement-model.up.railway.app`)

### 7. Test Aplikasi

```powershell
# Test health endpoint
curl https://YOUR_APP_URL.railway.app/health

# Test metrics endpoint
curl https://YOUR_APP_URL.railway.app/metrics

# Test prediction (dari browser)
https://YOUR_APP_URL.railway.app
```

---

## File yang Diperlukan

Railway akan otomatis detect file berikut:

1. **requirements.txt** - Dependencies Python
2. **app.py** - Flask application
3. **railway.json** - Konfigurasi Railway (opsional)
4. **runtime.txt** - Python version (opsional)

---

## Troubleshooting

### Error: "No module named 'tensorflow'"

**Solusi:**
- Pastikan `requirements.txt` ada dan berisi tensorflow
- Railway akan install otomatis dari requirements.txt

### Error: "Model not found"

**Solusi:**
- Upload model files ke Railway Volume
- Atau update `MODEL_PATH` environment variable
- Atau include model di Git (jika kecil)

### Error: "Port already in use"

**Solusi:**
- Railway otomatis set `PORT` environment variable
- Pastikan `app.py` menggunakan `os.environ.get('PORT', 5000)`

### Error: "Build failed"

**Solusi:**
- Cek logs di Railway dashboard
- Pastikan `requirements.txt` valid
- Pastikan Python version sesuai

### App tidak bisa diakses

**Solusi:**
- Pastikan service sudah deployed
- Cek domain di Settings → Networking
- Cek logs untuk error

---

## Monitoring dengan Prometheus

### 1. Update Prometheus Config

Edit `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'placement-model-railway'
    scheme: https
    static_configs:
      - targets: ['YOUR_APP_URL.railway.app']
        labels:
          instance: 'railway-app'
    metrics_path: '/metrics'
```

### 2. Jalankan Prometheus

```bash
# Download Prometheus
# Atau gunakan Docker:
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 3. Akses Prometheus UI

Buka: `http://localhost:9090`

---

## Update Deployment

Railway akan otomatis redeploy ketika Anda push ke GitHub:

```powershell
# Update code
git add .
git commit -m "Update app"
git push

# Railway akan otomatis redeploy
```

---

## Pricing

- **Free Tier:** $5 credit per bulan
- **Hobby:** $5/bulan untuk lebih banyak resources
- **Pro:** $20/bulan untuk production

Untuk submission, free tier sudah cukup!

---

## Checklist

- [ ] Buat akun Railway
- [ ] Push code ke GitHub
- [ ] Deploy dari GitHub repo di Railway
- [ ] Configure environment variables (jika perlu)
- [ ] Upload model files (Volume atau Cloud Storage)
- [ ] Test aplikasi
- [ ] Setup Prometheus monitoring
- [ ] Update README dengan URL Railway

---

## Referensi

- Railway Docs: https://docs.railway.app
- Railway Pricing: https://railway.app/pricing
- Railway Discord: https://discord.gg/railway

---

## Catatan

- Railway lebih mudah daripada Heroku
- Tidak perlu kartu kredit untuk mulai
- Auto-deploy dari GitHub sangat praktis
- Built-in monitoring dan logs

