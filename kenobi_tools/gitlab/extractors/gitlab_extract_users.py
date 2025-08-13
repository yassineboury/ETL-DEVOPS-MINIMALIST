"""
Extracteur d'utilisateurs GitLab
Module pour extraire uniquement les vrais utilisateurs (pas les bots/services)
"""
from datetime import datetime
from typing import Any, Dict, Optional

import gitlab as python_gitlab
import pandas as pd


def _format_date(date_string: Optional[str]) -> str:
    """
    Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS

    Args:
        date_string: Date au format ISO (ex: "2024-01-15T14:30:25.123Z")

    Returns:
        Date formatée (ex: "15/01/2024 14:30:25") ou "N/A" si None
    """
    if not date_string:
        return "N/A"

    try:
        # Parser la date ISO (gérer différents formats)
        if 'T' in date_string:
            # Format ISO complet
            date_part = date_string.split('T')[0]
            time_part = date_string.split('T')[1].split('.')[0].split('+')[0].split('Z')[0]
        else:
            # Format date simple
            date_part = date_string.split(' ')[0] if ' ' in date_string else date_string
            time_part = date_string.split(' ')[1] if ' ' in date_string else "00:00:00"

        # Parser la date
        dt = datetime.strptime(f"{date_part} {time_part[:8]}", "%Y-%m-%d %H:%M:%S")

        # Formater vers DD/MM/YYYY HH:MM:SS
        return dt.strftime("%d/%m/%Y %H:%M:%S")

    except Exception:
        # En cas d'erreur, retourner la chaîne originale ou N/A
        return date_string if date_string else "N/A"


def _format_name(name: Optional[str]) -> str:
    """
    Formate un nom avec la première lettre en majuscule et supprime le contenu entre parenthèses

    Args:
        name: Nom à formater

    Returns:
        Nom formaté avec première lettre majuscule, sans contenu entre parenthèses
    """
    if not name or name.strip() == "":
        return "N/A"

    # Supprimer le contenu entre parenthèses de manière sécurisée
    # Utiliser une approche simple sans regex complexe pour éviter ReDoS
    cleaned_name = name

    # Supprimer toutes les occurrences de contenu entre parenthèses
    while '(' in cleaned_name and ')' in cleaned_name:
        start_paren = cleaned_name.find('(')
        if start_paren == -1:
            break
        end_paren = cleaned_name.find(')', start_paren)
        if end_paren == -1:
            break
        # Supprimer tout ce qui est entre parenthèses, y compris les parenthèses
        cleaned_name = cleaned_name[:start_paren] + cleaned_name[end_paren + 1:]

    # Nettoyer les espaces multiples
    cleaned_name = ' '.join(cleaned_name.split())

    # Nettoyer le nom et capitaliser proprement
    formatted_name = cleaned_name.strip().title()

    # Si après nettoyage il ne reste rien, retourner N/A
    if not formatted_name:
        return "N/A"

    return formatted_name


def _translate_state(state: str) -> str:
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


def _determine_user_type(user) -> str:
    """
    Détermine si un utilisateur est Humain, Bot ou Service

    Args:
        user: Objet utilisateur GitLab

    Returns:
        Type d'utilisateur: "Humain", "Bot", "Service"
    """
    # Priorité 1: Vérifier l'attribut natif GitLab
    is_gitlab_bot = getattr(user, 'bot', False)
    if is_gitlab_bot:
        return "Bot"
    
    username = getattr(user, 'username', '').lower()
    name = getattr(user, 'name', '').lower()
    email = getattr(user, 'email', '').lower()

    # Patterns pour identifier les services (comptes techniques spécifiques à l'organisation)
    service_patterns = [
        'deploy', 'service', 'system', 'backup', 'monitoring', 'alert',
        'scheduler', 'cron', 'batch', 'process', 'gitlabuser', 'sonarqube',
        'nexus', 'artifactory', 'prometheus', 'grafana', 'kibana', 'elastic',
        'gitlab-duo', 'gitlabduo', 'duo', 'pic-', 'jks', 'atman_netopia'
    ]

    # Vérifier les patterns de service (comptes techniques organisationnels)
    for pattern in service_patterns:
        if pattern in username or pattern in name or pattern in email:
            return "Service"

    # Patterns pour identifier les bots non détectés par GitLab (legacy ou custom)
    bot_patterns = [
        'robot', 'ci', 'cd', 'build', 'jenkins', 'gitlab-ci',
        'admin', 'noreply', 'ghost', 'runner'
    ]

    # Vérifier les patterns de bot custom
    for pattern in bot_patterns:
        if pattern in username or pattern in name or pattern in email:
            return "Bot"

    # Par défaut, considérer comme humain
    return "Humain"


