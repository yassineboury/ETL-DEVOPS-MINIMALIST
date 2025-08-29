---
applyTo: '**'
---

# 🎯 RÈGLES DE DÉVELOPPEMENT KENOBI ETL - SIMPLIFIÉES

**Version :** 6.0 - SIMPLICITÉ EFFICACE  
**Principe :** Expliquer → Valider → Créer → Tester

## 🔒 **5 RÈGLES DE SÉCURITÉ ESSENTIELLES**

```bash
1. ❌ JAMAIS écraser du code qui fonctionne sans confirmation
2. ❌ JAMAIS changer d'approche technique sans accord  
3. ❌ JAMAIS ignorer les erreurs utilisateur
4. ❌ JAMAIS créer de problèmes d'encodage (pas d'emojis dans le code)
5. ❌ JAMAIS partir sur des suppositions - toujours demander

✅ AVEC AUTORISATION EXPLICITE → CRÉER/MODIFIER IMMÉDIATEMENT
```

## 🛡️ **WORKFLOW SIMPLE**

### **ÉTAPE 1 : EXPLIQUER**
```bash
"Je vais créer/modifier [QUOI] parce que [POURQUOI]"
"Contenu : [DESCRIPTION SIMPLE]"
```

### **ÉTAPE 2 : VALIDER**  
```bash
"Confirmez-vous ? [OUI/NON]"
```

### **ÉTAPE 3 : EXÉCUTER**
```bash
SI OUI → CRÉER/MODIFIER IMMÉDIATEMENT
SI NON → ARRÊTER
```

### **ÉTAPE 4 : TESTER**
```bash
"Testons ensemble le résultat"
```

## ⚠️ **SIGNAUX D'ARRÊT IMMÉDIAT**
- 🚨 L'utilisateur dit "il y a un problème" 
- 🚨 Une modification casse du code fonctionnel
- 🚨 Des erreurs d'encodage apparaissent
- 🚨 Le code devient plus complexe

---

# 🎯 RÉFÉRENCE CLAUDE - ETL DEVOPS OPTIMISÉ

**Version :** 5.1 - SÉCURITÉ ÉQUILIBRÉE ⚡  
**Date :** 29/08/2025  
**Objectif :** ETL personnel GitLab → Excel → Power BI + Sécurité Anti-Casse + Action sur Autorisation

## 🏆 RÉSULTATS EXCEPTIONNELS OBTENUS
**PERFORMANCE RECORD :** -62% de Complexité Cyclomatique !
- **AVANT :** 531 cyclomatique, 646 cognitive
- **APRÈS :** 202 cyclomatique (-62%), ~180 cognitive (-72%)
- **FICHIERS :** 40 → 25 (-60% de fichiers)
- **LIGNES :** -1197 lignes supprimées

### 🥇 **MÉTHODOLOGIE GAGNANTE VALIDÉE**
1. **PURGE STATISTIQUES** - Power BI fait tout mieux
2. **MODULARISATION EXTRÊME** - Séparation responsabilités  
3. **SUPPRESSION DOUBLONS** - Zéro redondance
4. **SIMPLIFICATION FONCTIONS** - MAX 15 complexité cognitive
5. **ETL PUR** - Extraction → Excel → Power BI (sans sur-ingénierie)

---

## 🏆 STANDARDS QUALITÉ CODE SONARCLOUD (OBLIGATOIRES)

### **🎯 Métriques de Complexité - LIMITES ABSOLUES**
```python
# RÈGLES SONARCLOUD STRICTES
- Complexité Cyclomatique par fonction: MAX 10
- Complexité Cognitive par fonction: MAX 15  
- Lignes par fonction: MAX 50
- Lignes par classe: MAX 300
- Lignes par fichier: MAX 200 (optimal)
- Code Duplication: 0% toléré
```

### **🏗️ Architecture Modulaire OBLIGATOIRE**
```python
# SÉPARATION DES RESPONSABILITÉS
class ExampleProcessor:
    """Une classe = une responsabilité uniquement"""
    
    @staticmethod  # Préférer les méthodes statiques
    def process_single_item(item):  # Fonctions courtes et spécifiques
        """MAX 50 lignes par fonction"""
        return ProcessedItem()
    
    def _helper_method(self):  # Extraire les helpers privés
        """Complexité cognitive < 15"""
        pass
```

