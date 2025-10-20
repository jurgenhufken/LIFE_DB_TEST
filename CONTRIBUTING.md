# Contributing to LIFE_DB

Bedankt voor je interesse in LIFE_DB! 🎉

## Development Setup

### Vereisten
- Docker Desktop
- Python 3.9+
- Node.js 18+
- Git

### Quick Start

1. **Clone de repository**
```bash
git clone https://github.com/jurgenhufken/LIFE_DB_TEST.git
cd LIFE_DB_TEST
```

2. **Start de stack**
```bash
cp .env.example .env
docker compose up -d --build
```

3. **Ontwikkel lokaal**
```bash
# Frontend
cd frontend
npm install
npm run dev

# Clipper
cd clipper_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python clipper.py
```

## Project Structuur

```
LIFE_DB_TEST/
├── backend/          # FastAPI + SQLAlchemy
├── frontend/         # React + TypeScript + Vite
├── clipper_app/      # Desktop & Web clippers
├── db/              # PostgreSQL schema
└── docs/            # Documentatie
```

## Development Workflow

### Branch Naming
- `feature/naam` - Nieuwe features
- `fix/naam` - Bug fixes
- `docs/naam` - Documentatie updates
- `refactor/naam` - Code refactoring

### Commit Messages
Gebruik conventional commits:
- `feat:` - Nieuwe feature
- `fix:` - Bug fix
- `docs:` - Documentatie
- `style:` - Formatting
- `refactor:` - Code refactoring
- `test:` - Tests toevoegen
- `chore:` - Maintenance

Voorbeelden:
```
feat: Add full-text search to items endpoint
fix: Resolve Tkinter width parameter issue
docs: Update WINDSURF_SETUP.md with troubleshooting
```

### Pull Requests

1. **Fork de repository**
2. **Maak een feature branch**
   ```bash
   git checkout -b feature/mijn-feature
   ```
3. **Commit je changes**
   ```bash
   git commit -m "feat: Add awesome feature"
   ```
4. **Push naar je fork**
   ```bash
   git push origin feature/mijn-feature
   ```
5. **Open een Pull Request**

### PR Checklist
- [ ] Code volgt bestaande style
- [ ] Tests toegevoegd (indien van toepassing)
- [ ] Documentatie bijgewerkt
- [ ] Commit messages volgen conventional commits
- [ ] Geen merge conflicts
- [ ] Docker build succesvol

## Code Style

### Python
- PEP 8 style guide
- Type hints waar mogelijk
- Docstrings voor functies

### TypeScript/React
- ESLint configuratie volgen
- Functional components met hooks
- Props interfaces definiëren

### SQL
- Lowercase keywords
- Descriptive table/column names
- Proper indexing

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker compose up -d
curl http://localhost:8081/healthz
```

## Documentatie

- Update README.md voor user-facing changes
- Update WINDSURF_SETUP.md voor setup changes
- Add inline comments voor complexe logic
- Update API docs in backend/app.py

## Vragen?

- Open een [Issue](https://github.com/jurgenhufken/LIFE_DB_TEST/issues)
- Check bestaande [Discussions](https://github.com/jurgenhufken/LIFE_DB_TEST/discussions)

## Code of Conduct

Wees respectvol en constructief. We willen een welkome community voor iedereen.

## License

Door bij te dragen ga je akkoord dat je bijdragen onder de MIT License vallen.

---

**Bedankt voor je bijdrage! 🚀**
