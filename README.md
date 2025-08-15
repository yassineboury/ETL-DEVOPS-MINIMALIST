# ETL DevSecOps Minimalist

## Description
ETL simple pour extraire des indicateurs DevSecOps depuis GitLab et les exporter en fichiers Excel pour analyse dans Power BI.

## 🏗️ **ARCHITECTURE DU PROJET**

### 📂 **Structure des dossiers**
```
KENOBI_DEVOPS/
├── kenobi_tools/                  # 🛠️ Outils DevOps Kenobi (GitLab uniquement)
│   └── gitlab/                    # 🦊 GitLab
│       ├── client/
│       │   └── gitlab_client.py
│       ├── extractors/
│       │   ├── gitlab_extract_users.py
│       │   ├── gitlab_extract_projects.py
│       │   ├── gitlab_extract_groups.py
│       │   ├── gitlab_extract_commits.py
│       │   ├── gitlab_extract_events.py
│       │   ├── gitlab_extract_merge_requests.py
│       │   └── gitlab_extract_pipelines.py
│       ├── exporters/
│       │   └── gitlab_export_excel.py
│       └── scripts/
│           ├── gitlab_script_users.py
│           ├── gitlab_script_projects.py
│           └── gitlab_script_groups.py
├── shared/                        # 🔧 Code commun Kenobi
│   ├── config/
│   │   └── shared_config.py
│   ├── utils/
│   │   └── shared_utils.py
│   └── exporters/
│       └── shared_export_base.py
├── config/                        # ⚙️ Configuration globale
├── exports/                       # 📁 Fichiers de sortie
└── maestro_kenobi.py             # 🎼 Orchestrateur principal
```

### 📝 **CONVENTIONS DE NOMMAGE**

#### **Format** : `{outil}_{responsabilité}_{fonction}.py`

| **Responsabilité** | **Format** | **Exemple** |
|-------------------|------------|-------------|
| **Client** | `{outil}_client.py` | `gitlab_client.py` |
| **Extracteur** | `{outil}_extract_{fonction}.py` | `gitlab_extract_users.py` |
| **Exporteur** | `{outil}_export_{format}.py` | `gitlab_export_excel.py` |
| **Script** | `{outil}_script_{fonction}.py` | `gitlab_script_users.py` |
| **Partagé** | `shared_{type}.py` | `shared_config.py` |

#### **Avantages** :
- ✅ **Identification immédiate** : outil + rôle + fonction
- ✅ **Tri alphabétique** naturel par outil
- ✅ **Recherche facilitée** par nom de fichier
- ✅ **Convention uniforme** sur tous les outils
- ✅ **Évolutivité** : nouveau rôle = nouveau dossier

---

## 🚀 **UTILISATION**

### **Orchestrateur principal**
```bash
# Export complet de tous les outils
python maestro_kenobi.py
```

### **Scripts spécialisés**
```bash
# GitLab seulement
python -m kenobi_tools.gitlab.scripts.gitlab_script_users
python -m kenobi_tools.gitlab.scripts.gitlab_script_projects
python -m kenobi_tools.gitlab.scripts.gitlab_script_groups
```

### **Développement - Nouveaux fichiers**

#### **Créer un nouvel extracteur**
1. **Dossier** : `kenobi_tools/{outil}/extractors/`
2. **Nom** : `{outil}_extract_{fonction}.py`
3. **Exemple** : `gitlab_extract_commits.py`

#### **Créer un nouvel outil**
1. **Structure** : Copier `kenobi_tools/gitlab/` → `kenobi_tools/{nouvel_outil}/`
2. **Renommer** tous les fichiers selon la convention
3. **Adapter** le client et les extracteurs

> **💡 Note** : Pour le moment, seul GitLab est implémenté. Les autres outils (SonarQube, Jenkins, etc.) peuvent être ajoutés plus tard en suivant la même structure.

---

## 🚀 **État actuel du projet**

### ✅ **Fonctionnalités implémentées**
- **GitLab** : Extraction projets et utilisateurs
- **Interface** : MAESTRO KENOBI avec barres de progression
- **Export** : Fichiers Excel horodatés
- **Architecture** : Modulaire et extensible

### 🚧 **En développement**
- GitLab : Commits, Events, MR, Pipelines

### 📋 **Roadmap**
1. ✅ **Architecture validée** : Dossiers + convention de nommage
2. ✅ **Migration terminée** : `gitlab_tools/` → `kenobi_tools/gitlab/`
3. � **GitLab complet** : Commits, Events, MR, Pipelines
4. � **Futurs outils** : SonarQube, Jenkins, Docker/K8s (si besoin)

### 🎯 **État actuel**
- **État** : Architecture kenobi_tools/ opérationnelle
- **Fonctionnel** : GitLab Users, Projects, Groups
- **Migration** : ✅ Terminée avec succès

## 📊 **INDICATEURS COLLECTÉS**

### GitLab ✅ **Implémenté**
- **👥 Utilisateurs** : 158 utilisateurs humains (filtrage bot natif + patterns custom)
- **📂 Projets** : Liste des projets, statuts, dernière activité  
- **👥 Groupes** : Organisation et permissions

### 🚧 **En développement GitLab**
- **💾 Commits** : Nombre de commits par projet/période
- **📋 Events** : Activités récentes (push, merge, etc.)
- **🔀 Merge Requests** : Statuts, temps de review
- **🔧 Pipelines** : Succès/échecs, durées

