"""
Utilitaires de dates simplifiés - VERSION REFACTORISÉE
Module pour la gestion des dates avec complexité réduite
"""

import pandas as pd
from datetime import datetime
from typing import Union, Optional

from .constants import DATE_FORMAT_FRENCH


class DateFormatter:
    """Formateur de dates simplifié"""
    
    @staticmethod
    def format_gitlab_date(date_input: Union[str, datetime, pd.Timestamp, None]) -> str:
        """
        Convertit une date GitLab en format français DD/MM/YYYY HH:MM:SS
        
        Args:
            date_input: Date à formater
            
        Returns:
            Date formatée ou "N/A" si invalide
        """
        if not date_input:
            return "N/A"
        
        try:
            # Si c'est déjà un datetime
            if isinstance(date_input, datetime):
                return date_input.strftime(DATE_FORMAT_FRENCH)
            
            # Si c'est un pd.Timestamp
            if isinstance(date_input, pd.Timestamp):
                return date_input.strftime(DATE_FORMAT_FRENCH)
            
            # Convertir string au format ISO vers datetime
            date_str = str(date_input).strip()
            
            # Supporter les formats GitLab courants
            if date_str.endswith('Z'):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif 'T' in date_str:
                dt = datetime.fromisoformat(date_str)
            else:
                # Essayer un parsing direct
                dt = datetime.fromisoformat(date_str)
            
            return dt.strftime(DATE_FORMAT_FRENCH)
            
        except (ValueError, TypeError, AttributeError):
            return str(date_input) if date_input else "N/A"
    
    @staticmethod
    def format_date_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Formate toutes les colonnes de dates dans un DataFrame
        
        Args:
            df: DataFrame à traiter
            
        Returns:
            DataFrame avec dates formatées
        """
        if df.empty:
            return df
        
        # Colonnes de dates communes
        date_columns = [
            'created_at', 'updated_at', 'last_activity_on',
            'last_sign_in_at', 'date_creation', 'derniere_activite',
            'derniere_connexion'
        ]
        
        df_copy = df.copy()
        
        for col in date_columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(DateFormatter.format_gitlab_date)
        
        return df_copy


# Fonctions de compatibilité avec l'ancienne API
def format_gitlab_date(date_input: Union[str, datetime, pd.Timestamp, None]) -> str:
    """Fonction de compatibilité pour le formatage de dates GitLab"""
    return DateFormatter.format_gitlab_date(date_input)


def format_date_for_powerbi(date_input: Union[str, datetime, pd.Timestamp, None]) -> str:
    """Fonction de compatibilité pour Power BI"""
    return DateFormatter.format_gitlab_date(date_input)


def format_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Fonction de compatibilité pour le formatage des colonnes de dates"""
    return DateFormatter.format_date_columns(df)


def validate_date_format(date_str: str) -> bool:
    """Valide si une chaîne est au format français DD/MM/YYYY"""
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        # Vérifier si c'est au format français DD/MM/YYYY HH:MM:SS
        datetime.strptime(date_str.split()[0], "%d/%m/%Y")
        return True
    except (ValueError, IndexError):
        return False
