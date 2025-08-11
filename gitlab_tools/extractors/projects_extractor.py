"""
Extracteur de projets GitLab
Module pour extraire les informations des projets GitLab selon les spécifications
"""
import gitlab as python_gitlab
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


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
        
    except Exception as e:
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
        # Vérifier s'il y a une branche par défaut
        default_branch = getattr(project, 'default_branch', None)
        if not default_branch:
            return "Oui"
        
        # Vérifier s'il y a des commits
        try:
            commits = project.commits.list(per_page=1)
            if not commits:
                return "Oui"
        except:
            # Si on ne peut pas accéder aux commits, considérer comme vide
            return "Oui"
        
        return "Non"
        
    except Exception:
        return "Inconnu"


def extract_projects(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
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
                
                # Informations du namespace
                namespace = getattr(project, 'namespace', {})
                namespace_name = namespace.get('name', 'N/A') if isinstance(namespace, dict) else str(namespace)
                namespace_kind = namespace.get('kind', 'user') if isinstance(namespace, dict) else 'user'
                
                # Propriétaire du projet
                owner = getattr(project, 'owner', {})
                owner_name = owner.get('name', 'N/A') if isinstance(owner, dict) else 'N/A'
                
                # Dernière activité
                last_activity = getattr(project, 'last_activity_at', None)
                
                # Essayer de récupérer le dernier commit
                last_commit_date = "N/A"
                try:
                    if getattr(project, 'default_branch', None):
                        commits = project.commits.list(per_page=1)
                        if commits:
                            last_commit_date = _format_date(getattr(commits[0], 'created_at', None))
                except:
                    last_commit_date = "N/A"
                
                # Langage principal - utiliser une approche simple pour éviter les erreurs d'API
                main_language = "N/A"
                try:
                    # Pour l'instant, laisser N/A car l'API languages() pose des problèmes de type
                    # TODO: Améliorer cette logique si nécessaire
                    main_language = "N/A"
                except Exception:
                    main_language = "N/A"
                
                # Extraire les informations du projet selon les spécifications
                project_info = {
                    'id_projet': getattr(project, 'id', 0),
                    'nom_projet': getattr(project, 'name', 'N/A'),
                    'nom_complet': getattr(project, 'path_with_namespace', 'N/A'),
                    'url_web': getattr(project, 'web_url', 'N/A'),
                    'namespace': namespace_name,
                    'type_namespace': _translate_namespace_kind(namespace_kind),
                    'proprietaire': owner_name,
                    'date_creation': _format_date(getattr(project, 'created_at', None)),
                    'derniere_activite': _format_date(last_activity),
                    'dernier_commit': last_commit_date,
                    'langage_principal': main_language,
                    'etat': _determine_project_state(project),
                    'archivé': "Oui" if is_archived else "Non",
                    'vide': _is_empty_project(project),
                }
                
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
    """Test de l'extracteur de projets"""
    import sys
    from pathlib import Path
    
    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    
    from client.gitlab_client import create_gitlab_client
    
    print("🧪 Test de l'extracteur de projets GitLab")
    print("=" * 60)
    
    try:
        # Créer le client GitLab
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        # Test 1: Statistiques générales
        print("\n1️⃣ Statistiques générales:")
        stats = get_project_statistics(gl)
        
        # Test 2: Extraction des projets actifs
        print("\n2️⃣ Extraction des projets actifs:")
        active_projects = extract_active_projects(gl)
        
        if not active_projects.empty:
            print(f"   Colonnes: {', '.join(active_projects.columns)}")
            print(f"   Premiers projets:")
            for i, project in active_projects.head(3).iterrows():
                print(f"     - {project['nom_projet']} ({project['namespace']}) - {project['etat']}")
        
        # Test 3: Tous les projets (avec archivés)
        print("\n3️⃣ Extraction de tous les projets:")
        all_projects = extract_projects(gl, include_archived=True)
        
        if not all_projects.empty:
            print(f"   📊 {len(all_projects)} projets trouvés")
            print(f"   États: {all_projects['etat'].value_counts().to_dict()}")
        
        gitlab_client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        sys.exit(1)
    
    print("\n🎉 Test terminé avec succès!")
