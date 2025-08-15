"""
Extracteur de groupes GitLab - Kenobi Tools
Module pour extraire les informations des groupes GitLab selon les spécifications DevSecOps
Optimisé pour export Excel avec métriques de gouvernance et sécurité
"""
from datetime import datetime
from typing import Optional
import pandas as pd
import gitlab as python_gitlab


def extract_groups(gl_client: python_gitlab.Gitlab, include_statistics: bool = True) -> pd.DataFrame:
    """
    Extrait les groupes GitLab avec leurs informations principales
    
    Args:
        gl_client: Instance du client GitLab
        include_statistics: Inclure les statistiques des groupes
        
    Returns:
        DataFrame avec les informations des groupes
    """
    try:
        print("🔍 Extraction des groupes GitLab...")
        
        # Récupération de tous les groupes accessibles
        groups = gl_client.groups.list(all=True, statistics=include_statistics)
        groups_data = []
        ignored_groups_count = 0
        
        for group in groups:
            # Filtrer les groupes dans projets-archives/ ET le groupe racine projets-archives
            full_path = getattr(group, 'full_path', '')
            if full_path.startswith('projets-archives/') or full_path == 'projets-archives':
                ignored_groups_count += 1
                continue
                
            group_info = {
                'id': group.id,
                'name': group.name,
                'path': group.path,
                'full_name': getattr(group, 'full_name', ''),
                'full_path': getattr(group, 'full_path', ''),
                'description': getattr(group, 'description', ''),
                'visibility': getattr(group, 'visibility', ''),
                'created_at': _format_date(getattr(group, 'created_at', None)),
                'web_url': getattr(group, 'web_url', ''),
                'parent_id': getattr(group, 'parent_id', None),
            }
            
            # Essayer différentes méthodes pour obtenir les statistiques
            projects_count = 0
            members_count = 0
            subgroups_count = 0
            
            if include_statistics:
                # Méthode 1: statistics directement
                if hasattr(group, 'statistics'):
                    stats = group.statistics
                    projects_count = stats.get('projects_count', 0)
                    members_count = stats.get('members_count', 0) 
                    subgroups_count = stats.get('subgroups_count', 0)
                
                # Méthode 2: attributs directs
                if projects_count == 0:
                    projects_count = getattr(group, 'projects_count', 0)
                if members_count == 0:
                    members_count = getattr(group, 'members_count', 0)
                if subgroups_count == 0:
                    subgroups_count = getattr(group, 'subgroups_count', 0)
                
                # Méthode 3: calcul via les listes (plus lent mais plus fiable)
                try:
                    if projects_count == 0:
                        projects = group.projects.list(all=True)
                        projects_count = len(projects)
                except:
                    pass
                    
                try:
                    if members_count == 0:
                        members = group.members.list(all=True)
                        members_count = len(members)
                except:
                    pass
                    
                try:
                    if subgroups_count == 0:
                        subgroups = group.subgroups.list(all=True)
                        subgroups_count = len(subgroups)
                except:
                    pass
            
            # Ajouter les compteurs au groupe
            group_info.update({
                'projects_count': projects_count,
                'members_count': members_count,
                'subgroups_count': subgroups_count,
            })
            
            # Ajouter nom du groupe parent
            parent_name = "N/A"
            if group_info['parent_id']:
                try:
                    parent_group = gl_client.groups.get(group_info['parent_id'])
                    parent_name = parent_group.name
                except:
                    pass
            group_info['parent_name'] = parent_name
            
            groups_data.append(group_info)
        
        df = pd.DataFrame(groups_data)
        
        # Résumé de l'extraction
        print(f"✅ {len(df)} groupes extraits")
        if ignored_groups_count > 0:
            print(f"⏭️ {ignored_groups_count} groupes archivés ignorés")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des groupes : {e}")
        raise


def _format_date(date_string: Optional[str]) -> str:
    """Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS"""
    if not date_string:
        return "N/A"
    
    try:
        # Parse ISO format
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, AttributeError):
        return date_string or "N/A"


if __name__ == "__main__":
    """Extraction et export Excel des groupes GitLab - VERSION OPTIMISÉE"""
    import sys
    from pathlib import Path

    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    from client.gitlab_client import create_gitlab_client

    print("🧪 Extraction et export Excel des groupes GitLab")
    print("=" * 60)

    try:
        # Créer le client GitLab
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        # Extraction directe des groupes
        print("\n📊 Extraction des groupes...")
        all_groups = extract_groups(gl, include_statistics=True)

        if not all_groups.empty:
            print(f"   ✅ {len(all_groups)} groupes extraits")
            print(f"   Visibilités: {all_groups['visibility'].value_counts().to_dict()}")

        gitlab_client.disconnect()

        # Export Excel immédiat
        print("\n📁 Export Excel:")
        if not all_groups.empty:
            try:
                # Import de l'exporteur Excel
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
                from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
                
                # Créer l'exporteur et générer le fichier Excel
                exporter = GitLabExcelExporter()
                excel_path = exporter.export_groups(all_groups, "gitlab_groups.xlsx")
                
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
            print("❌ Aucun groupe à exporter")
            print("\n❌ Export échoué!")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        sys.exit(1)
