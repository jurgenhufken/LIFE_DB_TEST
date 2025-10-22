# LIFE_DB - Windsurf Setup Guide

## 🚀 Quick Start

### 1. Start Docker Stack (API, Postgres, Neo4j, Frontend)

**Terminal 1:**
```bash
cp .env.example .env
# Optioneel: pas API_TOKEN aan in .env
docker compose up -d --build
curl http://localhost:8081/healthz
```

Je moet `{"ok":true,...}` terugkrijgen.

**Poorten:**
- API → `http://localhost:8081`
- Frontend (Docker) → `http://localhost:5173`
- Neo4j → `http://localhost:7474` (login: neo4j / test12345)
- PostgreSQL → `localhost:5432`

### 2. Start Desktop Clipper

**Terminal 2:**
```bash
cd clipper_app
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Optie A: Expandable Clipper (aanbevolen - modern UI)**
```bash
python expandable_clipper.py
# Opens floating window with expand/collapse
```

**Optie B: Web Clipper (browser-based)**
```bash
python web_clipper.py
# Opens http://localhost:8888
```

**Optie C: Desktop Clipper (original Tkinter)**
```bash
python clipper.py
# Opens Tk window (als het werkt)
```

> **Note:** Als Tkinter niet werkt (macOS versie issues), gebruik de Web Clipper.

### 3. Gebruik de Clipper

**In de clipper:**
1. **API:** `http://localhost:8081`
2. **Token:** Leeg laten (of je API_TOKEN uit .env)
3. **Plak URL** → Kies categorie → **Clip → Backend**

### 4. Check Results

**Frontend:** Open `http://localhost:5174` (lokale dev) of `http://localhost:5173` (Docker)
- Tab **Lijst** → je net geclipte item moet zichtbaar zijn

**Neo4j Browser:** `http://localhost:7474`
```cypher
MATCH (i:Item) RETURN i LIMIT 5;
```

---

## 🎯 Windsurf Tasks (één-klik knoppen)

Gebruik **Terminal → Run Task...** voor:

- **Stack: up** - Start alle Docker containers
- **Stack: down** - Stop alle containers
- **Stack: logs** - Bekijk logs
- **Web Clipper** - Start web-based clipper
- **Desktop Clipper (Tkinter)** - Start Tk clipper (als het werkt)
- **API Health Check** - Test of API draait
- **Frontend: Local Dev** - Start frontend lokaal

---

## ⚠️ Veelgemaakte Valkuilen

### 1. Windsurf opent een preview voor clipper
❌ **Fout:** Browser preview voor `clipper.py`  
✅ **Fix:** Sluit de preview tab. Start clipper altijd met `python clipper.py` in terminal.

### 2. API unreachable / 404
❌ **Fout:** Oude stack draait nog  
✅ **Fix:**
```bash
docker ps
docker compose down
docker compose up -d
```

### 3. Token fout (401/403)
❌ **Fout:** Token mismatch  
✅ **Fix:** Vul in clipper/Frontend hetzelfde `API_TOKEN` als in `.env`

### 4. Tkinter ontbreekt
❌ **Fout:** `No module named tkinter`  
✅ **Fix:**
```bash
# Test:
python3 -c "import tkinter; print('ok')"

# macOS (pyenv):
brew install tcl-tk
# En Python opnieuw bouwen met Tk

# Of gebruik standaard Python van python.org
```

### 5. macOS versie issue met Tkinter
❌ **Fout:** `macOS 26 (2600) or later required`  
✅ **Fix:** Gebruik de **Web Clipper** in plaats van Tkinter:
```bash
cd clipper_app
source .venv/bin/activate
python web_clipper.py
```

---

## 📁 Project Structuur

```
LIFE_DB_TEST/
├── .vscode/
│   └── tasks.json          # Windsurf run tasks
├── backend/
│   ├── app.py              # FastAPI + SQLAlchemy
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   ├── Dockerfile
│   ├── package.json
│   └── .env.local          # Local dev config
├── clipper_app/
│   ├── clipper.py          # Tkinter desktop app
│   ├── web_clipper.py      # Web-based clipper (fallback)
│   ├── simple_clipper.py   # Terminal-based
│   └── requirements.txt
├── db/
│   └── init.sql            # PostgreSQL schema
├── docker-compose.yml
├── .env                    # Environment variables
└── README.md
```

---

## 🔧 Development Workflow

### Start Everything
```bash
# Terminal 1: Docker stack
docker compose up -d --build

# Terminal 2: Frontend (local dev)
cd frontend
npm run dev

# Terminal 3: Clipper
cd clipper_app
source .venv/bin/activate
python web_clipper.py
```

### Stop Everything
```bash
docker compose down
# Ctrl+C in frontend terminal
# Ctrl+C in clipper terminal
```

### View Logs
```bash
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f neo4j
```

### Database Access
```bash
# PostgreSQL
docker compose exec postgres psql -U lifedb -d lifedb

# Neo4j
# Open http://localhost:7474
# Login: neo4j / test12345
```

---

## 🎨 Features

### v4 Quick Wins
- ✅ **Full-text search** (Postgres GIN/tsvector)
- ✅ **URL canonicalisatie + dedupe** (url_norm UNIQUE)
- ✅ **Dark mode** + keyboard shortcuts (`/` focus, `d` dark mode)
- ✅ **Graph kleurcodering** per node-type
- ✅ **Export CSV** (naast JSON/NDJSON)
- ✅ **Health metrics** (`/healthz`)
- ✅ **Simple Admin** (categorie hernoemen, tags merge)

### Clipper Options
1. **Web Clipper** - Modern web UI op `http://localhost:8888`
2. **Desktop Clipper** - Tkinter GUI (als het werkt)
3. **Simple Clipper** - Terminal-based interactief

---

## 🌐 URLs Overzicht

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8081 | - |
| Frontend (Docker) | http://localhost:5173 | - |
| Frontend (Local) | http://localhost:5174 | - |
| Web Clipper | http://localhost:8888 | - |
| Neo4j Browser | http://localhost:7474 | neo4j / test12345 |
| PostgreSQL | localhost:5432 | lifedb / lifedb |

---

## 📝 API Endpoints

```bash
# Health check
curl http://localhost:8081/healthz

# List items
curl http://localhost:8081/items

# Capture
curl -X POST http://localhost:8081/capture \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","category":"Test","tags":["demo"]}'

# Categories
curl http://localhost:8081/categories

# Export
curl http://localhost:8081/export?fmt=csv
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
lsof -i :8081  # API
lsof -i :5173  # Frontend
lsof -i :7474  # Neo4j
lsof -i :5432  # PostgreSQL

# Kill process
kill -9 <PID>
```

### Docker issues
```bash
docker compose down -v  # Remove volumes
docker system prune -a  # Clean everything
docker compose up -d --build
```

### Frontend niet bereikbaar
```bash
# Check if running
docker compose ps

# Restart
docker compose restart frontend

# Or run locally
cd frontend
npm run dev
```

---

## ✅ Success Checklist

- [ ] Docker Desktop draait
- [ ] `docker compose up -d --build` succesvol
- [ ] `curl http://localhost:8081/healthz` geeft `{"ok":true}`
- [ ] Frontend bereikbaar op http://localhost:5174
- [ ] Neo4j bereikbaar op http://localhost:7474
- [ ] Clipper draait (web of desktop)
- [ ] Test clip: URL → categorie → Clip → Backend
- [ ] Item zichtbaar in frontend (tab Lijst)
- [ ] Item zichtbaar in Neo4j: `MATCH (i:Item) RETURN i LIMIT 5`

---

**Veel succes! 🚀**
