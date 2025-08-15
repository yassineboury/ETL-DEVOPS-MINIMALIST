---
applyTo: '**'
---
# 🎯 RÉFÉRENCE CLAUDE - ETL SIMPLE & EFFICACE

**Version :** 2.0  
**Date :** 15/08/2025  
**Objectif :** ETL personnel GitLab → Excel → Power BI

---

## 1. 🚀 SETUP RAPIDE

### **� Dépendances Obligatoires**
```python
# requirements.txt essentiels
pandas>=2.0.0
openpyxl>=3.1.0
python-gitlab>=4.0.0
python-dotenv>=1.0.0
```

### **📂 Structure Projet**
```
ETL DevSecOps Minimalist/
├── maestro_kenobi.py              # Point d'entrée
├── kenobi_tools/gitlab/           # Outils GitLab
│   ├── client/, extractors/, exporters/
├── exports/                       # Fichiers Excel
└── .env                          # GITLAB_TOKEN=xxx
```

---

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

### **🏷️ Noms Colonnes Power BI**
```python
# Espaces autorisés, caractères spéciaux OK
COLUMNS = {
    "id_utilisateur": "id Utilisateur",
    "nom_utilisateur": "Nom Utilisateur",
    "date_creation": "Date Creation",
    # Éviter: underscores, CamelCase
}
```

---

## 3. 🔧 PATTERNS ESSENTIELS

### **� Pattern Extracteur**
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

## 4. ❌ TOP 5 ANTI-PATTERNS

### **🚫 Erreurs Critiques à Éviter**

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
# ❌ Magic numbers
if len(col) > 60: width = 60

# ✅ Constantes nommées
MAX_COLUMN_WIDTH = 60
if len(col) > MAX_COLUMN_WIDTH: width = MAX_COLUMN_WIDTH
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

### **� Tests Locaux**
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

### **� Problèmes Courants**

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

### **� Debug Rapide**
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

**� Variables d'environnement requises:**
```bash
GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxx
```

**🎯 En cas de doute: garder simple et pragmatique !**