def _is_human_user(user) -> bool:
    """
    Filtre pour déterminer si un utilisateur est humain

    Args:
        user: Objet utilisateur GitLab

    Returns:
        True si l'utilisateur est considéré comme humain
    """
    user_type = _determine_user_type(user)

    # Ne garder que les humains
    if user_type != "Humain":
        return False

    # Exclure les utilisateurs "ghost" (supprimés)
    username = getattr(user, 'username', '').lower()
    if 'ghost' in username or username.startswith('ghost'):
        return False

    # Exclure les comptes techniques avec nom identique au username (sauf prénoms simples)
    name = getattr(user, 'name', '').lower()
    if username == name and len(username) > 5:  # Éviter d'exclure des prénoms courts
        return False

    # Exclure les états non pertinents (garder active, blocked et deactivated)
    state = getattr(user, 'state', 'active')
    return state in ['active', 'blocked', 'deactivated']


def extract_human_users(
    gl_client: python_gitlab.Gitlab, include_blocked: bool = True
) -> pd.DataFrame:
    """
    Extrait uniquement les utilisateurs humains de GitLab

    Args:
        gl_client: Client GitLab authentifié
        include_blocked: Inclure les utilisateurs bloqués (défaut: True)

    Returns:
        DataFrame avec les informations des utilisateurs humains
    """
    print("🔍 Extraction des utilisateurs humains GitLab...")

    users_data = []
    total_users = 0
    filtered_users = 0

    try:
        # Récupérer tous les utilisateurs
        all_users = gl_client.users.list(all=True)
        total_users = len(all_users)
        print(f"📊 {total_users} utilisateurs trouvés au total")

        for user in all_users:
            try:
                # Filtrer les utilisateurs humains
                if not _is_human_user(user):
                    continue

                # Filtrer par état si demandé
                user_state = getattr(user, 'state', 'active')
                if not include_blocked and user_state in ['blocked', 'deactivated']:
                    continue

                # Extraire les informations utilisateur
                user_info = {
                    'id_utilisateur': getattr(user, 'id', 0),
                    'nom_utilisateur': getattr(user, 'username', 'N/A'),
                    'email': getattr(user, 'email', 'N/A'),
                    'nom_complet': _format_name(getattr(user, 'name', None)),
                    'admin': "Oui" if getattr(user, 'is_admin', False) else "Non",
                    'etat': _translate_state(user_state),
                    'type_utilisateur': _determine_user_type(user),
                    'date_creation': _format_date(getattr(user, 'created_at', None)),
                    'date_validation': _format_date(getattr(user, 'confirmed_at', None)),
                    'derniere_activite': _format_date(getattr(user, 'last_activity_on', None)),
                    'derniere_connexion': _format_date(getattr(user, 'current_sign_in_at', None)),
                }

                users_data.append(user_info)
                filtered_users += 1

            except Exception as user_error:
                print(f"⚠️ Erreur utilisateur ID {getattr(user, 'id', 'N/A')}: {user_error}")
                continue

        print(f"✅ {filtered_users} utilisateurs humains extraits sur {total_users} total")

        # Créer et retourner le DataFrame
        df = pd.DataFrame(users_data)

        # Trier par nom d'utilisateur
        if not df.empty:
            df = df.sort_values('nom_utilisateur', ascending=True)
            df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des utilisateurs: {e}")
        return pd.DataFrame()


def _update_type_statistics(stats: Dict[str, int], user_type: str):
    """Met à jour les statistiques par type d'utilisateur"""
    if user_type == "Humain":
        stats['human_users'] += 1
    elif user_type == "Bot":
        stats['bot_users'] += 1
    else:
        stats['service_users'] += 1


