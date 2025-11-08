# Panduan Lengkap: Deploy ke Railway dengan Volume (Tanpa GCS)

Panduan step-by-step untuk deploy aplikasi ke Railway dan upload model menggunakan Railway Volume.

---

## Keuntungan Railway Volume

- ✅ **Tidak perlu billing** (gratis!)
- ✅ **Lebih sederhana** daripada GCS
- ✅ **Terintegrasi** dengan Railway
- ✅ **Mudah digunakan**

---

## Langkah 1: Deploy App ke Railway (Tanpa Model)

### 1.1 Push Code ke GitHub

```powershell
# Pastikan semua file sudah di-commit
git status

# Push ke GitHub (jika belum)
git push origin main
```

### 1.2 Deploy ke Railway

1. **Buka Railway:**
   - https://railway.app
   - Login dengan GitHub

2. **Create New Project:**
   - Klik **"New Project"**
   - Pilih **"Deploy from GitHub repo"**
   - Authorize Railway (jika pertama kali)
   - Pilih repository `placement-model`

3. **Railway akan otomatis:**
   - Detect Python app
   - Install dependencies
   - Deploy aplikasi

4. **Catat URL aplikasi:**
   - Railway akan memberikan URL (contoh: `https://placement-model.up.railway.app`)

---

## Langkah 2: Tambahkan Volume di Railway

### 2.1 Create Volume

1. **Di Railway Dashboard:**
   - Pilih project Anda
   - Klik **"New"** → **"Volume"**

2. **Configure Volume:**
   - **Name**: `model-storage` (atau nama lain)
   - **Size**: 1 GB (cukup untuk model)
   - Klik **"Add"**

3. **Mount Volume ke Service:**
   - Pilih service (Flask app)
   - Klik **"Settings"** → **"Volumes"**
   - Klik **"Add Volume"**
   - Pilih volume `model-storage`
   - **Mount Path**: `/models` (atau path lain)
   - Klik **"Add"**

---

## Langkah 3: Upload Model ke Volume

### Opsi A: Via Railway CLI (Recommended)

#### 3.1 Install Railway CLI

```powershell
# Via npm (jika sudah ada Node.js)
npm install -g @railway/cli

# Atau via PowerShell (Windows)
iwr https://railway.app/install.ps1 | iex
```

#### 3.2 Login ke Railway

```powershell
railway login
```

#### 3.3 Link Project

```powershell
# Di folder project
cd C:\bertrandcorneliussia-pipeline

# Link project
railway link
```

Pilih project yang sudah dibuat.

#### 3.4 Upload Model

```powershell
# Upload model ke volume
# Ganti /models dengan mount path yang Anda set
railway run --service YOUR_SERVICE_NAME -- \
  sh -c "mkdir -p /models/placement_model && \
         cp -r output/serving_model/* /models/placement_model/"

# Atau lebih sederhana, upload via Railway dashboard
```

### Opsi B: Via Railway Dashboard (Lebih Mudah)

1. **Buka Railway Dashboard:**
   - Pilih project → Service → **"Deployments"**

2. **Open Shell:**
   - Klik pada deployment terbaru
   - Klik **"Shell"** atau **"Connect"**

3. **Upload via Railway Web Interface:**
   - Railway tidak support direct file upload via web
   - Gunakan Railway CLI atau metode lain

### Opsi C: Via Git + Build (Paling Mudah)

**Cara termudah:** Commit model ke Git (jika < 100MB)

```powershell
# Update .gitignore untuk allow model files sementara
# Edit .gitignore, comment out output/ serving_model line

# Add model files
git add output/serving_model/
git commit -m "Add model files for Railway deployment"
git push origin main

# Railway akan otomatis redeploy dengan model files
```

**Catatan:** Setelah deploy berhasil, bisa remove model dari Git lagi.

---

## Langkah 4: Update App untuk Load dari Volume

### 4.1 Update app.py

File `app.py` sudah support local path. Untuk Railway Volume, kita perlu:

