"""
Extracteur d'utilisateurs GitLab - VERSION REFACTORISÉE
Module pour extraire uniquement les vrais utilisateurs (pas les bots/services)
Complexité cognitive réduite via séparation des responsabilités
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

import gitlab as python_gitlab
import pandas as pd
from ...utils.constants import ERROR_EXPORT_FAILED

from kenobi_tools.utils.date_utils import format_gitlab_date
from kenobi_tools.utils.user_formatter import UserFormatter
from kenobi_tools.utils.user_classifier import UserClassifier


def extract_human_users(
    gl_client: python_gitlab.Gitlab, include_blocked: bool = True
) -> pd.DataFrame:
    """
    Extrait uniquement les utilisateurs humains de GitLab - VERSION SIMPLIFIÉE
    
    Args:
        gl_client: Client GitLab authentifié
        include_blocked: Inclure les utilisateurs bloqués (défaut: True)
        
    Returns:
        DataFrame avec les informations des utilisateurs humains
    """
    print("🔍 Extraction des utilisateurs humains GitLab...")

    users_data = []
    
    try:
        # Récupérer et filtrer les utilisateurs
        all_users = gl_client.users.list(all=True)
        total_users = len(all_users)
        print(f"📊 {total_users} utilisateurs trouvés au total")

        # Filtrer et extraire en une seule passe
        for user in all_users:
            user_data = _process_single_user(user, include_blocked)
            if user_data:
                users_data.append(user_data)

        filtered_users = len(users_data)
        print(f"✅ {filtered_users} utilisateurs humains extraits sur {total_users}")

        return _create_users_dataframe(users_data)

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des utilisateurs: {e}")
        return pd.DataFrame()


def _process_single_user(user, include_blocked: bool) -> Optional[Dict[str, Any]]:
    """
    Traite un utilisateur individuel
    
    Args:
        user: Objet utilisateur GitLab
        include_blocked: Inclure les utilisateurs bloqués
        
    Returns:
        Dictionnaire avec les données utilisateur ou None si à exclure
    """
    try:
        # Filtrer les utilisateurs humains
        if not UserClassifier.is_human_user(user):
            return None

        # Filtrer par état si demandé
        user_state = getattr(user, 'state', 'active')
        if not include_blocked and user_state in ['blocked', 'deactivated']:
            return None

        # Extraire les informations utilisateur
        return {
            'id_utilisateur': getattr(user, 'id', 0),
            'nom_utilisateur': getattr(user, 'username', 'N/A'),
            'email': getattr(user, 'email', 'N/A'),
            'nom_complet': UserFormatter.format_name(getattr(user, 'name', None)),
            'admin': "Oui" if getattr(user, 'is_admin', False) else "Non",
            'etat': UserFormatter.translate_state(user_state),
            'derniere_activite': format_gitlab_date(getattr(user, 'last_activity_on', None)),
            'derniere_connexion': format_gitlab_date(getattr(user, 'last_sign_in_at', None)),
            'date_creation': format_gitlab_date(getattr(user, 'created_at', None)),
            'confirmation_email': "Oui" if getattr(user, 'confirmed_at', None) else "Non",
            'projets_crees': getattr(user, 'projects_limit', 0),
            'identite_externe': "Oui" if getattr(user, 'external', False) else "Non",
            'organisation': getattr(user, 'organization', '') or 'N/A',
            'localisation': getattr(user, 'location', '') or 'N/A',
            'site_web': getattr(user, 'web_url', '') or 'N/A',
            'theme': getattr(user, 'theme_id', 1),
            'couleur': getattr(user, 'color_scheme_id', 1)
        }

    except Exception as e:
        print(f"⚠️  Erreur traitement utilisateur {getattr(user, 'username', 'inconnu')}: {e}")
        return None


def _create_users_dataframe(users_data: list) -> pd.DataFrame:
    """
    Crée le DataFrame final avec les utilisateurs
    
    Args:
        users_data: Liste des données utilisateur
        
    Returns:
        DataFrame formaté
    """
    if not users_data:
        print("⚠️ Aucun utilisateur humain trouvé")
        return pd.DataFrame()

    df = pd.DataFrame(users_data)
    
    # Trier par nom d'utilisateur
    df = df.sort_values('nom_utilisateur', ascending=True)
    
    # Réinitialiser l'index
    df = df.reset_index(drop=True)
    
    return df


# Fonctions auxiliaires pour maintenir la compatibilité
def get_user_summary_stats(df_users: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule des statistiques résumées sur les utilisateurs
    
    Args:
        df_users: DataFrame des utilisateurs
        
    Returns:
        Dictionnaire avec les statistiques
    """
    if df_users.empty:
        return {}

    return {
        'total_utilisateurs': len(df_users),
        'utilisateurs_actifs': len(df_users[df_users['etat'] == 'Actif']),
        'utilisateurs_bloques': len(df_users[df_users['etat'] == 'Bloqué']),
        'utilisateurs_desactives': len(df_users[df_users['etat'] == 'Désactivé']),
        'administrateurs': len(df_users[df_users['admin'] == 'Oui']),
        'utilisateurs_externes': len(df_users[df_users['identite_externe'] == 'Oui'])
    }


def filter_users_by_activity(df_users: pd.DataFrame, days_threshold: int = 90) -> pd.DataFrame:
    """
    Filtre les utilisateurs par activité récente
    
    Args:
        df_users: DataFrame des utilisateurs
        days_threshold: Seuil en jours pour considérer un utilisateur comme actif (utilisé pour future extension)
        
    Returns:
        DataFrame filtré
    """
    if df_users.empty:
        return df_users

    # Cette fonction pourrait être étendue avec une logique de filtrage par date
    # Pour l'instant, retourne tous les utilisateurs actifs
    # Le paramètre days_threshold est préservé pour compatibilité future
    _ = days_threshold  # Utilisation explicite pour éviter l'erreur
    return df_users[df_users['etat'] == 'Actif']
