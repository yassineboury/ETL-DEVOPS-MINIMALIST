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

        # Extraire les informations utilisateur essentielles
        user_data = {
            'id_utilisateur': getattr(user, 'id', 0),
            'nom_utilisateur': getattr(user, 'username', 'N/A'),
            'email': getattr(user, 'email', 'N/A'),
            'nom_complet': UserFormatter.format_name(getattr(user, 'name', None)),
            'admin': "Oui" if getattr(user, 'is_admin', False) else "Non",
            'etat': UserFormatter.translate_state(user_state),
            'derniere_activite': format_gitlab_date(getattr(user, 'last_activity_on', None)),
            'derniere_connexion': format_gitlab_date(getattr(user, 'last_sign_in_at', None)),
            'date_creation': format_gitlab_date(getattr(user, 'created_at', None))
        }
        
        return user_data

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


# Toutes les fonctions statistiques supprimées - Power BI fait tout ça mieux !
