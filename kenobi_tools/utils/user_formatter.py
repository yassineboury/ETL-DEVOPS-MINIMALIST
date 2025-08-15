"""
Utilitaires de formatage pour les utilisateurs GitLab
Sépare la logique de formatage pour réduire la complexité cognitive
"""
from typing import Optional


class UserFormatter:
    """Formatage et validation des données utilisateur"""
    
    @staticmethod
    def format_name(name: Optional[str]) -> str:
        """
        Formate un nom avec la première lettre en majuscule et supprime le contenu entre parenthèses
        
        Args:
            name: Nom à formater
            
        Returns:
            Nom formaté avec première lettre majuscule, sans contenu entre parenthèses
        """
        if not name or name.strip() == "":
            return "N/A"

        cleaned_name = UserFormatter._remove_parentheses_content(name)
        
        # Nettoyer les espaces multiples
        cleaned_name = ' '.join(cleaned_name.split())

        # Nettoyer le nom et capitaliser proprement
        formatted_name = cleaned_name.strip().title()

        # Si après nettoyage il ne reste rien, retourner N/A
        if not formatted_name:
            return "N/A"

        return formatted_name

    @staticmethod
    def _remove_parentheses_content(text: str) -> str:
        """Supprime le contenu entre parenthèses de manière sécurisée"""
        cleaned_text = text
        
        # Supprimer toutes les occurrences de contenu entre parenthèses
        while '(' in cleaned_text and ')' in cleaned_text:
            start_paren = cleaned_text.find('(')
            if start_paren == -1:
                break
            end_paren = cleaned_text.find(')', start_paren)
            if end_paren == -1:
                break
            # Supprimer tout ce qui est entre parenthèses, y compris les parenthèses
            cleaned_text = cleaned_text[:start_paren] + cleaned_text[end_paren + 1:]
        
        return cleaned_text

    @staticmethod
    def translate_state(state: str) -> str:
        """
        Traduit l'état d'un utilisateur en français
        
        Args:
            state: État en anglais (active, blocked, deactivated)
            
        Returns:
            État traduit en français
        """
        state_translations = {
            'active': 'Actif',
            'blocked': 'Bloqué',
            'deactivated': 'Désactivé',
            'ldap_blocked': 'Bloqué'  # Cas particulier LDAP
        }

        return state_translations.get(state.lower(), state.capitalize())
