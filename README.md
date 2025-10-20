# 🔖 LIFE_DB — All-in-One v4

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Personal knowledge management system met full-text search, graph visualization en smart clipping.**

# LIFE_DB — All-in-One (Windsurf) v4 (Quick Wins)

**Nieuw in v4 (quick wins):**
- **Full‑text search (Postgres GIN/tsvector)** op titel, beschrijving, URL.
- **URL canonicalisatie + dedupe** (kolom `url_norm` UNIQUE, verwijdert utm/fbclid/fragmenten).
- **Dark mode** + **keyboard shortcuts**: `/` focust zoeken, `d` togglet dark mode.
- **Graph kleurcodering** per node‑type (Item/Domain/Category/Tag).
- **Export CSV** (naast JSON/NDJSON).
- **Health metrics** (`/healthz`) met item/tag/categorie‑counts.
- **Simple Admin**: categorie hernoemen, tags samenvoegen (merge).

## 🚀 Quick Start

### 1. Start Docker Stack
```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8081/healthz  # Should return {"ok":true}
```

**Services:**
- Frontend: http://localhost:5173 (Docker) of http://localhost:5174 (local dev)
- API: http://localhost:8081
- Neo4j: http://localhost:7474 (neo4j / test12345)
- PostgreSQL: localhost:5432

### 2. Start Clipper

**Web Clipper (aanbevolen - werkt altijd):**
```bash
cd clipper_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python web_clipper.py
# Opens http://localhost:8888
```

**Desktop Clipper (Tkinter - optioneel):**
```bash
python clipper.py
# Opens Tk window (als Tkinter werkt)
```

### 3. Gebruik Windsurf Tasks

Open **Terminal → Run Task...** en kies:
- **Stack: up** - Start Docker
- **Web Clipper** - Start clipper
- **API Health Check** - Test API

## 📖 Volledige Documentatie

Zie **[WINDSURF_SETUP.md](./WINDSURF_SETUP.md)** voor:
- Stap-voor-stap setup
- Troubleshooting
- Development workflow
- API endpoints
- Veelgemaakte valkuilen

## ⚡ Snelle Test

```bash
# Clip een URL via API
curl -X POST http://localhost:8081/capture \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","category":"Test","tags":["demo"]}'

# Check in frontend
open http://localhost:5174

# Check in Neo4j
open http://localhost:7474
# Run: MATCH (i:Item) RETURN i LIMIT 5;
```

## 🔧 Troubleshooting

**API niet bereikbaar?**
```bash
docker compose down
docker compose up -d --build
```

**Tkinter werkt niet?**
Gebruik de Web Clipper: `python web_clipper.py`

**Meer hulp?** Zie [WINDSURF_SETUP.md](./WINDSURF_SETUP.md)

