# 🤖 Code Review Agent

Pipeline d'analyse de code automatisé basé sur **4 agents IA** qui collaborent pour détecter les bugs, évaluer la qualité, corriger le code et générer des tests — le tout via une interface web simple.

---

##  Fonctionnalités

-  **Bug Detector** — analyse statique, détecte bugs, erreurs logiques et failles de sécurité
-  **Code Reviewer** — évalue la qualité, le style et les bonnes pratiques (SOLID, lisibilité...)
-  **Code Corrector** — réécrit le code en corrigeant tous les problèmes détectés
-  **Test Engineer** — génère une suite de tests `pytest` complète
-  Pipeline **asynchrone** avec suivi en temps réel (polling)
-  Cache intelligent (Redis ou JSON local) pour éviter de retraiter un code déjà soumis
-  Authentification par clé API

---

##  Architecture

```
review_code_agent/
│
├── backend/                  # API Python (FastAPI + CrewAI)
│   ├── main.py                # Endpoints HTTP, auth, jobs async
│   ├── crew.py                 # Pipeline des 4 agents IA (CrewAI + Groq)
│   ├── cache.py                # Cache Redis / JSON local
│   ├── requirements.txt
│   ├── Dockerfile
│   └── gunicorn.conf.py
│
├── frontend/                 # Interface web (React + TypeScript + Vite)
│   └── src/
│       ├── App.tsx             # Logique principale + polling
│       ├── components/
│       │   ├── Header.tsx
│       │   ├── CodePanel.tsx   # Saisie du code à analyser
│       │   └── ResultPanel.tsx # Affichage des résultats par onglet
│       └── types/
│
└── docker-compose.yml        # Orchestration API + Redis
```

---

##  Fonctionnement du pipeline

```
Code soumis
    ↓
 Bug Detector     → liste des bugs détectés
    ↓
 Code Reviewer    → suggestions qualité & style
    ↓
 Code Corrector   → code corrigé + explications
    ↓
 Test Engineer    → suite de tests pytest
```

Chaque agent reçoit le contexte des agents précédents (`context=[...]` dans CrewAI) pour produire un résultat cohérent.

---

##  Démarrage rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- Une clé API [Groq](https://console.groq.com/) (gratuite)
- Redis *(optionnel — fallback JSON local automatique)*

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

pip install -r requirements.txt
```

Crée un fichier `.env` dans `backend/` :
```env
GROQ_API_KEY=ta_clé_groq
API_KEY=ta_clé_secrète_api
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=86400
CACHE_MAX_ENTRIES=500
CORS_ORIGINS=http://localhost:5173
```

Lance le serveur :
```bash
python main.py
```
 API disponible sur `http://localhost:8000`
 Documentation Swagger sur `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
```

Crée un fichier `.env` dans `frontend/` :
```env
VITE_API_URL=http://localhost:8000
```

Lance l'interface :
```bash
npm run dev
```
 Interface disponible sur `http://localhost:5173`

### 3. Avec Docker (recommandé pour la production)

```bash
docker-compose up --build
```
Démarre automatiquement l'API et Redis.

---

## 📡 Endpoints API

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Informations sur le service |
| `GET` | `/health` | Healthcheck |
| `POST` | `/review` | Lance une review **synchrone** (attend le résultat) |
| `POST` | `/review/async` | Lance une review **asynchrone**, retourne un `job_id` |
| `GET` | `/review/status/{job_id}` | Vérifie l'état d'un job asynchrone |

Toutes les routes `/review*` nécessitent le header :
```
X-API-Key: ta_clé_secrète_api
```

### Exemple de requête

```bash
curl -X POST http://localhost:8000/review/async \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ta_clé_secrète_api" \
  -d '{"code": "def add(a,b): return a+b", "language": "python"}'
```

---

##  Stack technique

| Couche | Technologies |
|---|---|
| **Orchestration IA** | CrewAI, LiteLLM |
| **LLM** | Groq (LLaMA 3.3 70B Versatile) |
| **Backend** | FastAPI, Pydantic, Uvicorn, Gunicorn |
| **Cache** | Redis (prod) / JSON local (dev, fallback automatique) |
| **Frontend** | React, TypeScript, Vite |
| **Rendu Markdown** | react-markdown, react-syntax-highlighter |
| **Conteneurisation** | Docker, Docker Compose |

---

## Sécurité

- Authentification par clé API (`X-API-Key`) sur tous les endpoints sensibles
- CORS configuré par variable d'environnement
- Vérification des variables d'environnement critiques au démarrage (`lifespan`)
- Conteneur Docker exécuté avec un utilisateur non-root

---

##  Pistes d'amélioration

- [ ] Stocker les jobs asynchrones dans Redis plutôt qu'en mémoire (perdu au redémarrage)
- [ ] Ajouter un système de rate limiting (`slowapi`)
- [ ] Cleanup du polling frontend via `useEffect` (éviter les fuites mémoire)
- [ ] Tests automatisés (pytest backend, Vitest frontend)
- [ ] Accessibilité clavier sur les onglets de résultats

---

## Licence

Projet personnel — usage libre.