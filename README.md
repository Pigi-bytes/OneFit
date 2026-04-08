# OneFit

Application web de fitness avec un backend Flask (API REST) et un frontend Angular.

## Structure

- `backend/` API Flask, routes, schemas, modeles, config et base
- `frontend/` application Angular

## Backend

### 1. Prerequis

- Python 3.13+
- `uv`

#### Installation de `uv` :

| Système | Commande |
|--------|----------|
| **Windows** | `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` |
| **macOS / Linux** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Via pip** | `pip install uv` |

### 2. Installation

Depuis le répertoire `backend`, initialisez l''environnement :

```bash
cd backend
uv sync
```
 
`uv sync` installe automatiquement la version de Python requise ainsi que toutes les dépendances dans un environnement virtuel (`.venv`).
 
### 3. Configuration de l'environnement `.env`

Copiez le fichier `.env.example` (fourni dans le dépôt) en `.env` à la racine du dossier `backend` :

```bash
# macOS / Linux
cp .env.example .env
 
# Windows (PowerShell)
Copy-Item .env.example .env
```

Remplissez ensuite les valeurs manquantes dans `.env` :

> Ne commitez jamais le fichier `.env` il est (et doit rester) dans le `.gitignore`.


### 3. Lancement de l'API
 
Le comportement de l'application dépend du flag `FLASK_DEBUG` :
 
#### Mode développement SQLite local
 
```bash
uv run flask run --debug
```
 
#### Mode production PostgreSQL
 
```bash
uv run flask run
```
 
Depuis `backend/`.
 
---
 
### 4. Gestion de la base de données

Rajouter le flag debug si vous voulez toucher a la base de donnée Local

```bash
# Initialiser la base de données
uv run flask [--debug] init-db
 
# Réinitialiser (supprime et recrée toutes les tables)
uv run flask [--debug] reset-db
 
# Supprimer la table des logs de requêtes
uv run flask [--debug] drop-requestlog
```
### 6. Info 

> Le CORS est configuré pour accepter uniquement les requêtes provenant du frontend Angular sur `http://localhost:4200`.


## Frontend

### 1. Prerequis
- node.js
-- télechargable depuis le site de  [Node.js](https://nodejs.org/en/) (sélectionner la version de votre os)
-- vérifier l'installation : 
```bash
Node --version
npm --version
```

- Angular
```bash
npm install -g @angular/cli
```
### 2. Lancement du serveur

- déplacement dans le dossier frontend
```bash
cd frontend
```

- lancer le serveur
```bash
ng serve
```

Bravo vous avez lancé la meilleur application de suivit de sport.