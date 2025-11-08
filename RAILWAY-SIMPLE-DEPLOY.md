# Panduan Cepat: Deploy ke Railway (Cara Termudah)

Panduan paling sederhana untuk deploy aplikasi ke Railway tanpa perlu GCS atau Volume.

---

## Opsi: Commit Model ke Git (Paling Mudah)

### Langkah 1: Update .gitignore

Kita perlu allow model files untuk di-commit. Edit `.gitignore`:

**Comment out atau remove baris:**
```
# output/
# *.pb
```

Atau buat exception untuk serving_model:
```
output/
!output/serving_model/
*.pb
!output/serving_model/**/*.pb
```

### Langkah 2: Add Model Files ke Git

```powershell
# Add model files
git add output/serving_model/

# Commit
git commit -m "Add model files for Railway deployment"

# Push
git push origin main
```

### Langkah 3: Deploy ke Railway

1. **Buka Railway:**
   - https://railway.app
   - Login dengan GitHub

2. **New Project:**
   - Klik **"New Project"**
   - Pilih **"Deploy from GitHub repo"**
   - Pilih repository

3. **Railway akan otomatis:**
   - Detect Python app
   - Install dependencies
   - Deploy dengan model files

### Langkah 4: Set Environment Variables (Opsional)

Di Railway dashboard → Variables:
- **MODEL_PATH**: `output/serving_model/1762435641` (path ke model)

Atau biarkan default, app.py akan auto-detect.

### Langkah 5: Test

```powershell
# Test health
curl https://YOUR_APP_URL.railway.app/health

# Test di browser
https://YOUR_APP_URL.railway.app
```

---

## Jika Model Terlalu Besar (> 100MB)

Gunakan Railway Volume atau compress model terlebih dahulu.

---

## Checklist

- [ ] Update .gitignore
- [ ] Add model files ke Git
- [ ] Push ke GitHub
- [ ] Deploy ke Railway
- [ ] Test aplikasi

---

**Ini adalah cara termudah untuk submission!** 🚀

