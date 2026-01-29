# OneFit Backend

Backend de l''application OneFit développé avec Flask et géré par [uv](https://docs.astral.sh/uv/).

## Installation

### 1. Installation de `uv`

Exécutez la commande correspondant à votre système d''exploitation :

- **Windows** :
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **macOS / Linux** :
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Avec pip** : 
  ```bash
  pip install uv
  ```

### 2. Configuration du projet

Depuis le répertoire `backend`, initialisez l''environnement :

```bash
uv sync
```

Cette commande installe automatiquement la version de Python requise et les dépendances dans un environnement virtuel (`.venv`).

## Utilisation

### Création et reset de la base de donnée

```
uv run init-db
```

```
uv run reset-db
```


### Lancement du serveur

```bash
uv run -- flask run --debug
```

Le serveur sera accessible sur `http://127.0.0.1:5000`.

### Gestion des dépendances

- **Ajouter un paquet** : `uv add <nom_du_paquet>`
- **Mettre à jour** : `uv sync`
- **Exécuter un script** : `uv run <script.py>`
## Tests

Pour lancer les tests unitaires :

```bash
uv run pytest
```