# ETL DevSecOps Minimalist

## Description
ETL simple pour extraire des indicateurs DevSecOps depuis GitLab et SonarQube, et les exporter en fichiers Excel pour analyse dans Power BI.

## 🚀 **État actuel du projet**

### ✅ **Fonctionnalités implémentées**
- **GitLab** : Extraction projets et utilisateurs
- **Interface** : MAESTRO KENOBI avec barres de progression
- **Export** : Fichiers Excel horodatés
- **Architecture** : Modulaire et extensible

### 🚧 **En développement**
- GitLab : Commits, Events, MR, Pipelines
- SonarQube : Tous les modules

### 📋 **Roadmap**
1. Compléter les extracteurs GitLab
2. Implémenter les modules SonarQube  
3. Ajouter Dependency Track
4. Interface web (optionnel)

## Indicateurs collectés

### GitLab ✅ **Implémenté**
- **Projets** : Liste des projets, statuts, dernière activité
- **Users** : Contributeurs actifs, rôles, permissions

### 🚧 **En cours de développement**
- **Commits** : Nombre de commits par projet/période
- **Events** : Activités récentes (push, merge, etc.)
- **Merge Requests** : Statuts, temps de review
- **Pipelines** : Succès/échecs, durées

### SonarQube 🔮 **À venir**
- **Couverture de code** : Pourcentages par projet
- **Bugs** : Nombre et sévérité
- **Vulnérabilités** : Critiques, majeures, mineures
- **Code smells** : Dette technique
- **Quality Gates** : Statuts de validation

## Architecture

```
etl-devsecops/
├── 📄 maestro_kenobi.py           # 🎯 MAESTRO KENOBI - Orchestrateur principal avec UI
├── 📄 STATUS_GITLAB.md           # Documentation connexion
├── 📁 config/
│   ├── config.yaml                # Configuration URLs/tokens
│   ├── config.example.yaml        # Template de configuration  
│   └── projects.yaml              # Liste des 200 projets
├── 📁 gitlab_tools/               # 🔧 Modules GitLab (architecture modulaire)
│   ├── client/
│   │   └── gitlab_client.py       # Client GitLab centralisé
│   ├── extractors/
│   │   ├── projects_extractor.py  # Extraction projets GitLab
│   │   └── users_extractor.py     # Extraction utilisateurs GitLab
│   └── exporters/
│       └── excel_exporter.py      # Export vers Excel
├── 📁 scripts/                    # Scripts d'export spécifiques
│   ├── export_gitlab_projects.py  # Script projets
│   └── export_gitlab_users.py     # Script utilisateurs
├── 📁 exports/gitlab/             # 📊 Fichiers Excel générés
├── 📄 requirements.txt            # Dépendances Python
└── 📄 pyproject.toml              # Configuration Ruff
```

### 🚧 **Modules en développement (SonarQube)**
```
├── 📁 sonar_tools/ (à venir)
│   ├── extractors/
│   │   ├── coverage_extractor.py
│   │   ├── bugs_extractor.py
│   │   ├── vulnerabilities_extractor.py
│   │   └── quality_gates_extractor.py
│   └── exporters/
└── 📁 exports/sonar/ (à venir)
```

## Installation

1. **Cloner le projet**
```bash
git clone https://github.com/yassineboury/ETL-DEVOPS-MINIMALIST.git
cd ETL-DEVOPS-MINIMALIST
```

2. **Créer environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les accès**
   - Copier `config/config.example.yaml` vers `config/config.yaml`
   - Renseigner les URLs et tokens GitLab/SonarQube
   - Modifier `config/projects.yaml` avec vos 200 projets

## Configuration

### config/config.yaml
```yaml
gitlab:
  url: "https://gitlab.votre-entreprise.com"
  token: "your-gitlab-token"
  
sonar:
  url: "https://sonar.votre-entreprise.com"
  token: "your-sonar-token"
```

### Variables d'environnement (.env)
```bash
GITLAB_TOKEN=your-gitlab-token
SONAR_TOKEN=your-sonar-token
```

## Utilisation

### 🎯 **Méthode recommandée : MAESTRO KENOBI**
```bash
python maestro_kenobi.py
```
*🎭 L'orchestrateur ultime avec interface interactive, barres de progression et nettoyage automatique*

### 📋 **Méthodes alternatives**

**Extraction par scripts individuels :**
```bash
python scripts/export_gitlab_projects.py
python scripts/export_gitlab_users.py
```

**Extraction via MAESTRO KENOBI (recommandé) :**
```bash
python maestro_kenobi.py
```

## Outputs

Les fichiers Excel sont générés dans le dossier `exports/gitlab/` :
- `gitlab_projects.xlsx` : Données des projets GitLab
- `gitlab_users.xlsx` : Données des utilisateurs GitLab
- `gitlab_rapport_complet.xlsx` : Rapport consolidé complet

**Format des fichiers :**
- Noms simples sans horodatage pour faciliter l'intégration
- Multiples onglets par type d'indicateur
- Compatible Power BI Desktop

### 🔄 **Nettoyage automatique**
MAESTRO KENOBI supprime automatiquement les anciens fichiers avant chaque export.

## Import dans Power BI

1. Ouvrir Power BI Desktop
2. **Obtenir les données** > **Fichier** > **Excel**
3. Sélectionner les fichiers `gitlab_*.xlsx` dans `exports/gitlab/`
4. Choisir les onglets à importer
5. Créer vos visualisations

### 💡 **Conseil**
Utilisez les fichiers les plus récents (horodatage dans le nom) pour vos analyses.

## Planification

Exécution recommandée : **Hebdomadaire le dimanche soir**

### Option 1 - Cron (macOS/Linux) avec MAESTRO KENOBI :
```bash
0 22 * * 0 cd /path/to/etl-devsecops && python maestro_kenobi.py
```

### Option 2 - Scripts individuels :
```bash
# Projets seulement
0 22 * * 0 cd /path/to/etl-devsecops && python scripts/export_gitlab_projects.py

# Utilisateurs seulement  
5 22 * * 0 cd /path/to/etl-devsecops && python scripts/export_gitlab_users.py
```

### Option 3 - Automator (macOS) ou Tâches planifiées (Windows)
Créer une tâche qui exécute `python maestro_kenobi.py`

## Dépannage

### Erreurs fréquentes

**Erreur d'authentification :**
- Vérifier la validité des tokens
- Contrôler les permissions d'accès

**Timeout API :**
- Réduire le nombre de projets par lot
- Augmenter les délais entre appels

**Fichier Excel verrouillé :**
- Fermer Power BI avant l'extraction
- Vérifier les permissions du dossier `exports/gitlab/`
- Utiliser le nettoyage automatique de MAESTRO KENOBI

**Erreurs de modules :**
- Vérifier que tous les packages sont installés : `pip install -r requirements.txt`
- Activer l'environnement virtuel

### Logs
Les logs d'exécution sont affichés dans la console avec des barres de progression.
Pour sauvegarder les logs :
```bash
python maestro_kenobi.py > logs/extraction_$(date +%Y%m%d).log 2>&1
```

## Support

- **État actuel** : GitLab partiellement implémenté (projets + utilisateurs)
- **Fréquence recommandée** : Extraction hebdomadaire
- **Volume testé** : 327 projets (instance ONCF)
- **Formats de sortie** : Excel (.xlsx) avec horodatage
- **Destination** : Power BI Desktop
- **Interface** : Console avec barres de progression (tqdm)

---
*Dernière mise à jour : Août 2025*
