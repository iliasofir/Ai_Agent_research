# Documentation de l'API de Recherche

## Endpoint de Recherche

### POST `/api/v1/research/send`

Cet endpoint permet d'envoyer une requête de recherche et de recevoir un résultat d'analyse.

#### URL

```
http://localhost:8000/api/v1/research/send
```

#### Méthode

`POST`

#### Headers

```
Content-Type: application/json
```

#### Corps de la Requête

```json
{
  "topic": "Votre sujet de recherche"
}
```

##### Paramètres

| Paramètre | Type   | Requis | Description              |
| --------- | ------ | ------ | ------------------------ |
| topic     | string | Oui    | Le sujet de la recherche |

#### Réponse

##### Structure de la Réponse

```typescript
interface ResearchResponse {
  status: "success" | "failed" | "processing";
  topic: string;
  result: string;
  message: string;
}
```

##### Exemple de Réponse en Cas de Succès

```json
{
  "status": "success",
  "topic": "Intelligence Artificielle",
  "result": "# Rapport de Recherche\n\n## Introduction\n...",
  "message": "Recherche 'Intelligence Artificielle' réussie"
}
```

##### Exemple de Réponse en Cas d'Échec

```json
{
  "status": "failed",
  "topic": "Intelligence Artificielle",
  "result": "Research failed after 3 attempts.\n\nLast feedback:\nInsufficient data found",
  "message": "Recherche 'Intelligence Artificielle' échouée après 3 tentatives"
}
```

#### Codes de Statut HTTP

| Code | Description                             |
| ---- | --------------------------------------- |
| 200  | Requête réussie                         |
| 400  | Requête invalide (paramètres manquants) |
| 500  | Erreur interne du serveur               |

## Utilisation dans l'Application

### Service de Recherche

Le service `researchService.ts` encapsule la logique d'appel à l'API :

```typescript
import { sendResearchRequest } from "@/services/researchService";

// Envoyer une requête de recherche
try {
  const response = await sendResearchRequest("Mon sujet de recherche");
  console.log(response.result); // Le résultat de la recherche
} catch (error) {
  console.error("Erreur lors de la recherche:", error);
}
```

### Intégration dans l'Interface

L'interface utilisateur utilise ce service pour :

1. **Saisie du Sujet** : L'utilisateur entre son sujet dans le champ de texte
2. **Envoi de la Requête** : Au clic sur "Start Research", l'API est appelée
3. **Affichage du Workflow** : Une animation montre la progression du traitement
4. **Affichage du Résultat** : Le résultat est affiché dans un rapport formaté

## Configuration

### URL de l'API

L'URL de base de l'API est configurée dans `src/services/researchService.ts` :

```typescript
const API_BASE_URL = "http://localhost:8000/api/v1";
```

Pour modifier l'URL, éditez cette constante.

### Variables d'Environnement (Optionnel)

Vous pouvez créer un fichier `.env` pour configurer l'URL de l'API :

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Puis dans le service :

```typescript
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
```

## Gestion des Erreurs

L'application gère plusieurs types d'erreurs :

1. **Erreur de Connexion** : Affiche un toast indiquant que le serveur n'est pas accessible
2. **Erreur de Recherche** : Affiche le message d'erreur retourné par l'API
3. **Erreur de Format** : Gère les réponses mal formatées

## Tests

### Tester l'API avec cURL

```bash
curl -X POST http://localhost:8000/api/v1/research/send \
  -H "Content-Type: application/json" \
  -d '{"topic": "Intelligence Artificielle"}'
```

### Tester l'API avec Postman

1. Créez une nouvelle requête POST
2. URL : `http://localhost:8000/api/v1/research/send`
3. Headers : `Content-Type: application/json`
4. Body (raw JSON) :
   ```json
   {
     "topic": "Votre sujet"
   }
   ```
5. Envoyez la requête

## Dépannage

### Le serveur n'est pas accessible

**Erreur** : "Impossible de se connecter à l'API"

**Solutions** :

- Vérifiez que le serveur backend est démarré sur le port 8000
- Vérifiez que l'URL de l'API est correcte
- Vérifiez les paramètres CORS du serveur

### Erreur CORS

Si vous rencontrez des erreurs CORS, assurez-vous que votre serveur backend autorise les requêtes depuis `http://localhost:5173` (ou le port de votre application frontend).

Configuration backend recommandée (exemple Python FastAPI) :

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
