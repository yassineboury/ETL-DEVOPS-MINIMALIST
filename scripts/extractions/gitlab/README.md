# 🎯 Scripts d'Extraction GitLab Individuels

Ce dossier contient des scripts spécialisés pour effectuer des extractions individuelles des données GitLab ONCF.

## 📁 Structure

```
scripts/extractions/
├── extract_users.py      # 👥 Extraction des utilisateurs uniquement
├── extract_projects.py   # 📁 Extraction des projets uniquement  
├── extract_groups.py     # 👥 Extraction des groupes uniquement
└── README.md            # 📖 Documentation
```

## 🚀 Utilisation

### Prérequis
- Environnement Python configuré avec les dépendances
- Fichier `.env` avec les credentials GitLab
- Configuration dans `config/config.yaml`

### Extraction des Utilisateurs
```bash
# Depuis le répertoire racine du projet
python scripts/extractions/extract_users.py
```
**Résultat** : `exports/gitlab/gitlab_users.xlsx`

### Extraction des Projets
```bash
# Depuis le répertoire racine du projet
python scripts/extractions/extract_projects.py
```
**Résultat** : `exports/gitlab/gitlab_projects.xlsx`

### Extraction des Groupes
```bash
# Depuis le répertoire racine du projet
python scripts/extractions/extract_groups.py
```
**Résultat** : `exports/gitlab/gitlab_groups.xlsx`

## 📊 Avantages des Extractions Individuelles

- ⚡ **Rapidité** : Extraction ciblée sans données inutiles
- 🎯 **Flexibilité** : Choisir exactement ce dont vous avez besoin
- 💾 **Ressources** : Moins de mémoire et de temps de traitement
- 🔧 **Maintenance** : Plus facile à débugger et maintenir
- 📋 **Spécialisation** : Chaque script peut avoir ses propres optimisations

## 🆚 Alternative Complète

Pour une extraction complète avec toutes les données, utilisez l'orchestrateur principal :
```bash
python maestro_kenobi.py
```

## 📝 Notes

- Tous les scripts utilisent la même configuration GitLab
- Les fichiers Excel sont générés dans `exports/gitlab/`
- La connexion GitLab est fermée proprement après chaque extraction
- Gestion d'erreur intégrée avec messages explicites

---
*Créé pour le projet KENOBI DEVOPS - Extraction GitLab ONCF*
