"""
Extracteur de groupes GitLab - VERSION ULTRA-SIMPLIFIÉE POWER BI
Extraction pure sans statistiques - Power BI s'en charge !
Complexité cognitive visée: ≤ 8
"""
import pandas as pd
import gitlab as python_gitlab
from ...utils.date_utils import DateFormatter


def extract_groups(gl_client: python_gitlab.Gitlab) -> pd.DataFrame:
    """
    Extrait les groupes GitLab - VERSION SIMPLIFIÉE
    
    Args:
        gl_client: Client GitLab authentifié
        
    Returns:
        DataFrame avec les données brutes pour Power BI
    """
    print("👥 Extraction des groupes GitLab...")
    
    try:
        # Récupération simple sans statistiques
        groups = gl_client.groups.list(all=True)
        
        if not groups:
            print("⚠️ Aucun groupe trouvé")
            return pd.DataFrame()
        
        # Construction des données brutes
        data = []
        for group in groups:
            # Ignorer les archives
            if _is_archive_group(group.full_path):
                continue
            
            # Récupérer le nom du groupe parent
            parent_name = 'N/A'
            try:
                if hasattr(group, 'parent_id') and group.parent_id:
                    parent_group = gl_client.groups.get(group.parent_id)
                    parent_name = parent_group.name
            except:
                pass
                
            data.append({
                'id_groupe': group.id,
                'nom': group.name,
                'nom_complet': getattr(group, 'full_name', group.name),
                'chemin_complet': group.full_path,
                'parent_name': parent_name,
                'archive': 'Oui' if getattr(group, 'archived', False) else 'Non',
                'date_creation': group.created_at
            })
        
        df = pd.DataFrame(data)
        
        if not df.empty:
            # Format dates pour Power BI
            df = DateFormatter.format_date_columns(df)
            print(f"✅ {len(df)} groupes extraits (archives exclues)")
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur extraction groupes: {e}")
        return pd.DataFrame()


def _is_archive_group(full_path: str) -> bool:
    """Vérifie si c'est un groupe d'archives"""
    return full_path.startswith('projets-archives/') or full_path == 'projets-archives'


if __name__ == "__main__":
    """Test simple du module"""
    import sys
    from pathlib import Path
    
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))
    
    from ..client.gitlab_client import GitLabClient
    
    print("🧪 Test extraction groupes - VERSION SIMPLIFIÉE")
    
    try:
        client = GitLabClient()
        gl = client.connect()
        
        df = extract_groups(gl)
        print(f"📊 Résultat: {len(df)} groupes")
        
        client.disconnect()
        print("✅ Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
