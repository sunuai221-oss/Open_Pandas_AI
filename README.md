# 🧠 Open Pandas-AI - Agent IA d'analyse de données

Agent intelligent pour analyser des données avec l'IA. Chargez un CSV/Excel, posez vos questions en langage naturel, obtenez des réponses avec code généré automatiquement.

## ✨ Dernières mises à jour

**Phase 2 - Système hybride de dictionnaire** (NOUVEAU):
- Détection automatique du type de dataset (12+ domaines)
- Dictionnaires prédéfinis pour E-commerce, CRM, RH, Finance, etc.
- Enrichissement optionnel avec UI intuitive
- Intégration au LLM pour meilleur contexte métier
- Amélioration qualité réponses estimée: +15-25%

**Phase 1 - Qualité des réponses**:
- Détection 16 intentions analytiques
- Validation intelligente des résultats
- Suggestions d'amélioration
- Scoring de qualité

## 🚀 Fonctionnalités

## Démarrage

1. Installer les dépendances :

pip install -r requirements.txt

2. Exportez votre clé Codestral :

export MISTRAL_API_KEY="sk-..."


3. Lancez l’interface Streamlit :

streamlit run app.py


4. Uploadez un CSV, posez une question ("Quels sont les 5 pays avec le plus de ventes ?")

## Fonctionnalités

- Génération automatique de code Python/Pandas via Codestral
- Exécution locale, résultat affiché directement
- Compatible toutes questions sur vos CSV (NL2Pandas)
- Résultats intelligemment formatés (table, liste, texte...)

## Limitations MVP

- Sandbox Docker éphémère disponible (activable via USE_DOCKER_SANDBOX=true)
- **Pas de visualisation graphique automatique**
- **Pas de correction automatique des erreurs**
- **Pas de jointure multi-DataFrames**
- Utilisation recommandée en environnement de test !

---

Développé avec ❤️ pour les curieux de l’IA et de la data.
Crédits : [Mistral AI](https://mistral.ai/) + Pandas + Streamlit

## Sandbox et securite

- Le code Pandas genere est execute dans un sous-processus isole (`core.sandbox_runner`).
- L'analyse AST est renforcee pour bloquer imports, introspection dangereuse et acces systeme.
- Ajustez le delai maximal via la variable d'environnement `SANDBOX_TIMEOUT_SECONDS`.

## Tests automatiques

```bash
pytest
```

Les tests couvrent les utilitaires (`core/utils.py`) et un flux d'analyse complet avec un LLM mocke.

## Deploiement Docker Compose

1. Copiez `.env.example` vers `.env` et renseignez vos secrets (cle Mistral, URL Postgres).
2. Lancez l'ensemble :
   ```bash
   docker compose up --build
   ```
3. Streamlit est disponible sur http://localhost:8501.
4. La base `db` expose `postgresql+psycopg2://postgres:postgres@db:5432/openpanda` par defaut. Modifiez ces valeurs pour un environnement de production.

## Gestion des dependances

- `requirements.txt` fige les versions pour des builds reproductibles.
- Pour mettre a jour proprement : installez `pip-tools` puis `pip-compile requirements.in` (a introduire si besoin) afin de regenir `requirements.txt`.
- Pour des workflows plus avances ou mono-repo, Poetry reste une option viable, mais n'est pas necessaire pour ce MVP.


## Sécurité renforcée avec Docker

### Exécution sécurisée par conteneurs éphémères

Le projet utilise maintenant des **conteneurs Docker éphémères** pour l'exécution du code généré par l'IA :

- ✅ Isolation complète : chaque exécution dans un conteneur dédié
- ✅ Auto-destruction : conteneurs supprimés automatiquement après usage
- ✅ Limites de ressources : CPU/mémoire/réseau contrôlés
- ✅ Utilisateur non-privilégié : exécution sans droits administrateur

### Configuration

1. Construction de l'image sandbox :
```bash
chmod +x scripts/build-sandbox.sh
./scripts/build-sandbox.sh
```

2. Activation du mode Docker :
```bash
export USE_DOCKER_SANDBOX=true
docker compose up --build
```

3. Mode fallback : Si Docker n'est pas disponible, le système utilise automatiquement l'ancien mode subprocess.

### Architecture de sécurité

```
Question utilisateur
    ↓
Code généré par IA
    ↓
Validation AST (code_security.py)
    ↓
Conteneur Docker éphémère
    ├── Isolation réseau (network_mode=none)
    ├── Limites ressources (512MB RAM, 50% CPU)
    ├── Utilisateur non-privilégié
    └── Auto-destruction après exécution
    ↓
Résultat sécurisé
```

### Variables d'environnement

- `USE_DOCKER_SANDBOX=true` : Active l'exécution Docker
- `SANDBOX_TIMEOUT_SECONDS=30` : Timeout d'exécution
- `SANDBOX_IMAGE=openpanda-sandbox:latest` : Image à utiliser
