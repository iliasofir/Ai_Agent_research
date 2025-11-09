# 🤖 AI Research Assistant - Multi-Agent System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.0%2B-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

Un système intelligent de recherche et d'analyse basé sur des agents IA multi-agents. Ce projet combine CrewAI, FastAPI et React pour créer une plateforme de recherche automatisée avec validation de qualité en temps réel.

## 📋 Table des matières

- [Aperçu](#-aperçu)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [API Documentation](#-api-documentation)
- [WebSocket](#-websocket)
- [Développement](#-développement)
- [Dépannage](#-dépannage)
- [Contributions](#-contributions)
- [Licence](#-licence)

## 🎯 Aperçu

AI Research Assistant est un système de recherche automatisé qui utilise trois agents IA spécialisés :

1. **🔍 Researcher** - Collecte et analyse des articles scientifiques depuis ArXiv et le web
2. **✅ Reviewer** - Valide la qualité et la pertinence de la recherche
3. **📊 Synthesizer** - Génère un rapport de synthèse complet

Le système fonctionne de manière itérative avec un maximum de 3 tentatives pour garantir la qualité des résultats.

## ✨ Fonctionnalités

### Backend

- ✅ Workflow multi-agents avec CrewAI
- ✅ Communication WebSocket en temps réel
- ✅ Upload et analyse de PDFs
- ✅ Recherche sur ArXiv et sources web
- ✅ Validation de qualité automatique
- ✅ Génération de rapports Markdown
- ✅ Gestion des erreurs et retry automatique
- ✅ API RESTful avec FastAPI

### Frontend

- ✅ Interface utilisateur moderne et réactive
- ✅ Visualisation du workflow en temps réel
- ✅ Animation des agents et de leurs états
- ✅ Affichage des rapports avec rendu Markdown
- ✅ Upload de fichiers PDF
- ✅ Notifications toast pour les événements
- ✅ Design responsive avec Tailwind CSS

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Input Form   │  │  Workflow    │  │  Report Display      │  │
│  │              │  │  Animation   │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   WebSocket       │
                    │   HTTP REST       │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              WebSocket Manager                           │   │
│  │         (Broadcasting en temps réel)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Research Flow (CrewAI)                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────────┐   │   │
│  │  │ Researcher │→ │  Reviewer  │→ │  Synthesizer    │   │   │
│  │  └────────────┘  └────────────┘  └─────────────────┘   │   │
│  │         ↓              ↓                  ↓              │   │
│  │    [ArXiv/Web]    [Validation]      [Report Gen]        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Prérequis

### Backend

- Python 3.10 à 3.13
- UV (gestionnaire de paquets Python)
- Clé API OpenAI

### Frontend

- Node.js 18+
- npm ou bun

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <repository-url>
cd Ai
```

### 2. Installation du Backend

```bash
cd firstone

# Installer UV si nécessaire
pip install uv

# Créer l'environnement virtuel et installer les dépendances
uv venv
source .venv/bin/activate  # Sur macOS/Linux
# ou
.venv\Scripts\activate  # Sur Windows

# Installer les dépendances
uv pip install -r requirements.txt
```

### 3. Installation du Frontend

```bash
cd ../front/ai-flow-visualizer-53

# Installer les dépendances
npm install
# ou
bun install
```

## ⚙️ Configuration

### Backend Configuration

Créez un fichier `.env` dans le dossier `firstone/` :

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_NAME=gpt-4o-mini

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Configuration

Créez un fichier `.env` dans le dossier `front/ai-flow-visualizer-53/` :

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000/api/v1
```

### Configuration des Agents

Modifiez `firstone/src/firstone/config/agents.yaml` pour personnaliser les agents :

```yaml
researcher:
  role: "Senior Research Analyst"
  goal: "Find and analyze the most relevant academic papers"
  backstory: "Expert researcher with deep knowledge of scientific literature"

reviewer:
  role: "Quality Assurance Specialist"
  goal: "Ensure research meets high quality standards"
  backstory: "Meticulous reviewer with years of academic experience"

synthesizer:
  role: "Content Synthesizer"
  goal: "Create comprehensive synthesis reports"
  backstory: "Expert at distilling complex information into clear insights"
```

## 🎮 Utilisation

### Démarrer le Backend

```bash
cd firstone/backend

# Option 1: Avec uvicorn directement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Avec le script de démarrage
chmod +x start.sh
./start.sh
```

Le backend sera accessible sur `http://localhost:8000`

### Démarrer le Frontend

```bash
cd front/ai-flow-visualizer-53

# Avec npm
npm run dev

# Avec bun
bun run dev
```

Le frontend sera accessible sur `http://localhost:5173`

### Utiliser l'application

1. **Ouvrez votre navigateur** à `http://localhost:5173`
2. **Entrez un sujet de recherche** (ex: "Machine Learning in Healthcare")
3. **Optionnel**: Uploadez des PDFs pour analyse
4. **Lancez la recherche** et observez le workflow en temps réel
5. **Consultez le rapport** généré automatiquement

## 📁 Structure du projet

```
Ai/
├── firstone/                     # Backend
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   │       ├── research.py      # Routes de recherche
│   │   │   │       ├── websocket.py     # WebSocket endpoint
│   │   │   │       ├── upload.py        # Upload de PDFs
│   │   │   │       └── health.py        # Health check
│   │   │   ├── models/
│   │   │   │   └── schemas.py          # Modèles Pydantic
│   │   │   ├── services/
│   │   │   │   ├── orchestrator.py     # Orchestration des agents
│   │   │   │   └── knowledge_service.py
│   │   │   ├── websocket_manager.py    # Gestion WebSocket
│   │   │   ├── config.py               # Configuration
│   │   │   └── main.py                 # Point d'entrée FastAPI
│   │   ├── output/                     # Rapports générés
│   │   └── uploads/                    # PDFs uploadés
│   ├── src/
│   │   └── firstone/
│   │       ├── config/
│   │       │   ├── agents.yaml         # Configuration agents
│   │       │   └── tasks.yaml          # Configuration tâches
│   │       ├── tools/
│   │       │   ├── pdf_reader_tool.py  # Outil lecture PDF
│   │       │   └── custom_tool.py
│   │       ├── crew.py                 # Définition CrewAI
│   │       └── main.py
│   └── requirements.txt
│
└── front/                        # Frontend
    └── ai-flow-visualizer-53/
        ├── src/
        │   ├── components/
        │   │   ├── WorkflowAnimation.tsx   # Animation du workflow
        │   │   ├── InputForm.tsx           # Formulaire d'entrée
        │   │   ├── ReportDisplay.tsx       # Affichage rapport
        │   │   ├── AgentNode.tsx           # Nœud agent
        │   │   └── ui/                     # Composants UI
        │   ├── hooks/
        │   │   └── useResearchWebSocket.ts # Hook WebSocket
        │   ├── services/
        │   │   ├── websocketService.ts     # Service WebSocket
        │   │   └── researchService.ts      # Service API
        │   ├── pages/
        │   │   └── Index.tsx               # Page principale
        │   └── lib/
        │       └── utils.ts                # Utilitaires
        ├── package.json
        └── vite.config.ts
```

## 📚 API Documentation

### Endpoints REST

#### POST /api/v1/research/send

Démarre une nouvelle recherche.

```json
{
  "topic": "Machine Learning in Healthcare"
}
```

**Response:**

```json
{
  "research_id": "uuid-here",
  "topic": "Machine Learning in Healthcare",
  "status": "processing",
  "message": "Research started"
}
```

#### POST /api/v1/research/upload-pdf

Upload un PDF pour analyse.

```bash
curl -X POST "http://localhost:8000/api/v1/research/upload-pdf" \
  -F "file=@document.pdf" \
  -F "topic=Machine Learning"
```

#### GET /api/v1/health

Health check de l'API.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T12:00:00Z"
}
```

## 🔌 WebSocket

### Connexion

```javascript
const ws = new WebSocket("ws://localhost:8000/api/ws/progress");
```

### Messages reçus

```typescript
interface WebSocketMessage {
  agent: "Researcher" | "Reviewer" | "Synthesizer" | "System";
  status:
    | "started"
    | "thinking"
    | "working"
    | "done"
    | "error"
    | "retry"
    | "approved"
    | "rejected"
    | "completed";
  message: string;
  timestamp: string;
  details?: {
    final_report?: string;
    report_content?: string;
    [key: string]: any;
  };
  iteration?: number;
}
```

### Exemple de séquence

```
1. {agent: "Researcher", status: "started", message: "Starting research..."}
2. {agent: "Researcher", status: "working", message: "Gathering papers..."}
3. {agent: "Researcher", status: "done", message: "Research completed"}
4. {agent: "Reviewer", status: "thinking", message: "Reviewing quality..."}
5. {agent: "Reviewer", status: "done", message: "Research approved"}
6. {agent: "Synthesizer", status: "working", message: "Generating report..."}
7. {agent: "Synthesizer", status: "done", details: {report_content: "..."}}
8. {agent: "System", status: "completed", details: {final_report: "..."}}
```

## 🛠 Développement

### Backend

```bash
# Lancer en mode développement avec auto-reload
cd firstone/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Lancer les tests (si disponibles)
pytest

# Vérifier le code
ruff check .
black .
```

### Frontend

```bash
cd front/ai-flow-visualizer-53

# Développement
npm run dev

# Build
npm run build

# Preview de la build
npm run preview

# Lint
npm run lint
```

### Variables d'environnement de développement

**Backend:**

- `DEBUG=True` - Active le mode debug
- `LOG_LEVEL=DEBUG` - Niveau de log détaillé

**Frontend:**

- `VITE_API_BASE_URL` - URL de l'API backend
- `VITE_WS_BASE_URL` - URL WebSocket

## 🐛 Dépannage

### Backend ne démarre pas

**Problème:** `ModuleNotFoundError: No module named 'firstone.pdf_reader_tool'`

**Solution:** Vérifier que l'import dans `src/firstone/__init__.py` est correct:

```python
from .tools.pdf_reader_tool import read_pdf, PDFReaderTool
```

### WebSocket se déconnecte

**Problème:** Le WebSocket se ferme avant la fin du processing

**Solution:** Le système de keepalive est maintenant implémenté. Assurez-vous que:

- Le backend envoie des pings toutes les 30s
- Le frontend répond aux pings
- Les deux serveurs sont bien démarrés

### Le rapport ne s'affiche pas

**Vérifications:**

1. Vérifier les logs du backend pour `details.final_report` ou `details.report_content`
2. Vérifier la console du navigateur pour les messages WebSocket
3. Vérifier que le fichier `output/synthesis_report.md` est créé

### Erreur CORS

**Solution:** Vérifier le fichier `.env` du backend:

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🤝 Contributions

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [CrewAI](https://crewai.com) - Framework multi-agents
- [FastAPI](https://fastapi.tiangolo.com/) - Framework API moderne
- [React](https://reactjs.org/) - Bibliothèque UI
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS
- [shadcn/ui](https://ui.shadcn.com/) - Composants UI

## 📞 Support

Pour toute question ou problème :

- 📧 Email: support@example.com
- 💬 Discord: [Rejoindre le serveur](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/yourrepo/issues)

---

Développé avec ❤️ par votre équipe
