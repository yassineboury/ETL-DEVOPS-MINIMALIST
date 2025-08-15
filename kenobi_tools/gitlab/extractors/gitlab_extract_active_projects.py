"""
Extracteur de projets GitLab
Module pour extraire les informations des projets GitLab selon les spécifications
"""
from datetime import datetime
from typing import Any, Dict, Optional

import gitlab as python_gitlab
import pandas as pd


def _format_date(date_string: Optional[str]) -> str:
    """
    Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS

    Args:
        date_string: Date au format ISO

    Returns:
        Date formatée ou "N/A" si None
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


def _translate_namespace_kind(kind: str) -> str:
    """
    Traduit le type de namespace en français

    Args:
        kind: Type de namespace GitLab

    Returns:
        Type traduit en français
    """
    translations = {
        'user': 'Utilisateur',
        'group': 'Groupe',
        'subgroup': 'Sous-groupe'
    }
    return translations.get(kind.lower(), kind.capitalize())


def _determine_project_state(project) -> str:
    """
    Détermine l'état du projet

    Args:
        project: Objet projet GitLab

    Returns:
        État du projet: "Actif", "Archivé", "Supprimé"
    """
    if getattr(project, 'archived', False):
        return "Archivé"
    elif hasattr(project, 'marked_for_deletion_at') and getattr(project, 'marked_for_deletion_at', None):
        return "Supprimé"
    else:
        return "Actif"


def _is_empty_project(project) -> str:
    """
    Détermine si le projet est vide (sans commits)

    Args:
        project: Objet projet GitLab

    Returns:
        "Oui" si vide, "Non" sinon
    """
    try:
        # Essayer de récupérer la liste des commits (explicitement get_all=False)
        commits = project.commits.list(per_page=1, get_all=False)
        if not commits:
            return "Oui"
        return "Non"
    except Exception:
        # Si on ne peut pas accéder aux commits, considérer comme vide
        return "Oui"


def _extract_namespace_info(project) -> tuple[str, str]:
    """
    Extrait les informations du namespace

    Args:
        project: Objet projet GitLab

    Returns:
        Tuple (nom_namespace, type_namespace)
    """
    try:
        namespace = getattr(project, 'namespace', {})
        
        if isinstance(namespace, dict):
            namespace_name = namespace.get('name', namespace.get('path', 'N/A'))
            namespace_kind = namespace.get('kind', 'user')
            return namespace_name, namespace_kind
        else:
            # Fallback: utiliser path_with_namespace pour extraire le namespace
            path_with_namespace = getattr(project, 'path_with_namespace', '')
            if '/' in path_with_namespace:
                namespace_name = path_with_namespace.split('/')[0]
                namespace_kind = 'user'
                return namespace_name, namespace_kind
                
        return 'N/A', 'user'
        
    except Exception:
        return 'N/A', 'user'


def _extract_last_commit_date(project) -> str:
    """
    Extrait la date du dernier commit

    Args:
        project: Objet projet GitLab

    Returns:
        Date formatée du dernier commit ou "N/A"
    """
    try:
        if getattr(project, 'default_branch', None):
            commits = project.commits.list(per_page=1, get_all=False)
            if commits:
                return _format_date(getattr(commits[0], 'created_at', None))
    except Exception:
        pass
    return "N/A"


def _get_dominant_language(project) -> str:
    """
    Récupère le langage principal du projet depuis l'API GitLab
    
    Args:
        project: Objet projet GitLab
        
    Returns:
        Nom du langage principal ou "N/A" si indisponible
    """
    try:
        # Essayer de récupérer les langages du projet
        languages = project.languages()
        
        if languages:
            # Trouver le langage avec le plus haut pourcentage
            dominant_language = max(languages.items(), key=lambda x: x[1])
            return dominant_language[0]
            
    except Exception as e:
        # En cas d'erreur d'API ou d'accès, ignorer silencieusement
        pass
        
    return "N/A"


def _build_project_info(project) -> Dict[str, Any]:
    """
    Construit les informations du projet

    Args:
        project: Objet projet GitLab

    Returns:
        Dictionnaire avec les informations du projet
    """
    namespace_name, namespace_kind = _extract_namespace_info(project)
    last_activity = getattr(project, 'last_activity_at', None)
    last_commit_date = _extract_last_commit_date(project)
    is_archived = getattr(project, 'archived', False)

    return {
        'id_projet': getattr(project, 'id', 0),
        'nom_projet': getattr(project, 'name', 'N/A'),
        'nom_complet': getattr(project, 'path_with_namespace', 'N/A'),
        'url_web': getattr(project, 'web_url', 'N/A'),
        'namespace': namespace_name,
        'type_namespace': _translate_namespace_kind(namespace_kind),
        'date_creation': _format_date(getattr(project, 'created_at', None)),
        'derniere_activite': _format_date(last_activity),
        'dernier_commit': last_commit_date,
        'langage_principal': _get_dominant_language(project),
        'etat': _determine_project_state(project),
        'archivé': "Oui" if is_archived else "Non",
        'vide': _is_empty_project(project),
    }


def extract_projects(
    gl_client: python_gitlab.Gitlab, include_archived: bool = False
) -> pd.DataFrame:
    """
    Extrait les projets GitLab selon les spécifications

    Args:
        gl_client: Client GitLab authentifié
        include_archived: Inclure les projets archivés (défaut: False)

    Returns:
        DataFrame avec les informations des projets
    """
    print("🔍 Extraction des projets GitLab...")

    projects_data = []
    total_projects = 0
    filtered_projects = 0

    try:
        # Récupérer tous les projets
        all_projects = gl_client.projects.list(all=True, statistics=True)
        total_projects = len(all_projects)
        print(f"📊 {total_projects} projets trouvés au total")

        for project in all_projects:
            try:
                # Filtrer les projets archivés si demandé
                is_archived = getattr(project, 'archived', False)
                if not include_archived and is_archived:
                    continue

                # Construire les informations du projet
                project_info = _build_project_info(project)
                projects_data.append(project_info)
                filtered_projects += 1

            except Exception as project_error:
                print(f"⚠️ Erreur projet ID {getattr(project, 'id', 'N/A')}: {project_error}")
                continue

        print(f"✅ {filtered_projects} projets extraits sur {total_projects} total")

        # Créer et retourner le DataFrame
        df = pd.DataFrame(projects_data)

        # Trier par nom de projet
        if not df.empty:
            df = df.sort_values('nom_projet', ascending=True)
            df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des projets: {e}")
        return pd.DataFrame()


def extract_active_projects(gl_client: python_gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait uniquement les projets actifs (non archivés)

    Args:
        gl_client: Client GitLab authentifié

    Returns:
        DataFrame avec les projets actifs uniquement
    """
    print("🔍 Extraction des projets actifs uniquement...")
    return extract_projects(gl_client, include_archived=False)