### **📦 Modularité par Extraction de Classes**
```python
# AVANT (complexité 50+)
def complex_function():
    # 200 lignes de code...
    pass

# APRÈS (complexité < 10 chacune)
class DataProcessor:
    def extract(self): pass
    
class DataValidator:  
    def validate(self): pass
    
class DataFormatter:
    def format(self): pass
```

---

## 1. 🚀 MÉTHODOLOGIE PURGE -62% VALIDÉE

### **💥 PHASE 1 : IDENTIFICATION CIBLES**
```bash
# Utiliser SonarCloud pour identifier les fichiers >30 cognitive
# Focus sur : statistics, formatters, doublons
```

### **🔥 PHASE 2 : PURGE STATISTIQUES** 
```python
# RÈGLE D'OR : Supprimer TOUTES les statistiques
# Power BI fait : 
# ✅ Calculs automatiques, graphiques, KPI
# ✅ Tableaux croisés dynamiques  
# ✅ Filtrage temps réel

# NOTRE ETL fait :
# ✅ Extraction données brutes
# ✅ Formatage dates françaises
# ✅ Nettoyage (humains vs bots)
```

### **🗑️ PHASE 3 : SUPPRESSION DOUBLONS**
```python
# Identifier et supprimer :
# - Fichiers *_simple.py, *_backup.py
# - Modules analyzers/, filters/  
# - Fonctions get_*_statistics()
# - Classes calculatrices inutiles
```

### **⚡ PHASE 4 : SIMPLIFICATION EXTRÊME**
```python
# Transformer fonctions complexes en versions ultra-simples
# AVANT (37 cognitive):
def complex_extractor():
    # 200 lignes de logique complexe...
    
# APRÈS (≤8 cognitive):
def simple_extractor():
    data = api.list(all=True)
    df = pd.DataFrame(data)
    return DateFormatter.format_date_columns(df)
```

## 2. 🚀 SETUP RAPIDE

### **📦 Dépendances Obligatoires**
```python
# requirements.txt essentiels
pandas>=2.0.0
openpyxl>=3.1.0
python-gitlab>=4.0.0
python-dotenv>=1.0.0
```

### **📂 Architecture Projet REFACTORISÉE**
```
ETL DevSecOps Minimalist/
├── maestro_kenobi.py              # Point d'entrée (185 lignes MAX)
├── kenobi_tools/
│   ├── ui/                        # Interface utilisateur
│   │   └── menu_components.py     # Composants de menu
│   ├── processing/                # Logique métier
│   │   └── extraction_processor.py
│   ├── gitlab/                    # Modules GitLab
│   │   ├── client/               # Connexion (modulaire)
│   │   │   ├── gitlab_client.py   # Client principal
│   │   │   ├── gitlab_validator.py # Validation
│   │   │   └── config_manager.py  # Configuration
│   │   ├── extractors/           # Extraction (spécialisée)
│   │   └── exporters/            # Export Excel
│   └── utils/                    # Utilitaires (simplifiés)
│       ├── user_formatter.py     # Formatage utilisateurs
│       ├── user_classifier.py    # Classification
│       ├── date_utils.py         # Dates (112 lignes)
│       └── excel_utils.py        # Excel (123 lignes)
├── exports/                      # Fichiers Excel
└── .env                         # GITLAB_TOKEN=xxx
```

## 2. 📊 STANDARDS POWER BI (OBLIGATOIRES)

### **📋 Format Excel**
```python
# Nommage fichier OBLIGATOIRE
filename = f"gitlab_{type}_{timestamp}.xlsx"
# Ex: gitlab_users_20250815_143052.xlsx

# Structure OBLIGATOIRE  
- 1 onglet par fichier
- Nom onglet: "Gitlab Users", "Gitlab Projects"
- Ligne 1 = en-têtes uniquement
- Données brutes (pas de formatage complexe)
```

