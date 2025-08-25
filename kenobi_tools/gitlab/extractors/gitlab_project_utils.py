"""
Utilitaires communs pour l'extraction des projets GitLab - VERSION ULTRA-SIMPLIFIÉE
Une seule fonction simple pour Power BI
Complexité cognitive visée: ≤ 8
"""
import pandas as pd
import gitlab as python_gitlab
from ...utils.date_utils import DateFormatter


def extract_all_projects(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
    """
    Extrait tous les projets GitLab - VERSION ULTRA-SIMPLE
    
    Args:
        gl_client: Client GitLab authentifié
        include_archived: Inclure les projets archivés
        
    Returns:
        DataFrame avec les données brutes pour Power BI
    """
    try:
        print(f"🔍 Extraction projets (archivés: {'Oui' if include_archived else 'Non'})...")
        
        # Récupération des projets
        projects = gl_client.projects.list(all=True, archived=include_archived)
        
        if not projects:
            print("⚠️ Aucun projet trouvé")
            return pd.DataFrame()
        
        # Construction des données brutes pour Power BI
        data = []
        for project in projects:
            # Extraction des métriques avancées
            try:
                # Compter les branches via l'API (avec pagination)
                branches_count = len(project.branches.list(get_all=False))  # Limite à 20 pour performance
            except:
                branches_count = 0
            
            # Type de namespace - CORRECTION: vérifier namespace.kind correctement
            namespace_type = 'Utilisateur'
            try:
                if hasattr(project, 'namespace') and project.namespace:
                    # Le namespace est un dictionnaire, pas un objet
                    kind = project.namespace.get('kind', 'user')
                    namespace_type = 'Groupe' if kind == 'group' else 'Utilisateur'
            except:
                pass
            
            data.append({
                'id_projet': project.id,
                'nom': project.name,
                'nom_complet': project.path_with_namespace,
                'archive': 'Oui' if getattr(project, 'archived', False) else 'Non',
                'date_creation': project.created_at,
                'date_derniere_activite': project.last_activity_at,
                'total_branches': branches_count,
                'type_namespace': namespace_type
            })
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Format dates pour Power BI
            df = DateFormatter.format_date_columns(df)
            print(f"✅ {len(df)} projets extraits")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction projets: {e}")
        return pd.DataFrame()
