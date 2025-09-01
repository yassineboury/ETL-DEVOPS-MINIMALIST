"""
RÉFÉRENCE DÉFINITIVE - MAPPINGS COLONNES POWER BI
Version: 1.0 - VERROUILLÉE ✅
Date: 19/08/2025

⚠️ ATTENTION: Ce fichier définit les mappings OFFICIELS des colonnes
NE JAMAIS modifier sans validation utilisateur explicite !

Objectif: Éviter toute confusion entre noms techniques et noms Power BI
"""

# 🏷️ CONSTANTES COMMUNES POWER BI
ID_UTILISATEUR = 'id Utilisateur'
NOM_COMPLET = 'Nom Complet'
ARCHIVE = 'Archivé'
DATE_CREATION = 'Date Création'
ID_PROJET = 'id Projet'

# 👥 UTILISATEURS - Mapping colonnes techniques → Power BI
USERS_COLUMN_MAPPING = {
    'id_utilisateur': ID_UTILISATEUR,
    'nom_utilisateur': 'Nom Utilisateur', 
    'email': 'Email',
    'nom_complet': NOM_COMPLET,
    'admin': 'Admin',
    'etat': 'Etat',
    'date_creation': 'Date Creation',
    'derniere_activite': 'Date Derniere Activite',
    'derniere_connexion': 'Date Derniere Connexion'
}

# 📋 ORDRE COLONNES UTILISATEURS (OBLIGATOIRE POWER BI)
USERS_COLUMN_ORDER = [
    ID_UTILISATEUR, 'Nom Utilisateur', 'Email', NOM_COMPLET, 'Admin',
    'Etat', 'Date Creation', 'Date Derniere Activite', 'Date Derniere Connexion'
]

# 👥 GROUPES - Mapping colonnes techniques → Power BI
GROUPS_COLUMN_MAPPING = {
    'id_groupe': 'id Groupe',
    'nom': 'Nom',
    'nom_complet': NOM_COMPLET,
    'chemin_complet': 'Chemin Complet',
    'parent_name': 'Groupe Parent',
    'archive': ARCHIVE,
    'date_creation': DATE_CREATION
}

# 📁 PROJETS - Mapping colonnes techniques → Power BI
PROJECTS_COLUMN_MAPPING = {
    'id_projet': ID_PROJET,
    'nom': 'Nom',
    'nom_complet': NOM_COMPLET,
    'archive': ARCHIVE,
    'date_creation': DATE_CREATION,
    'date_derniere_activite': 'Date Dernière Activité',
    'total_branches': 'Total Branches',
    'type_namespace': 'Type Namespace'
}

# 📋 ORDRE COLONNES POWER BI (OBLIGATOIRE)
GROUPS_COLUMN_ORDER = [
    'id Groupe', 'Nom', NOM_COMPLET, 'Chemin Complet', 'Groupe Parent', 
    ARCHIVE, DATE_CREATION
]

PROJECTS_COLUMN_ORDER = [
    ID_PROJET, 'Nom', NOM_COMPLET,
    ARCHIVE, DATE_CREATION, 'Date Dernière Activité',
    'Total Branches', 'Type Namespace'
]

# 👥 GROUPES - Colonnes Power BI (déjà formatées) - OBSOLÈTE
GROUPS_COLUMNS = GROUPS_COLUMN_ORDER

# 📁 PROJETS - Colonnes Power BI (déjà formatées) - OBSOLÈTE  
PROJECTS_COLUMNS = PROJECTS_COLUMN_ORDER

# 📅 ÉVÉNEMENTS - Colonnes Power BI (si activés)
EVENTS_COLUMNS = [
    'id Événement', 'Type Action', 'id Projet', 'Nom Projet', 
    'id Utilisateur', 'Utilisateur', 'Date Événement', 'Branche'
]

# 📅 ÉVÉNEMENTS - Mapping colonnes techniques → Power BI
EVENTS_COLUMN_MAPPING = {
    'id_evenement': 'id Événement',
    'type_action': 'Type Action',
    'id_projet': ID_PROJET,
    'nom_projet': 'Nom Projet',
    'id_utilisateur': ID_UTILISATEUR,
    'utilisateur': 'Utilisateur',
    'date_evenement': 'Date Événement',
    'branche': 'Branche'
}


def get_users_mapping():
    """Retourne le mapping utilisateurs technique → Power BI"""
    return USERS_COLUMN_MAPPING.copy()


def get_users_column_order():
    """Retourne l'ordre des colonnes utilisateurs pour Power BI"""
    return USERS_COLUMN_ORDER.copy()


def get_groups_mapping():
    """Retourne le mapping groupes technique → Power BI"""
    return GROUPS_COLUMN_MAPPING.copy()


def get_projects_mapping():
    """Retourne le mapping projets technique → Power BI"""
    return PROJECTS_COLUMN_MAPPING.copy()


def get_groups_column_order():
    """Retourne l'ordre des colonnes groupes pour Power BI"""
    return GROUPS_COLUMN_ORDER.copy()


def get_projects_column_order():
    """Retourne l'ordre des colonnes projets pour Power BI"""
    return PROJECTS_COLUMN_ORDER.copy()


def get_events_mapping():
    """Retourne le mapping événements technique → Power BI"""
    return EVENTS_COLUMN_MAPPING.copy()


def get_events_column_order():
    """Retourne l'ordre des colonnes événements pour Power BI"""
    return EVENTS_COLUMNS.copy()


def validate_users_columns(df_columns: list) -> bool:
    """
    Valide que les colonnes d'un DataFrame utilisateurs sont correctes
    
    Args:
        df_columns: Liste des colonnes du DataFrame
        
    Returns:
        True si toutes les colonnes attendues sont présentes
    """
    expected_cols = set(USERS_COLUMN_MAPPING.keys())
    actual_cols = set(df_columns)
    
    missing = expected_cols - actual_cols
    extra = actual_cols - expected_cols
    
    if missing:
        print(f"⚠️ Colonnes manquantes: {missing}")
    if extra:
        print(f"⚠️ Colonnes supplémentaires: {extra}")
    
    return len(missing) == 0


# 🚫 RÈGLES DE PROTECTION
class ColumnMappingProtection:
    """Classe pour protéger les mappings contre les modifications accidentelles"""
    
    @staticmethod
    def verify_integrity():
        """Vérifie l'intégrité des mappings"""
        # Vérifier que le mapping et l'ordre sont cohérents
        mapped_cols = set(USERS_COLUMN_MAPPING.values())
        ordered_cols = set(USERS_COLUMN_ORDER)
        
        if mapped_cols != ordered_cols:
            raise ValueError("❌ ERREUR CRITIQUE: Incohérence entre mapping et ordre des colonnes!")
        
        print("✅ Intégrité des mappings colonnes validée")
        return True


if __name__ == "__main__":
    # Test d'intégrité au lancement
    ColumnMappingProtection.verify_integrity()
    
    print("📋 RÉFÉRENCE COLONNES POWER BI")
    print("=" * 50)
    print(f"👥 Utilisateurs: {len(USERS_COLUMN_MAPPING)} colonnes")
    print(f"👥 Groupes: {len(GROUPS_COLUMN_MAPPING)} colonnes") 
    print(f"📁 Projets: {len(PROJECTS_COLUMN_MAPPING)} colonnes")
    print(f"📅 Événements: {len(EVENTS_COLUMN_MAPPING)} colonnes")
    print("\n✅ Référence chargée avec succès")