def _update_state_statistics(stats: Dict[str, int], state: str):
    """Met à jour les statistiques par état d'utilisateur"""
    if state == 'active':
        stats['active_users'] += 1
    elif state == 'blocked':
        stats['blocked_users'] += 1
    elif state == 'deactivated':
        stats['deactivated_users'] += 1


def _update_user_attributes(stats: Dict[str, int], user, thirty_days_ago):
    """Met à jour les statistiques pour les attributs utilisateur"""
    # Compter les admins
    if getattr(user, 'is_admin', False):
        stats['admin_users'] += 1

    # Compter ceux avec email
    if getattr(user, 'email', None):
        stats['users_with_email'] += 1

    # Activité récente
    last_activity = getattr(user, 'last_activity_on', None)
    if last_activity:
        try:
            activity_date = datetime.strptime(last_activity, "%Y-%m-%d").replace(tzinfo=None)
            if activity_date > thirty_days_ago:
                stats['recent_activity'] += 1
        except (ValueError, TypeError):
            pass


def _process_user_for_stats(user, stats: Dict[str, int], thirty_days_ago):
    """Traite un utilisateur pour les statistiques"""
    try:
        user_type = _determine_user_type(user)
        state = getattr(user, 'state', 'active')

        _update_type_statistics(stats, user_type)
        _update_state_statistics(stats, state)
        _update_user_attributes(stats, user, thirty_days_ago)

    except Exception:
        pass


def get_user_statistics(gl_client: python_gitlab.Gitlab) -> Dict[str, Any]:
    """
    Récupère des statistiques sur les utilisateurs

    Args:
        gl_client: Client GitLab authentifié

    Returns:
        Dictionnaire avec les statistiques utilisateurs
    """
    print("📊 Calcul des statistiques utilisateurs...")

    try:
        all_users = gl_client.users.list(all=True)

        stats = {
            'total_users': len(all_users),
            'human_users': 0,
            'bot_users': 0,
            'service_users': 0,
            'active_users': 0,
            'blocked_users': 0,
            'deactivated_users': 0,
            'admin_users': 0,
            'users_with_email': 0,
            'recent_activity': 0  # Dernière activité < 30 jours
        }

        thirty_days_ago = datetime.now().replace(tzinfo=None) - pd.Timedelta(days=30)

        for user in all_users:
            _process_user_for_stats(user, stats, thirty_days_ago)

        print("📊 Statistiques calculées:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        return stats

    except Exception as e:
        print(f"❌ Erreur lors du calcul des statistiques: {e}")
        return {}


if __name__ == "__main__":
    """Extraction et export Excel des utilisateurs GitLab - VERSION OPTIMISÉE"""
    import sys
    from pathlib import Path

    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    from client.gitlab_client import create_gitlab_client

    print("🧪 Extraction et export Excel des utilisateurs GitLab")
    print("=" * 60)

    try:
        # Créer le client GitLab
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        # Extraction directe de tous les utilisateurs humains
        print("\n📊 Extraction des utilisateurs humains...")
        all_human_users = extract_human_users(gl)

        if not all_human_users.empty:
            print(f"   ✅ {len(all_human_users)} utilisateurs humains extraits")
            print(f"   États: {all_human_users['etat'].value_counts().to_dict()}")

        gitlab_client.disconnect()

        # Export Excel immédiat
        print("\n📁 Export Excel:")
        if not all_human_users.empty:
            try:
                # Import de l'exporteur Excel
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
                
                # Créer l'exporteur et générer le fichier Excel
                exporter = GitLabExcelExporter()
                excel_path = exporter.export_users(all_human_users)
                
                if excel_path:
                    print(f"✅ Fichier Excel généré: {excel_path}")
                    print("\n🎉 Export terminé avec succès!")
                else:
                    print("❌ Erreur lors de la génération du fichier Excel")
                    print("\n❌ Export échoué!")
                    sys.exit(1)
            except Exception as excel_error:
                print(f"❌ Erreur export Excel: {excel_error}")
                print("\n❌ Export échoué!")
                sys.exit(1)
        else:
            print("❌ Aucun utilisateur à exporter")
            print("\n❌ Export échoué!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        sys.exit(1)
