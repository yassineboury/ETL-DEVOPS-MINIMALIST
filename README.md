# ETL DevSecOps Minimalist

## Description
ETL simple pour extraire des indicateurs DevSecOps depuis GitLab et SonarQube, et les exporter en fichiers Excel pour analyse dans Power BI.

## Indicateurs collectés

### GitLab
- **Projets** : Liste des projets, statuts, dernière activité
- **Commits** : Nombre de commits par projet/période
- **Users** : Contributeurs actifs, rôles
- **Events** : Activités récentes (push, merge, etc.)
- **Merge Requests** : Statuts, temps de review
- **Pipelines** : Succès/échecs, durées

### SonarQube  
- **Couverture de code** : Pourcentages par projet
- **Bugs** : Nombre et sévérité
- **Vulnérabilités** : Critiques, majeures, mineures
- **Code smells** : Dette technique
- **Quality Gates** : Statuts de validation

## Architecture

```
etl-devsecops/
├── config/
│   ├── config.yaml          # Configuration URLs/tokens
│   └── projects.yaml        # Liste des 200 projets
├── gitlab/
│   ├── gitlab_projects.py   # Extraction projets GitLab
│   ├── gitlab_users.py      # Extraction utilisateurs
│   ├── gitlab_commits.py    # Extraction commits
│   ├── gitlab_events.py     # Extraction événements
│   ├── gitlab_merge_requests.py  # Extraction MR
│   └── gitlab_pipelines.py  # Extraction pipelines
├── sonar/
│   ├── sonar_projects.py    # Extraction projets Sonar
│   ├── sonar_coverage.py    # Extraction couverture
│   ├── sonar_bugs.py        # Extraction bugs
│   ├── sonar_vulnerabilities.py # Extraction vulnérabilités
│   ├── sonar_code_smells.py # Extraction code smells
│   └── sonar_quality_gates.py # Extraction quality gates
├── output/                  # Fichiers Excel générés
├── main.py                  # Point d'entrée principal
└── requirements.txt         # Dépendances Python
```

## Installation

1. **Cloner le projet**
```bash
git clone <repo-url>
cd etl-devsecops
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

### Extraction complète (hebdomadaire)
```bash
python main.py
```

### Extraction par outil
```bash
python main.py --gitlab-only
python main.py --sonar-only
```

## Outputs

Les fichiers Excel sont générés dans le dossier `output/` :
- `gitlab_indicators.xlsx` : Tous les indicateurs GitLab
- `sonar_indicators.xlsx` : Tous les indicateurs SonarQube

Chaque fichier contient plusieurs onglets par type d'indicateur.

## Import dans Power BI

1. Ouvrir Power BI Desktop
2. **Obtenir les données** > **Fichier** > **Excel**
3. Sélectionner les fichiers dans `output/`
4. Choisir les onglets à importer
5. Créer vos visualisations

## Planification

Exécution recommandée : **Hebdomadaire le dimanche soir**

Option 1 - Cron (macOS/Linux) :
```bash
0 22 * * 0 cd /path/to/etl-devsecops && python main.py
```

Option 2 - Automator (macOS) ou Tâches planifiées (Windows)

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
- Vérifier les permissions du dossier output/

### Logs
Les logs d'exécution sont affichés dans la console et peuvent être redirigés :
```bash
python main.py > logs/extraction_$(date +%Y%m%d).log 2>&1
```

## Support

- **Fréquence** : Extraction hebdomadaire
- **Volume** : 200 projets
- **Formats** : Excel (.xlsx)
- **Destination** : Power BI

---
*Dernière mise à jour : Août 2025*