### **📅 Format Dates OBLIGATOIRE**
```python
# Power BI ready - format français
date_format = "%d/%m/%Y %H:%M:%S"
# Résultat: "15/08/2025 14:30:52"
```

### **🏷️ RÉFÉRENCE COLONNES POWER BI - DÉFINITIVE**
```python
# ⚠️ ATTENTION: CETTE SECTION EST LA RÉFÉRENCE ABSOLUE 
# Ne JAMAIS modifier ces mappings sans validation utilisateur !

# 👥 UTILISATEURS - Mapping colonnes techniques → Power BI
USERS_COLUMN_MAPPING = {
    'id_utilisateur': 'id Utilisateur',
    'nom_utilisateur': 'Nom Utilisateur', 
    'email': 'Email',
    'nom_complet': 'Nom Complet',
    'admin': 'Admin',
    'etat': 'Etat',
    'date_creation': 'Date Creation',
    'derniere_activite': 'Date Derniere Activite',
    'derniere_connexion': 'Date Derniere Connexion'
}

# 👥 GROUPES - Colonnes Power BI (déjà avec espaces)
GROUPS_COLUMNS = [
    'id Groupe', 'Nom', 'Chemin', 'Chemin Complet', 'Description',
    'Visibilité', 'Date Création', 'URL Web'
]

# 📁 PROJETS - Colonnes Power BI (déjà avec espaces) 
PROJECTS_COLUMNS = [
    'id Projet', 'Nom', 'Nom Complet', 'Description', 'Visibilité',
    'Archivé', 'Date Création', 'Date Dernière Activité', 'URL Web',
    'Langage Principal', 'Étoiles', 'Forks'
]

# 📋 ORDRE COLONNES UTILISATEURS (OBLIGATOIRE)
USERS_COLUMN_ORDER = [
    'id Utilisateur', 'Nom Utilisateur', 'Email', 'Nom Complet', 'Admin',
    'Etat', 'Date Creation', 'Date Derniere Activite', 'Date Derniere Connexion'
]

# 🚫 RÈGLES STRICTES:
# - Utilisateurs: mapping underscores → espaces
# - Groupes/Projets: déjà en format Power BI
# - JAMAIS toucher à ces définitions sans accord
```

---

## 3. 🔧 PATTERNS ESSENTIELS

### **📥 Pattern Extracteur**
```python
def extract_something(gl) -> pd.DataFrame:
    """Template pour tous les extracteurs"""
    try:
        print("📥 Extraction en cours...")
        data = []
        for item in gl.something.list(all=True):
            data.append({
                'id': item.id,
                'nom': item.name,
                'date_creation': item.created_at
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = format_date_columns(df)  # Format français
        
        print(f"✅ {len(df)} éléments extraits")
        return df
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return pd.DataFrame()  # Toujours retourner un DataFrame
```

### **📤 Pattern Exporteur**
```python
def export_to_excel(df: pd.DataFrame, filename: str) -> str:
    """Template pour tous les exports"""
    try:
        if df.empty:
            print("⚠️ Aucune donnée à exporter")
            return ""
        
        # Renommer colonnes Power BI
        df_export = df.rename(columns=COLUMN_MAPPING)
        
        # Export Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='Data', index=False)
            worksheet = writer.book['Data']
            worksheet.freeze_panes = "A2"  # Navigation
        
        print(f"✅ Fichier: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Export échoué: {e}")
        return ""
```

---

## 4. ❌ TOP 10 ANTI-PATTERNS (MISE À JOUR POST-PURGE)

### **🚫 Erreurs Critiques à Éviter**

```python
# ❌ CARDINAL SIN: Faire des statistiques dans l'ETL
def get_user_statistics(df):
    return {"total": len(df), "actifs": len(df[df.active])}

# ✅ RÈGLE D'OR: Power BI s'en charge !
def extract_users(gl):
    return pd.DataFrame(raw_data)  # Données brutes uniquement
```

