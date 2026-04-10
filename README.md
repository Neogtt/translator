# Cheviri AI (MVP)

Bu uygulama, yabancı dilde gelen müşteri mesajlarını:

1. Dilini tespit eder
2. Türkçeye çevirir
3. Kısa özet çıkarır
4. Senin yazdığın Türkçe cevabı geliştirir
5. Müşterinin diline, seçtiğin tona (formal/informal/neutral) göre geri çevirir

## Kurulum

1) Sanal ortam (opsiyonel ama önerilir):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2) Paketleri yükle:

```powershell
pip install -r requirements.txt
```

3) API key ayarla:

- `.env.example` dosyasını `.env` olarak kopyala
- `OPENAI_API_KEY` değerini gir

## Çalıştırma

```powershell
streamlit run app.py
```

Tarayıcıda açılan ekrandan:
- müşteri mesajını yaz
- kendi Türkçe cevap taslağını yaz
- tonu seç (`formal`, `neutral`, `informal`)
- "Çevir ve Cevap Üret" butonuna bas

