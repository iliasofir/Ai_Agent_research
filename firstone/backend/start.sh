#!/bin/bash

# Script de démarrage du backend FastAPI

echo "🚀 Démarrage du Backend Multi-Agent Research System..."

# Vérifier si on est dans le bon répertoire
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erreur: Veuillez exécuter ce script depuis le répertoire backend/"
    exit 1
fi

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Créer un environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Vérifier le fichier .env
if [ ! -f "../.env" ]; then
    echo "⚠️  Attention: Fichier .env non trouvé à la racine du projet"
    echo "Assurez-vous de configurer vos API keys dans ../.env"
fi

# Démarrer le serveur
echo "✅ Démarrage du serveur FastAPI sur http://localhost:8000"
echo "📚 Documentation API disponible sur http://localhost:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
