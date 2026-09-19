<div align="center">

# 🔒 LocalSec-AI

### Local AI Log Analyzer for Cybersecurity

**100% on-premise · Zero data leaks · RAG-powered threat detection**

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-1.12-FF6B6B?style=for-the-badge)](https://qdrant.tech)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen2.5-black?style=for-the-badge)](https://ollama.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 🎯 Problem

Bank, səhiyyə və dövlət qurumları **məxfi log məlumatlarını** bulud əsaslı AI alətlərinə (ChatGPT, Snyk, SIEM) göndərə bilmir. **GDPR, HIPAA** və daxili təhlükəsizlik siyasətləri buna icazə vermir.

Mövcud həllər (Splunk, Snyk, Datadog) **bulud-only**-dir və ya **bahalı**dır. Kiçik və orta şirkətlər üçün **lokal, sərfəli və təhlükəsiz** bir alternativ yoxdur.

## 💡 Həll

**LocalSec-AI** — bu, tam lokal işləyən, RAG (Retrieval-Augmented Generation) əsaslı bir kiber təhlükəsizlik log analizatorudur:

- 📂 Log faylını API-yə yükləyirsən
- 🧠 AI analiz edir və **Azərbaycan dilində** cavab verir
- 🔐 Heç bir məlumat xaricə getmir (**100% on-premise**)
- 🎯 MITRE ATT&CK taktikasını aşkarlayır (T1110 Brute Force və s.)

---

## 🏗️ Arxitektura

```
┌─────────────────────────────────────────────────────────────────┐
│                         İSTİFADƏÇİ                              │
│                  (Swagger UI / curl / Frontend)                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP POST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI (REST API)                           │
│              /api/v1/ingest · /api/v1/analyze                    │
└─────────┬───────────────────────────────────┬───────────────────┘
          │                                   │
          │ 1. Log parse                      │ 3. RAG Query
          ▼                                   ▼
┌──────────────────────┐            ┌──────────────────────┐
│   Log Parser         │            │   Qdrant (Vector DB) │
│   (Regex → Dict)     │            │   768-dim embeddings │
└──────────┬───────────┘            └──────────┬───────────┘
           │                                   │
           │ 2. Embed                          │ 4. Context
           ▼                                   ▼
┌──────────────────────┐            ┌──────────────────────┐
│  nomic-embed-text    │            │  Qwen 2.5 7B (LLM)   │
│  (Ollama)            │            │  (Ollama)            │
└──────────────────────┘            └──────────┬───────────┘
                                               │ 5. Answer
                                               ▼
                                        ✅ Azərbaycan dilində
                                           SOC analitik cavabı
```

**Bütün komponentlər lokal olaraq işləyir — heç bir xarici API çağırışı yoxdur.**

---

## 🛠️ Texnologiya Stack

| Layer | Texnologiya | İstifadə məqsədi |
|-------|-------------|------------------|
| **API** | FastAPI + Uvicorn | REST endpoints |
| **LLM** | Ollama + Qwen 2.5 7B | Log analizi |
| **Embeddings** | nomic-embed-text | Mətn → 768-dim vektor |
| **Vector DB** | Qdrant | Oxşar logların axtarışı |
| **Validation** | Pydantic v2 | Data modelləri |
| **Deployment** | Docker Compose | 2 konteyner (API + Qdrant) |
| **Language** | Python 3.11 | Backend |

---

## ⚡ Sürətli Başlanğıc

### Tələblər
- [Docker Desktop](https://docker.com/products/docker-desktop) (Windows/Mac/Linux)
- [Ollama](https://ollama.com) (modelləri yükləmək üçün)
- 8 GB RAM (minimum), 16 GB (tövsiyə)

### Quraşdırma (3 addım)

**1. Repo-nu klonla:**
```bash
git clone https://github.com/SrTural/localsec-ai.git
cd localsec-ai
```

**2. Ollama modellərini yüklə:**
```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

**3. Sistemi işə sal:**
```bash
docker-compose up -d
```

**4. Yoxla:**
```bash
docker-compose ps
# Hər iki konteyner "Up" olmalıdır
```

🎉 **Hazırdır!** Swagger UI-ı aç: **http://localhost:8000/docs**

---

## 📖 İstifadə Nümunəsi

### 1️⃣ Log faylını yüklə (`/api/v1/ingest`)

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@data/sample_auth.log"
```

**Cavab:**
```json
{
  "status": "success",
  "ingested_count": 7
}
```

### 2️⃣ AI-dan sual ver (`/api/v1/analyze`)

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Son 1 saatda hansı şübhəli login cəhdləri olub?",
    "limit": 5
  }'
```

**Cavab:**
```json
{
  "question": "Son 1 saatda hansı şübhəli login cəhdləri olub?",
  "context_used": 5,
  "answer": "10.0.0.12 IP-dən admin istifadəçisi 2 dəfə şübhəli login cəhd etdi (T1110 Brute Force). 192.168.1.5 IP-dən root istifadəçisi 3 dəfə şübhəli login cəhd etdi. Tövsiyə: 192.168.1.5 IP-ni bloklayın və MFA aktiv edin."
}
```

---

## 🎯 Xüsusiyyətlər

- ✅ **100% Lokal** — heç bir məlumat buluda getmir (GDPR/HIPAA uyğun)
- ✅ **RAG Arxitekturası** — kontekst əsaslı dəqiq cavablar
- ✅ **Azərbaycan dili** — yerli SOC komandaları üçün
- ✅ **MITRE ATT&CK** aşkarlaması
- ✅ **Genişlənə bilən** — yeni log formatları əlavə edilə bilər
- ✅ **Docker-first** — 1 əmrlə quraşdırma
- ✅ **Açıq mənbə** (MIT License)

---

## 📊 Test Nəticələri

| Metrik | Nəticə |
|--------|--------|
| Log faylının yüklənməsi | ~0.5 saniyə |
| Vektorlaşdırma | ~1 saniyə / 7 log |
| AI cavabı (ilk sorğu) | ~30-60 saniyə (model load) |
| AI cavabı (sonrakı) | ~3-5 saniyə |
| Yaddaş istifadəsi | ~5.5 GB (Qwen 2.5 7B) |

---

## 🗺️ Gələcək Planlar

- [ ] Frontend (React/Next.js) — vizual dashboard
- [ ] Daha çox log formatları (Windows Event Log, syslog, JSON)
- [ ] Real-time streaming analizi (Kafka inteqrasiyası)
- [ ] Slack/Telegram xəbərdarlıqları
- [ ] PDF hesabat ixracı
- [ ] Multi-tenant dəstək

---

## 🤝 Töhfə Vermə

Töhfələrə açıqdır! Pull request göndərməzdən əvvəl:

1. Repo-nu fork et
2. Yeni branch yarat (`git checkout -b feature/yeni-xususiyyet`)
3. Dəyişiklikləri commit et (`git commit -m 'Yeni xüsusiyyət əlavə edildi'`)
4. Branch-i push et (`git push origin feature/yeni-xususiyyet`)
5. Pull Request aç

---

## 📄 Lisenziya

Bu layihə **MIT License** altında yayılmışdır. Ətraflı məlumat üçün [LICENSE](LICENSE) faylına bax.

---

## 👨‍💻 Müəllif

**Tural Dadaşov**
- GitHub: [@SrTural](https://github.com/SrTural)
- LinkedIn: [Tural Dadaşov](https://linkedin.com/in/...)
- Layihə: [LocalSec-AI](https://github.com/SrTural/localsec-ai)

---

<div align="center">

### ⭐ Bu layihəni bəyəndinizsə, ulduz verin! ⭐

**Made with 🔒 in Azerbaijan**

</div>