1. **Set Environment Variable:**
   - Di Railway dashboard → **"Variables"**
   - Add variable:
     - **Name**: `MODEL_PATH`
     - **Value**: `/models/placement_model` (atau mount path Anda)

2. **Update app.py untuk check volume path:**

File `app.py` sudah akan check `MODEL_PATH` environment variable. Pastikan model di volume berada di path yang benar.

---

## Langkah 5: Alternative - Commit Model ke Git

**Cara termudah untuk submission:** Commit model langsung ke Git.

### 5.1 Update .gitignore

```powershell
# Edit .gitignore
# Comment out atau remove line yang ignore output/serving_model
```

Atau temporary remove dari .gitignore:

```powershell
# Backup .gitignore
cp .gitignore .gitignore.backup

# Edit .gitignore, remove atau comment:
# output/
# *.pb
# dll yang related dengan model
```

### 5.2 Add Model Files

```powershell
# Add model files
git add output/serving_model/
git commit -m "Add model files for Railway deployment"
git push origin main
```

### 5.3 Set Environment Variable

Di Railway dashboard:
- **Name**: `MODEL_PATH`
- **Value**: `output/serving_model/1762435641` (path relatif dari root)

Atau biarkan default, app.py akan auto-detect.

### 5.4 Redeploy

Railway akan otomatis redeploy setelah push.

---

## Langkah 6: Test Aplikasi

### 6.1 Test Health Endpoint

```powershell
# Ganti URL dengan URL Railway Anda
curl https://YOUR_APP_URL.railway.app/health
```

Expected:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "transform_loaded": false
}
```

### 6.2 Test Prediction

Buka di browser:
```
https://YOUR_APP_URL.railway.app
```

Isi form dan test prediksi.

---

## Rekomendasi: Gunakan Git Commit (Paling Mudah)

Untuk submission Dicoding, cara **termudah** adalah:

1. **Commit model ke Git** (jika < 100MB)
2. **Push ke GitHub**
3. **Railway auto-deploy**
4. **Done!**

### Langkah Cepat:

```powershell
# 1. Update .gitignore (remove output/ serving_model)
# Edit .gitignore, comment out:
# output/
# *.pb
# dll

# 2. Add model
git add output/serving_model/
git commit -m "Add model files"
git push origin main

# 3. Railway akan auto-deploy
# 4. Test aplikasi
```

---

## Troubleshooting

### Error: "Model not found"

**Solusi:**
- Pastikan `MODEL_PATH` environment variable sudah di-set
- Pastikan model files sudah di-upload ke volume
- Cek logs di Railway dashboard

### Error: "Volume not mounted"

**Solusi:**
- Pastikan volume sudah di-mount ke service
- Pastikan mount path benar
- Redeploy service

### Error: "File too large for Git"

**Solusi:**
- Gunakan Railway Volume (Opsi A atau B)
- Atau compress model files terlebih dahulu
- Atau split menjadi beberapa commits

### Model tidak ter-load

**Solusi:**
- Cek logs di Railway dashboard
- Pastikan path model benar
- Pastikan model files ada di volume/Git

---

## Checklist

- [ ] Deploy app ke Railway
- [ ] Tambahkan Volume (opsional)
- [ ] Upload model files (via Git atau Volume)
- [ ] Set environment variables
- [ ] Test aplikasi
- [ ] Setup Prometheus monitoring

---

## Cost Estimation

### Railway:
- **Free tier**: $5 credit per bulan
- **Volume**: Included in free tier (1 GB)
- **Total**: **GRATIS** untuk submission!

---

## Referensi

- Railway Docs: https://docs.railway.app
- Railway Volumes: https://docs.railway.app/storage/volumes
- Railway CLI: https://docs.railway.app/develop/cli

---

## Catatan

- Railway Volume lebih mudah daripada GCS
- Untuk submission, commit model ke Git adalah cara termudah
- Model files akan ada di repository (perhatikan ukuran)

---

**Selamat! Aplikasi Anda sekarang sudah di-deploy ke Railway!** 🚀