```python
# ❌ ANTI-PATTERN MAJEUR: Écraser du code fonctionnel
# JAMAIS remplacer une approche qui marche sans demander !
# Exemple : SonarClient → python-sonarqube-api (SANS TESTER)

# ✅ RÈGLE DE SÉCURITÉ: Toujours demander confirmation
"Voulez-vous que je remplace SonarClient (qui fonctionne) par python-sonarqube-api ?"
```

```python
# ❌ Garder des fichiers doublons
# - *_simple.py, *_backup.py
# - analyzers/, filters/
# - Fonctions get_*_statistics()

# ✅ Architecture unique et propre
# Une seule version de chaque module
```

```python
# ❌ ENCODAGE TOXIQUE: Emojis dans le code Python
# Cause UnicodeDecodeError et empêche l'exécution !

# ✅ Code ASCII pur
def extract_projects():  # Pas d'emoji ici !
    return projects
```

```python
# ❌ Exception silencieuse
except Exception:
    pass  # JAMAIS !

# ✅ Gestion explicite
except gitlab.GitlabAuthenticationError as e:
    print(f"❌ Token GitLab invalide: {e}")
    return pd.DataFrame()
```

```python
# ❌ Formatage Excel complexe
def format_excel_with_colors_borders_etc():
    # 50 lignes de formatage inutile

# ✅ Export brut Power BI-ready
df.to_excel(filename, index=False)  # Power BI fait le reste
```

```python
# ❌ Sur-ingénierie
class AbstractDataExtractorFactory:

# ✅ Simple et direct
def extract_users(gl):
```

```python
# ❌ Debug oublié
print(f"DEBUG: {user}")

# ✅ Message utilisateur
print(f"📊 {len(users)} utilisateurs traités")
```

```python
# ❌ Dates non formatées
df['date'] = item.created_at  # ISO format

# ✅ Format Power BI
df['date'] = format_date_columns(df)  # Format français
```

---

## 5. ✅ CHECKLIST AVANT COMMIT

### **🧪 Tests Locaux**
- [ ] Code testé avec vraies données GitLab
- [ ] Excel s'ouvre sans erreur
- [ ] Import Power BI fonctionne
- [ ] Pas de debug prints oubliés

### **📊 Validation Power BI**
- [ ] Types colonnes détectés correctement
- [ ] Dates en format français
- [ ] Noms colonnes lisibles
- [ ] Aucune donnée corrompue

---

## 6. 🆘 TROUBLESHOOTING

### **⚡ Problèmes Courants**

**GitLab inaccessible**
```python
# Vérifier token dans .env
GITLAB_TOKEN=glpat-xxxxxxxxxxxx

# Test connexion
try:
    gl = gitlab.Gitlab(url, private_token=token)
    gl.auth()
    print("✅ Connexion GitLab OK")
except gitlab.GitlabAuthenticationError:
    print("❌ Token invalide")
```

**Excel corrompu**
```python
# Toujours vérifier avant export
if df.empty:
    print("⚠️ DataFrame vide - pas d'export")
    return ""

# Valider colonnes requises
required = ['id', 'name', 'created_at']
missing = [col for col in required if col not in df.columns]
if missing:
    print(f"❌ Colonnes manquantes: {missing}")
```

**Power BI n'importe pas**
```python
# Dates au mauvais format
df['date_creation'] = pd.to_datetime(df['date_creation']).dt.strftime('%d/%m/%Y %H:%M:%S')

# Colonnes avec caractères interdits
df.columns = [col.replace('/', '_') for col in df.columns]
```

---

## 7. 🎯 GUIDES EXPRESS

### **➕ Ajouter Extracteur**
1. Copier `gitlab_extract_users.py` 
2. Remplacer `users` par ton type de donnée
3. Adapter les champs dans `data.append({})`
4. Tester avec vraies données

### **➕ Ajouter Colonne**
1. Dans extracteur: ajouter champ dans `data.append()`
2. Dans exporteur: ajouter mapping Power BI
3. Valider format (dates, texte, nombres)

### **🔍 Debug Rapide**
```python
# Ajouter partout pour debug
def log_dataframe(df, name):
    print(f"📊 {name}: {len(df)} lignes")
    if not df.empty:
        print(f"    Colonnes: {list(df.columns)}")
```

