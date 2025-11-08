# Cara Enable Billing di Google Cloud Platform

## Langkah 1: Enable Billing Account

1. **Buka Google Cloud Console:**
   - https://console.cloud.google.com/billing

2. **Link Billing Account:**
   - Jika sudah punya billing account, pilih dan link ke project
   - Jika belum, klik **"CREATE ACCOUNT"**

3. **Isi Form:**
   - **Account name**: Nama billing account (misalnya: "My Billing Account")
   - **Country**: Pilih negara Anda
   - **Time zone**: Pilih timezone
   - Klik **"CONTINUE"**

4. **Add Payment Method:**
   - Masukkan kartu kredit/debit
   - **Jangan khawatir!** Google memberikan **$300 free credit** untuk 90 hari
   - Setelah $300 habis, baru akan di-charge
   - Untuk penggunaan kecil seperti ini, kemungkinan besar tidak akan di-charge sama sekali

5. **Verify dan Submit:**
   - Review informasi
   - Klik **"SUBMIT AND ENABLE BILLING"**

## Langkah 2: Link Billing ke Project

1. **Buka Project Settings:**
   - https://console.cloud.google.com/billing?project=sanguine-healer-477606-k7

2. **Select Billing Account:**
   - Pilih billing account yang sudah dibuat
   - Klik **"SET ACCOUNT"**

## Catatan Penting:

- **Free Tier:** Google Cloud memberikan $300 free credit untuk 90 hari
- **Tidak akan di-charge:** Untuk penggunaan kecil seperti model storage, kemungkinan besar tidak akan di-charge
- **Bisa di-nonaktifkan:** Billing account bisa di-nonaktifkan kapan saja
- **Cost estimation:** Model storage ~50MB = ~$0.01 per bulan

## Alternatif: Buat Project Baru dengan Billing

Jika tidak ingin enable billing di project saat ini:

1. **Buat project baru:**
   ```powershell
   gcloud projects create placement-model-project --name="Placement Model"
   ```

2. **Set project:**
   ```powershell
   gcloud config set project placement-model-project
   ```

3. **Enable billing untuk project baru:**
   - Buka: https://console.cloud.google.com/billing
   - Link billing account ke project baru

## Setelah Billing Enabled:

Lanjutkan dengan membuat bucket:
```powershell
gsutil mb -l asia-southeast2 gs://bertrandcorneliussia-ml-models
```

---

**Tips:** Untuk submission Dicoding, enable billing adalah opsi terbaik karena:
- Free credit $300 sudah lebih dari cukup
- Cost untuk model storage sangat murah (~$0.01/bulan)
- Bisa di-nonaktifkan setelah selesai

