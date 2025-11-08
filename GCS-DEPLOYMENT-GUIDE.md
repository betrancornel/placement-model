# Panduan Lengkap: Deploy Model ke Railway dengan Google Cloud Storage

Panduan step-by-step untuk upload model ke Google Cloud Storage dan deploy aplikasi ke Railway.

---

## Langkah 1: Setup Google Cloud Platform (GCP)

### 1.1 Buat Akun Google Cloud

1. Buka https://cloud.google.com/
2. Klik **"Get started for free"**
3. Daftar dengan akun Google Anda
4. Anda akan mendapat **$300 free credit** untuk 90 hari

### 1.2 Buat Project di GCP

1. Buka https://console.cloud.google.com/
2. Klik **"Select a project"** → **"New Project"**
3. Isi:
   - **Project name**: `placement-model` (atau nama lain)
   - **Location**: Pilih organization (bisa skip)
4. Klik **"Create"**
5. Catat **Project ID** (akan digunakan nanti)

### 1.3 Install Google Cloud SDK

#### Windows:

1. Download installer dari: https://cloud.google.com/sdk/docs/install
2. Jalankan installer
3. Ikuti wizard instalasi
4. Restart terminal/PowerShell

#### Verifikasi Instalasi:

```powershell
gcloud --version
```

### 1.4 Login ke Google Cloud

```powershell
gcloud auth login
```

Ini akan membuka browser untuk login. Setelah login, kembali ke terminal.

### 1.5 Set Project

```powershell
# Ganti YOUR_PROJECT_ID dengan Project ID Anda
gcloud config set project YOUR_PROJECT_ID
```

Verifikasi:
```powershell
gcloud config get-value project
```

---

## Langkah 2: Buat Bucket di Google Cloud Storage

### 2.1 Buat Bucket via Console (Recommended)

1. Buka https://console.cloud.google.com/storage
2. Klik **"CREATE BUCKET"**
3. Isi form:
   - **Name**: `bertrandcorneliussia-ml-models` (harus unik global)
   - **Location type**: `Region`
   - **Location**: `asia-southeast2` (Jakarta) atau pilih region terdekat
   - **Storage class**: `Standard`
   - **Access control**: `Fine-grained`
   - **Protection tools**: Default (bisa skip)
4. Klik **"CREATE"**

### 2.2 Buat Bucket via CLI (Alternatif)

```powershell
# Ganti YOUR_BUCKET_NAME dengan nama bucket (harus unik)
gsutil mb -l asia-southeast2 gs://YOUR_BUCKET_NAME
```

**Catatan:** Nama bucket harus unik secara global. Gunakan nama yang unik seperti: `bertrandcorneliussia-ml-models-2024`

---

## Langkah 3: Upload Model ke Google Cloud Storage

### 3.1 Enable Billing (Jika Perlu)

1. Buka https://console.cloud.google.com/billing
2. Link billing account (free tier tetap gratis, tapi perlu enable billing)
3. Atau skip jika hanya untuk testing

### 3.2 Upload Model Files

```powershell
# Pastikan di folder project
cd C:\bertrandcorneliussia-pipeline

# Upload model ke GCS
# Ganti YOUR_BUCKET_NAME dengan nama bucket Anda
gsutil -m cp -r output/serving_model/ gs://YOUR_BUCKET_NAME/placement_model/

# Contoh:
# gsutil -m cp -r output/serving_model/ gs://bertrandcorneliussia-ml-models/placement_model/
```

**Penjelasan:**
- `-m`: Parallel upload (lebih cepat)
- `-r`: Recursive (upload folder dan isinya)
- `output/serving_model/`: Folder model lokal
- `gs://BUCKET_NAME/placement_model/`: Path di GCS

### 3.3 Verifikasi Upload

```powershell
# List files di bucket
gsutil ls -r gs://YOUR_BUCKET_NAME/placement_model/
```

Atau cek via Console: https://console.cloud.google.com/storage/browser/YOUR_BUCKET_NAME

---

## Langkah 4: Atur Akses Bucket

### Opsi A: Public Access (Mudah, tapi kurang aman)

1. Buka https://console.cloud.google.com/storage/browser/YOUR_BUCKET_NAME
2. Klik pada folder `placement_model/`
3. Klik tab **"Permissions"**
4. Klik **"GRANT ACCESS"**
5. Isi:
   - **New principals**: `allUsers`
   - **Select a role**: `Storage Object Viewer`
6. Klik **"SAVE"**
7. Konfirmasi "Allow public access"

### Opsi B: Service Account (Recommended untuk Production)

1. Buat Service Account:
   ```powershell
   # Ganti YOUR_PROJECT_ID dengan Project ID
   gcloud iam service-accounts create railway-service-account \
       --display-name="Railway Service Account" \
       --project=YOUR_PROJECT_ID
   ```

2. Berikan permission:
   ```powershell
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
       --member="serviceAccount:railway-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/storage.objectViewer"
   ```