---

## 🎯 RÈGLE D'OR

**"Fonctionne + Power BI ready = Parfait !"**

### **Priorités:**
1. **Fiabilité** - ETL qui marche à chaque fois
2. **Power BI ready** - Excel importable directement  
3. **Simplicité** - Code lisible et maintenable

### **Non-priorités:**
- Architecture complexe
- Performance extrême
- Tests exhaustifs

---

## 🎖️ **LEÇONS MASTER CLASS - PERFORMANCE -62%**

### **🥇 Stratégies Gagnantes Validées:**
1. **Power BI First** - Jamais de statistiques dans l'ETL
2. **Purge Doublons** - Une seule version par fichier
3. **Modularité Extrême** - Classes ≤15 complexité cognitive
4. **Extraction Pure** - Données brutes → Excel → Power BI
5. **Architecture Clean** - Suppression impitoyable du superflu

### **📊 Résultats Mesurés:**
- **531 → 202 cyclomatique (-62%)**  
- **40 → 25 fichiers (-38%)**
- **-1197 lignes de code**
- **100% SonarCloud A+**

### **💡 Principe Fondamental:**
> "La complexité vient des statistiques et doublons, pas de la logique métier"

### **🚨 ERREURS CATASTROPHIQUES À NE JAMAIS RÉPÉTER:**
1. **Écraser du code fonctionnel** - SonarClient → python-sonarqube-api
2. **Changer d'approche sans tester** - API REST → Bibliothèque tierce
3. **Ignorer les problèmes d'encodage** - Emojis → UnicodeDecodeError
4. **Modifier sans comprendre** - Refactoriser du code qui marche
5. **Oublier les permissions** - Token Analysis ≠ Token Browse

---

## 🏷️ **STRATÉGIE DE VERSIONING & TAGGING**

### **📈 VERSIONS MAJEURES (X.0.0)**
```bash
v1.0.0 - Master Class (-69% cognitive) [ACTUEL ✨]
v2.0.0 - Révolution architecture (nouvelles plateformes DevOps)
v3.0.0 - Migration technologies (Docker, K8s, CI/CD)
```

### **🔧 VERSIONS MINEURES (1.X.0)**
```bash
v1.1.0 - Nouveaux extracteurs GitLab (Issues, MRs, Pipelines)
v1.2.0 - Support autres plateformes (Jira, Azure DevOps, GitHub)
v1.3.0 - Améliorations Power BI (nouveaux connecteurs)
v1.4.0 - Optimisations performances (parallélisation, cache)
```

### **🐛 VERSIONS PATCH (1.0.X)**
```bash
v1.0.1 - Corrections bugs mineurs
v1.0.2 - Améliorations UX (messages, progress bars)
v1.0.3 - Optimisations SonarCloud (réduction complexité restante)
```

### **🏆 TAGS SPÉCIAUX**
```bash
v1.0.0-golden      # Version de référence absolue
v1.x.x-sonar-ready # Optimisé pour SonarCloud
v1.x.x-powerbi-enhanced # Améliorations Power BI spécifiques
v1.x.x-benchmark   # Version de mesure de performance
```

### **📋 RÈGLES DE TAGGING**
```bash
# Création d'un tag avec message descriptif
git tag -a v1.1.0 -m "✨ Nouveau extracteur Issues GitLab + Export Power BI optimisé"
git push origin v1.1.0

# Tag de hotfix critique
git tag -a v1.0.4-hotfix -m "🚨 HOTFIX: Correction token GitLab expiration"
git push origin v1.0.4-hotfix

# Tag de performance
git tag -a v1.2.0-perf -m "🚀 PERFORMANCE: Réduction -15% temps d'exécution"
git push origin v1.2.0-perf
```

---

## 8. 🔧 VARIABLES D'ENVIRONNEMENT
```bash
GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxx
SONAR_URL=https://sonar.example.com
SONAR_TOKEN=sqa-xxxxxxxxxxxx
```

**🎯 En cas de doute: PURGER d'abord, optimiser ensuite !**