def get_project_statistics(gl_client: python_gitlab.Gitlab) -> Dict[str, Any]:
    """
    Récupère des statistiques sur les projets

    Args:
        gl_client: Client GitLab authentifié

    Returns:
        Dictionnaire avec les statistiques des projets
    """
    print("📊 Calcul des statistiques des projets...")

    try:
        all_projects = gl_client.projects.list(all=True)

        stats = {
            'total_projects': len(all_projects),
            'active_projects': 0,
            'archived_projects': 0,
            'empty_projects': 0,
            'user_projects': 0,
            'group_projects': 0,
        }

        for project in all_projects:
            try:
                # Compter par état
                if getattr(project, 'archived', False):
                    stats['archived_projects'] += 1
                else:
                    stats['active_projects'] += 1

                # Compter par type de namespace
                namespace = getattr(project, 'namespace', {})
                namespace_kind = namespace.get('kind', 'user') if isinstance(namespace, dict) else 'user'
                if namespace_kind == 'user':
                    stats['user_projects'] += 1
                else:
                    stats['group_projects'] += 1

                # Compter les projets vides
                if _is_empty_project(project) == "Oui":
                    stats['empty_projects'] += 1

            except Exception:
                continue

        print("📊 Statistiques calculées:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        return stats

    except Exception as e:
        print(f"❌ Erreur lors du calcul des statistiques: {e}")
        return {}


if __name__ == "__main__":
    """Test de l'extracteur de projets - VERSION OPTIMISÉE"""
    import sys
    from pathlib import Path

    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    from client.gitlab_client import create_gitlab_client

    print("🧪 Extraction et export Excel des projets GitLab")
    print("=" * 60)

    try:
        # Créer le client GitLab
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        # Extraction directe des projets actifs seulement
        print("\n📊 Extraction des projets actifs...")
        active_projects = extract_active_projects(gl)

        if not active_projects.empty:
            print(f"   ✅ {len(active_projects)} projets actifs extraits")
            print(f"   États: {active_projects['etat'].value_counts().to_dict()}")
        
        gitlab_client.disconnect()

        # Export Excel immédiat
        print("\n📁 Export Excel:")
        if not active_projects.empty:
            try:
                # Import de l'exporteur Excel
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
                
                # Créer l'exporteur et générer le fichier Excel
                exporter = GitLabExcelExporter()
                excel_path = exporter.export_projects(active_projects, "gitlab_active_projects.xlsx", "Gitlab Active Projects")
                
                if excel_path:
                    print(f"✅ Fichier Excel généré: {excel_path}")
                else:
                    print("❌ Erreur lors de la génération du fichier Excel")
            except Exception as excel_error:
                print(f"❌ Erreur export Excel: {excel_error}")
        else:
            print("❌ Aucun projet à exporter")

        gitlab_client.disconnect()

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        sys.exit(1)

    print("\n🎉 Export terminé avec succès!")