---

## 🛠️ **RÈGLES DE DÉVELOPPEMENT**

### **� Création de nouveaux fichiers**
1. **Respecter l'architecture** définie dans ce README
2. **Suivre les conventions de nommage** : `{outil}_{responsabilité}_{fonction}.py`
3. **Placer dans le bon dossier** selon la responsabilité
4. **Ajouter les imports** et `__init__.py` si nécessaire

### **🔧 Bonnes pratiques**
- **Un fichier = une responsabilité** claire
- **Réutiliser le code partagé** dans `shared/`
- **Documenter les fonctions** avec docstrings
- **Tester localement** avant de commit

### **📊 Standards Excel**
- **Un seul onglet** par fichier Excel
- **Nom d'onglet explicite** : "Gitlab_Users", "Gitlab_Projects", etc.
- **Formatage simple** : données brutes, pas de couleurs/styles complexes
- **Colonnes claires** : noms explicites sans espaces (underscore accepté)
- **Tri chronologique** : le plus récent en premier quand applicable
- **Compatible Power BI** : import direct sans retraitement

### **🎯 Points de référence**
- **Architecture** : Ce README (section structure)
- **Conventions** : Ce README (section conventions)
- **Exemple GitLab** : `kenobi_tools/gitlab/` comme modèle de référence
│   └── exporters/
└── 📁 exports/sonar/ (à venir)
---

## 🚧 **INSTALLATION**

1. **Cloner le projet**
```bash
git clone https://github.com/yassineboury/ETL-DEVOPS-MINIMALIST.git
cd KENOBI_DEVOPS
```

2. **Créer environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les accès**
   - Copier `config/config.example.yaml` vers `config/config.yaml`
   - Renseigner les URLs et tokens GitLab/SonarQube

## ⚙️ **CONFIGURATION**

### config/config.yaml
```yaml
gitlab:
  url: "https://gitlab.votre-entreprise.com"
  token: "${GITLAB_TOKEN}"

extraction:
  batch_size: 50
  delay_between_calls: 1
  timeout: 30
```

### Variables d'environnement (.env)
```bash
GITLAB_TOKEN=your-gitlab-token
```

---

## 📊 **OUTPUTS & POWER BI**

### **📊 Outputs & Power BI**

#### **Fichiers générés**
```
exports/
└── gitlab/
    ├── gitlab_users_filtered.xlsx     # 158 utilisateurs humains
    ├── gitlab_projects.xlsx           # Projets GitLab  
    └── gitlab_groups.xlsx             # Groupes GitLab
```

#### **Format Excel standardisé**
- ✅ **Un seul onglet** par fichier (ex: "Gitlab_Users")
- ✅ **Formatage simple** : données tabulaires, sans mise en forme complexe
- ✅ **Tri par date** : le plus récent en premier
- ✅ **Noms explicites** : colonnes claires et sans espaces
- ✅ **Compatible Power BI** : import direct sans traitement

#### **Import Power BI**
1. **Obtenir les données** > **Fichier** > **Excel**
2. Sélectionner `exports/gitlab/*.xlsx`
3. ✅ **Avantage** : Un seul onglet → sélection automatique
4. Import direct → pas de manipulation nécessaire

---

## 📅 **UTILISATION & PLANIFICATION**

### **Production (recommandé)**
```bash
# Export complet tous outils
python maestro_kenobi.py
```

### **Développement/Tests**
```bash
# GitLab utilisateurs seulement
python -m tools.gitlab.scripts.gitlab_script_users

# GitLab projets seulement
python -m tools.gitlab.scripts.gitlab_script_projects
```

### **Planification automatique**
```bash
# Cron (Linux/macOS) - Dimanche 22h
0 22 * * 0 cd /path/to/KENOBI_DEVOPS && python maestro_kenobi.py

# Tâches planifiées Windows
schtasks /create /tn "KENOBI_EXTRACT" /tr "python maestro_kenobi.py" /sc weekly
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

Les fichiers Excel sont générés dans le dossier `exports/` avec **un seul onglet par fichier** :
- `exports/gitlab/gitlab_projects.xlsx` : Projets GitLab (onglet "Gitlab_Projects")
- `exports/gitlab/gitlab_users_filtered.xlsx` : Utilisateurs humains (onglet "Gitlab_Users")
- `exports/gitlab/gitlab_groups.xlsx` : Groupes GitLab (onglet "Gitlab_Groups")

**Format standardisé :**
- ✅ **Un seul onglet** avec nom explicite
- ✅ **Formatage simple** pour Power BI
- ✅ **Données triées** (plus récent en premier)
- ✅ **Import direct** sans retraitement

### 🔄 **Nettoyage automatique**
MAESTRO KENOBI supprime automatiquement les anciens fichiers avant chaque export.

## Import dans Power BI

1. Ouvrir Power BI Desktop
2. **Obtenir les données** > **Fichier** > **Excel**
3. Sélectionner les fichiers `gitlab_*.xlsx` dans `exports/gitlab/`
4. ✅ **Avantage** : Un seul onglet par fichier → sélection automatique
5. Import direct → Créer vos visualisations

### 💡 **Conseil**
Format standardisé → Import Power BI simplifié (pas de sélection d'onglets multiples).

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
