# 📊 Scripts d'Extraction

Ce dossier contient tous les scripts d'extraction de données pour différentes plateformes DevOps.

## 📁 Structure

```
extractions/
├── gitlab/                 # Extractions GitLab
│   ├── extract_users.py    # Extraction utilisateurs GitLab
│   ├── extract_projects.py # Extraction projets GitLab  
│   ├── extract_groups.py   # Extraction groupes GitLab
│   └── README.md           # Documentation GitLab
└── README.md               # Ce fichier
```

## 🎯 Plateformes Supportées

### GitLab 🦊
- **Dossier** : `gitlab/`
- **Instance** : GitLab ONCF (https://gitlab.oncf.net/)
- **Scripts disponibles** :
  - 👥 Utilisateurs
  - 📁 Projets
  - 👥 Groupes

## 🚀 Utilisation

1. **Aller dans le dossier de la plateforme** :
   ```bash
   cd scripts/extractions/gitlab
   ```

2. **Exécuter un script d'extraction** :
   ```bash
   python extract_users.py      # Extraction utilisateurs
   python extract_projects.py   # Extraction projets
   python extract_groups.py     # Extraction groupes
   ```

3. **Fichiers générés** :
   - **Emplacement** : `exports/gitlab/`
   - **Format** : Excel (.xlsx)

## 📋 Prérequis

- Configuration `.env` avec les tokens d'accès
- Configuration `config/config.yaml`
- Dépendances Python installées (`pip install -r requirements.txt`)

## 🔧 Extension

Pour ajouter une nouvelle plateforme (ex: GitHub, Jenkins, etc.) :

1. Créer un dossier `nouvelle_plateforme/`
2. Ajouter les scripts d'extraction
3. Créer un README spécifique
4. Mettre à jour ce README principal
