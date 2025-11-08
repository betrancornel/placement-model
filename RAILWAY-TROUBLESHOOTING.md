# Troubleshooting Railway Deployment Error

## Error: "failed to push production-asia-southeast1... resumable blob upload invalid"

Error ini biasanya terjadi karena:
1. **Build terlalu besar** (TensorFlow + model files)
2. **Network timeout** saat push ke registry
3. **Registry issue** di Railway

---

## Solusi 1: Retry Deployment (Coba Dulu)

1. **Di Railway Dashboard:**
   - Pilih deployment yang gagal
   - Klik **"Redeploy"** atau **"Retry"**
   - Tunggu deployment ulang

2. **Atau trigger redeploy:**
   - Push commit kosong ke GitHub:
   ```powershell
   git commit --allow-empty -m "Trigger redeploy"
   git push origin main
   ```

---

## Solusi 2: Reduce Build Size

### 2.1 Exclude Large Files dari Build

Update `.railwayignore` atau pastikan `.gitignore` sudah benar:

```gitignore
# Exclude large files yang tidak diperlukan untuk deployment
output/bertrandcorneliussia-pipeline/
*.gz
*.tfrecord
*.whl
data/
notebook.ipynb
```

### 2.2 Optimize Requirements

TensorFlow sangat besar. Pertimbangkan:

1. **Gunakan TensorFlow Lite** (lebih kecil) - tapi perlu modifikasi code
2. **Atau biarkan** - Railway biasanya handle dengan baik

---

## Solusi 3: Change Build Settings

### 3.1 Update railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install --no-cache-dir -r requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3.2 Atau Remove railway.json

Hapus `railway.json` dan biarkan Railway auto-detect.

---

## Solusi 4: Check Repository Size

```powershell
# Cek ukuran repository
git count-objects -vH

# Cek file terbesar
git ls-files | xargs ls -la | sort -k5 -rn | head -20
```

Jika repository terlalu besar (> 500MB), pertimbangkan:
- Remove model files dari Git
- Gunakan Railway Volume atau GCS

---

## Solusi 5: Simplify Deployment

### 5.1 Remove Model dari Git (Gunakan Volume)

1. **Remove model dari Git:**
   ```powershell
   git rm -r --cached output/serving_model/
   git commit -m "Remove model files from Git"
   git push origin main
   ```

2. **Upload model ke Railway Volume:**
   - Di Railway dashboard → Add Volume
   - Upload model files via Railway CLI atau web interface

3. **Set environment variable:**
   - `MODEL_PATH`: `/models/placement_model`

### 5.2 Atau Gunakan GCS

Ikuti panduan di `GCS-DEPLOYMENT-GUIDE.md`

---

## Solusi 6: Contact Railway Support

Jika semua solusi di atas tidak bekerja:

1. **Cek Railway Status:**
   - https://status.railway.app

2. **Contact Support:**
   - Railway Discord: https://discord.gg/railway
   - Atau email support

---

## Quick Fix (Recommended)

**Coba ini dulu:**

1. **Retry deployment** di Railway dashboard
2. **Atau push commit kosong:**
   ```powershell
   git commit --allow-empty -m "Retry deployment"
   git push origin main
   ```

3. **Jika masih error, remove model dari Git:**
   ```powershell
   git rm -r --cached output/serving_model/
   git commit -m "Remove model files to reduce build size"
   git push origin main
   ```

4. **Deploy tanpa model dulu**, lalu upload model via Volume

---

## Alternative: Use Render.com

Jika Railway terus bermasalah, bisa coba Render.com:

1. Buka https://render.com
2. Deploy from GitHub
3. Similar dengan Railway, tapi mungkin lebih stabil

---

## Catatan

- Error ini biasanya temporary (network/registry issue)
- Retry biasanya menyelesaikan masalah
- Jika persist, reduce build size dengan remove model files