3. Buat key:
   ```powershell
   gcloud iam service-accounts keys create key.json \
       --iam-account=railway-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

4. Upload key ke Railway sebagai environment variable `GOOGLE_APPLICATION_CREDENTIALS`

**Untuk submission, Opsi A (Public Access) sudah cukup.**

---

## Langkah 5: Update Kode untuk Download dari GCS

File `app.py` sudah di-update untuk support GCS. Pastikan:

1. ✅ `requirements.txt` sudah include `google-cloud-storage==2.10.0`
2. ✅ `app.py` sudah di-update untuk download dari GCS

### 5.1 Test Lokal (Opsional)

Untuk test lokal tanpa GCS, pastikan folder `output/serving_model/` ada. App akan load dari local path.

---

## Langkah 6: Setup Railway

### 6.1 Deploy ke Railway

1. Buka https://railway.app
2. Login dengan GitHub
3. Klik **"New Project"**
4. Pilih **"Deploy from GitHub repo"**
5. Pilih repository `placement-model`
6. Railway akan otomatis detect dan deploy

### 6.2 Set Environment Variables

1. Di Railway dashboard, pilih project
2. Klik tab **"Variables"**
3. Tambahkan environment variables:

   **Variable 1:**
   - **Name**: `MODEL_BUCKET`
   - **Value**: `bertrandcorneliussia-ml-models` (nama bucket Anda)

   **Variable 2:**
   - **Name**: `MODEL_BLOB_PREFIX`
   - **Value**: `placement_model/` (prefix folder di bucket)

   **Variable 3 (Opsional - jika menggunakan Service Account):**
   - **Name**: `GOOGLE_APPLICATION_CREDENTIALS`
   - **Value**: (paste isi file key.json)

### 6.3 Get App URL

1. Di Railway dashboard, pilih service
2. Klik **"Settings"** → **"Networking"**
3. Generate domain atau tambahkan custom domain
4. Copy URL (contoh: `https://placement-model.up.railway.app`)

---

## Langkah 7: Test Aplikasi

### 7.1 Test Health Endpoint

```powershell
# Ganti URL dengan URL Railway Anda
curl https://YOUR_APP_URL.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "transform_loaded": false
}
```

### 7.2 Test Prediction

Buka di browser:
```
https://YOUR_APP_URL.railway.app
```

Isi form dan test prediksi.

### 7.3 Test Metrics

```powershell
curl https://YOUR_APP_URL.railway.app/metrics
```

---

## Langkah 8: Setup Prometheus Monitoring

### 8.1 Update Prometheus Config

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

### 8.2 Jalankan Prometheus

```bash
# Download Prometheus atau gunakan Docker:
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 8.3 Akses Prometheus UI

Buka: `http://localhost:9090`

---

## Troubleshooting

### Error: "Model not found"

**Solusi:**
- Pastikan `MODEL_BUCKET` dan `MODEL_BLOB_PREFIX` sudah di-set di Railway
- Pastikan model sudah di-upload ke GCS
- Cek logs di Railway dashboard

### Error: "Access denied"

**Solusi:**
- Pastikan bucket sudah di-set public access (Opsi A)
- Atau setup Service Account dengan benar (Opsi B)

### Error: "google-cloud-storage not installed"

**Solusi:**
- Pastikan `requirements.txt` include `google-cloud-storage==2.10.0`
- Redeploy di Railway

### Error: "Bucket not found"

**Solusi:**
- Pastikan nama bucket benar
- Pastikan project ID benar
- Pastikan sudah login dengan `gcloud auth login`

### Model download terlalu lama

**Solusi:**
- Gunakan region yang dekat dengan Railway server
- Consider menggunakan CDN
- Atau cache model di Railway Volume

---

## Checklist

- [ ] Buat akun Google Cloud
- [ ] Buat project di GCP
- [ ] Install Google Cloud SDK
- [ ] Login dengan `gcloud auth login`
- [ ] Set project dengan `gcloud config set project`
- [ ] Buat bucket di GCS
- [ ] Upload model ke GCS
- [ ] Set public access (atau Service Account)
- [ ] Update `app.py` dan `requirements.txt`
- [ ] Push ke GitHub
- [ ] Deploy ke Railway
- [ ] Set environment variables di Railway
- [ ] Test aplikasi
- [ ] Setup Prometheus monitoring

---

## Cost Estimation

### Google Cloud Storage:

- **Storage**: ~$0.020 per GB per bulan
- **Operations**: Free untuk operasi standar
- **Network egress**: Free untuk 1 GB pertama per bulan

**Estimasi untuk model ~50MB:**
- Storage: $0.001 per bulan
- **Total: ~$0.01 per bulan** (sangat murah!)

### Railway:

- **Free tier**: $5 credit per bulan
- **Hobby**: $5/bulan untuk lebih banyak resources

**Total estimasi: < $1 per bulan** untuk submission!

---

## Referensi

- Google Cloud Storage Docs: https://cloud.google.com/storage/docs
- Railway Docs: https://docs.railway.app
- gcloud CLI Docs: https://cloud.google.com/sdk/docs

---

## Catatan Penting

1. **Nama bucket harus unik global** - gunakan nama yang unik
2. **Public access kurang aman** - untuk production, gunakan Service Account
3. **Model files besar** - pertimbangkan kompresi jika perlu
4. **Region selection** - pilih region yang dekat dengan Railway server
5. **Cost monitoring** - monitor penggunaan di GCP Console

---

## Quick Command Reference

```powershell
# Login ke GCP
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Buat bucket
gsutil mb -l asia-southeast2 gs://YOUR_BUCKET_NAME

# Upload model
gsutil -m cp -r output/serving_model/ gs://YOUR_BUCKET_NAME/placement_model/

# List files
gsutil ls -r gs://YOUR_BUCKET_NAME/placement_model/

# Set public access (via console lebih mudah)
```

---

Selamat! Model Anda sekarang sudah di-deploy ke Railway dengan model di Google Cloud Storage! 🚀

