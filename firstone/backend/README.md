# Backend FastAPI - Multi-Agent Research System

Backend API pour le système de recherche multi-agents utilisant CrewAI.

## 🚀 Installation

### Prérequis

- Python 3.10+
- pip

### Installation rapide

```bash
cd backend

# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
.\venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

Assurez-vous que le fichier `.env` à la racine du projet contient vos clés API :

```env
# API Keys
SERPER_API_KEY=votre_cle_serper
GOOGLE_API_KEY=votre_cle_google
GEMINI_API_KEY=votre_cle_gemini
```

## 🏃 Démarrage

### Méthode 1: Script de démarrage (Recommandé)

```bash
chmod +x start.sh
./start.sh
```

### Méthode 2: Commande directe

```bash
# Depuis le répertoire backend/
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Méthode 3: Python directement

```bash
python -m app.main
```

Le serveur démarre sur `http://localhost:8000`

## 📚 Documentation API

Une fois le serveur démarré, accédez à :

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Endpoints Principaux

### Health Check

- `GET /health` - Vérifie l'état de santé de l'API

### Recherche

- `POST /api/v1/research` - Démarre une nouvelle recherche
- `GET /api/v1/research/{research_id}` - Récupère le statut d'une recherche
- `GET /api/v1/research` - Liste toutes les recherches

### Upload

- `POST /api/v1/upload` - Upload un document (PDF, TXT, MD, DOCX)
- `GET /api/v1/upload/files` - Liste les fichiers uploadés
- `DELETE /api/v1/upload/files/{filename}` - Supprime un fichier

### WebSocket

- `WS /api/v1/ws/research/{research_id}` - Suivi en temps réel d'une recherche
- `WS /api/v1/ws/live` - Notifications en temps réel

## 📂 Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration
│   ├── api/
│   │   └── routes/
│   │       ├── health.py    # Health check
│   │       ├── research.py  # Routes de recherche
│   │       ├── upload.py    # Routes d'upload
│   │       └── websocket.py # Routes WebSocket
│   ├── models/
│   │   └── schemas.py       # Modèles Pydantic
│   └── services/
│       ├── orchestrator.py  # Orchestration CrewAI
│       └── knowledge_service.py  # Gestion des documents
├── requirements.txt
├── start.sh
└── README.md
```

## 🧪 Tests

### Test rapide avec curl

```bash
# Health check
curl http://localhost:8000/health

# Créer une recherche
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI LLMs trends 2025", "year": 2025}'
```

### Test WebSocket

Utilisez un client WebSocket ou la console du navigateur :

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/ws/live");
ws.onmessage = (event) => console.log(JSON.parse(event.data));
```

## 🐛 Debug

Pour activer le mode debug, modifiez `backend/app/config.py` :

```python
debug: bool = True
```

## 📝 Notes

- Les fichiers uploadés sont stockés dans `knowledge/uploaded_pdfs/`
- Les rapports générés sont dans `output/`
- Les recherches s'exécutent en arrière-plan (background tasks)
- WebSocket maintient la connexion avec des heartbeats toutes les 30s
