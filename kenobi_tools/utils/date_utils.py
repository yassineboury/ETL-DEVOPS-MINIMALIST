#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires pour la gestion des dates et formats français
Optimisés pour Power BI et exports Excel
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Union, Optional, Any, List
from .constants import DATE_FORMAT_FRENCH, DATE_FORMAT_ISO_Z


def format_date_for_powerbi(date_input: Union[str, datetime, pd.Timestamp, None]) -> str:
    """
    Convertit une date en format français DD/MM/YYYY HH:MM:SS pour Power BI
    
    Args:
        date_input: Date à formater (str, datetime, pd.Timestamp ou None)
    
    Returns:
        str: Date formatée en français ou "N/A" si invalide
    
    Examples:
        >>> format_date_for_powerbi("2025-08-15T14:30:00Z")
        "15/08/2025 14:30:00"
    """
    
    try:
        # Si c'est déjà un objet datetime
        if isinstance(date_input, datetime):
            return date_input.strftime(DATE_FORMAT_FRENCH)
        
        # Si c'est un pd.Timestamp
        if isinstance(date_input, pd.Timestamp):
            return date_input.strftime(DATE_FORMAT_FRENCH)
            
        # Si c'est None ou vide
        if not date_input or str(date_input).strip() == '':
            return "N/A"
            
        # Convertir en string et nettoyer
        date_str = str(date_input).strip()
        
        # Si c'est déjà au bon format, vérifier et retourner
        if validate_date_format(date_str):
            return date_str
        
        # Essayer de parser depuis différents formats ISO
        try:
            # Format ISO avec Z
            if date_str.endswith('Z'):
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime(DATE_FORMAT_FRENCH)
            
            # Format ISO sans Z
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str)
                return dt.strftime(DATE_FORMAT_FRENCH)
                
        except ValueError:
            pass
        
        # Autres tentatives de parsing
        formats_to_try = [
            DATE_FORMAT_ISO_Z,
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y"
        ]
        
        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(DATE_FORMAT_FRENCH)
            except ValueError:
                continue
                
        # Si aucun format ne fonctionne
        return "N/A"
        
    except Exception:
        return "N/A"


def format_gitlab_date(date_input: Optional[Union[str, datetime, Any]]) -> str:
    """
    Formate une date GitLab vers le format standard DD/MM/YYYY HH:MM:SS
    
    Args:
        date_input: Date à formater (string ISO, datetime, ou autre)
        
    Returns:
        Date formatée en string DD/MM/YYYY HH:MM:SS ou "N/A"
    """
    if not date_input or str(date_input).lower() in ['none', 'nat', 'null', '']:
        return "N/A"
    
    try:
        # Convertir en string pour traitement
        date_str = str(date_input).strip()
        
        if not date_str or date_str.lower() in ['none', 'nat', 'null']:
            return "N/A"
        
        # Différents formats ISO possibles
        formats_to_try = [
            # Format ISO complet avec Z
            lambda d: datetime.fromisoformat(d.replace('Z', '+00:00')),
            # Format ISO complet sans Z
            lambda d: datetime.fromisoformat(d),
            # Format avec microsecondes
            lambda d: datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%fZ"),
            # Format sans microsecondes
            lambda d: datetime.strptime(d, DATE_FORMAT_ISO_Z),
            # Format standard SQL
            lambda d: datetime.strptime(d, "%Y-%m-%d %H:%M:%S"),
            # Format date seule
            lambda d: datetime.strptime(d, "%Y-%m-%d"),
        ]
        
        # Essayer chaque format
        for format_func in formats_to_try:
            try:
                dt = format_func(date_str)
                return dt.strftime(DATE_FORMAT_FRENCH)
            except (ValueError, TypeError):
                continue
        
        # Si aucun format ne fonctionne, retourner la valeur originale
        return date_str
        
    except Exception as e:
        print(f"⚠️ Erreur formatage date '{date_input}': {e}")
        return str(date_input) if date_input else "N/A"


def format_date_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Applique le formatage de date à une colonne entière d'un DataFrame
    
    Args:
        df: DataFrame à traiter
        column_name: Nom de la colonne à formater
        
    Returns:
        DataFrame avec la colonne formatée
    """
    if column_name not in df.columns:
        return df
    
    try:
        df_copy = df.copy()
        df_copy[column_name] = df_copy[column_name].apply(format_gitlab_date)
        return df_copy
    except Exception as e:
        print(f"⚠️ Erreur formatage colonne '{column_name}': {e}")
        return df


def format_date_columns(df: pd.DataFrame, date_column_patterns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Applique le formatage de date à toutes les colonnes de dates d'un DataFrame
    
    Args:
        df: DataFrame à traiter
        date_column_patterns: Liste de patterns pour identifier les colonnes de dates
                             Par défaut: ['date', 'created_at', 'updated_at', 'last_']
        
    Returns:
        DataFrame avec toutes les colonnes de dates formatées
    """
    if date_column_patterns is None:
        date_column_patterns = ['date', 'created_at', 'updated_at', 'last_']
    
    df_result = df.copy()
    
    # Identifier les colonnes de dates
    date_columns = []
    for col in df.columns:
        col_lower = col.lower()
        if any(pattern in col_lower for pattern in date_column_patterns):
            date_columns.append(col)
    
    # Formater chaque colonne de date
    for col in date_columns:
        print(f"📅 Formatage colonne date: {col}")
        df_result = format_date_column(df_result, col)
    
    return df_result


def get_date_range_filter(period_choice: str) -> tuple:
    """
    Génère des filtres de dates selon une période prédéfinie
    
    Args:
        period_choice: '30days', 'current_year', 'all'
        
    Returns:
        tuple: (after_date_iso, before_date_iso, description)
    """
    now = datetime.now()
    
    if period_choice == '30days':
        after_date = (now - pd.Timedelta(days=30)).isoformat() + "Z"
        return after_date, None, "30 derniers jours"
    
    elif period_choice == 'current_year':
        after_date = f"{now.year}-01-01T00:00:00Z"
        return after_date, None, f"Année {now.year}"
    
    elif period_choice == 'all':
        return None, None, "Tous les événements"
    
    else:
        raise ValueError(f"Période inconnue: {period_choice}")


def validate_date_format(date_str: str) -> bool:
    """
    Valide si une date est dans le format DD/MM/YYYY HH:MM:SS
    
    Args:
        date_str: String à valider
        
    Returns:
        True si le format est correct, False sinon
    """
    if not date_str or date_str == "N/A":
        return True  # N/A est acceptable
    
    try:
        datetime.strptime(date_str, DATE_FORMAT_FRENCH)
        return True
    except (ValueError, TypeError):
        return False


# Constantes utiles
DATE_FORMAT_DISPLAY = DATE_FORMAT_FRENCH
DATE_FORMAT_ISO = DATE_FORMAT_ISO_Z

# Patterns courants pour identifier les colonnes de dates
COMMON_DATE_PATTERNS = [
    'date', 'created_at', 'updated_at', 'last_', 'time', 'when',
    'début', 'fin', 'creation', 'modification', 'evenement'
]
