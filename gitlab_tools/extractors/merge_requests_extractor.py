"""
Extracteur de Merge Requests GitLab
Module pour extraire les Merge Requests GitLab selon les spécifications
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


def _translate_state(state: str) -> str:
    """
    Traduit les états de MR GitLab en français
    
    Args:
        state: État GitLab
        
    Returns:
        État traduit en français
    """
    if not state:
        return 'N/A'
    
    translations = {
        'opened': 'ouvert',
        'closed': 'fermé', 
        'merged': 'fusionné',
        'locked': 'verrouillé'
    }
    return translations.get(state, state)


def _translate_merge_status(status: str) -> str:
    """
    Traduit les statuts de fusion GitLab en français
    
    Args:
        status: Statut de fusion GitLab
        
    Returns:
        Statut traduit en français
    """
    if not status:
        return 'N/A'
    
    translations = {
        'can_be_merged': 'peut être fusionné',
        'cannot_be_merged': 'ne peut pas être fusionné',
        'checking': 'vérification en cours',
        'unchecked': 'non vérifié',
        'cannot_be_merged_recheck': 'nouvelle vérification nécessaire'
    }
    return translations.get(status, status)


def _translate_detailed_status(status: str) -> str:
    """
    Traduit les statuts détaillés GitLab en français
    
    Args:
        status: Statut détaillé GitLab
        
    Returns:
        Statut détaillé traduit en français
    """
    if not status:
        return 'N/A'
    
    translations = {
        'mergeable': 'fusionnable',
        'not_open': 'pas ouvert',
        'checking': 'vérification',
        'ci_must_pass': 'CI doit réussir',
        'ci_still_running': 'CI en cours',
        'conflict': 'conflit',
        'discussions_not_resolved': 'discussions non résolues',
        'draft_status': 'statut brouillon',
        'not_approved': 'non approuvé',
        'blocked': 'bloqué'
    }
    return translations.get(status, status)


def _extract_reviewers_ids(reviewers: List[Dict[str, Any]]) -> str:
    """
    Extrait les IDs des reviewers sous forme de chaîne
    
    Args:
        reviewers: Liste des reviewers
        
    Returns:
        IDs séparés par des virgules ou "N/A"
    """
    if not reviewers:
        return "N/A"
    
    try:
        reviewer_ids = [str(reviewer.get('id', '')) for reviewer in reviewers if reviewer.get('id')]
        return ', '.join(reviewer_ids) if reviewer_ids else "N/A"
    except Exception:
        return "N/A"


def extract_merge_requests(gl_client: python_gitlab.Gitlab, include_archived: bool = False) -> pd.DataFrame:
    """
    Extrait toutes les Merge Requests GitLab accessibles
    
    Args:
        gl_client: Client GitLab connecté
        include_archived: Inclure les projets archivés
        
    Returns:
        DataFrame avec les Merge Requests GitLab
    """
    try:
        print("📊 === EXTRACTION DES MERGE REQUESTS GITLAB ===")
        print("📁 Récupération de la liste des projets...")
        
        # Récupérer tous les projets
        all_projects = gl_client.projects.list(all=True, simple=True)
        total_projects = len(all_projects)
        
        print(f"📋 {total_projects} projets trouvés")
        
        mrs_data = []
        processed_projects = 0
        filtered_mrs = 0
        
        for project in all_projects:
            try:
                # Filtrer les projets archivés si nécessaire
                if not include_archived:
                    try:
                        full_project = gl_client.projects.get(project.id)
                        if getattr(full_project, 'archived', False):
                            continue
                    except:
                        continue
                
                # Récupérer les MR du projet
                try:
                    merge_requests = project.mergerequests.list(all=True, per_page=100)
                except:
                    # Si pas d'accès aux MR du projet, passer au suivant
                    continue
                
                if not merge_requests:
                    continue
                
                print(f"📝 Projet '{getattr(project, 'name', 'N/A')}': {len(merge_requests)} MR")
                
                for mr in merge_requests:
                    try:
                        # Récupérer les détails complets de la MR
                        try:
                            full_mr = project.mergerequests.get(mr.iid)
                        except:
                            full_mr = mr
                        
                        # Données utilisateurs
                        author = getattr(full_mr, 'author', {}) or {}
                        assignee = getattr(full_mr, 'assignee', {}) or {}
                        merge_user = getattr(full_mr, 'merge_user', {}) or {}
                        reviewers = getattr(full_mr, 'reviewers', []) or []
                        
                        # Données pipeline
                        head_pipeline = getattr(full_mr, 'head_pipeline', {}) or {}
                        pipeline_status = head_pipeline.get('status', 'N/A') if head_pipeline else 'N/A'
                        
                        mr_info = {
                            'id_merge_request': getattr(full_mr, 'id', 0),
                            'iid_interne': getattr(full_mr, 'iid', 0),
                            'id_projet': getattr(full_mr, 'project_id', 0),
                            'titre': getattr(full_mr, 'title', 'N/A'),
                            'description': getattr(full_mr, 'description', 'N/A') or 'N/A',
                            'etat': _translate_state(getattr(full_mr, 'state', 'N/A')),
                            'brouillon': "Oui" if getattr(full_mr, 'draft', False) else "Non",
                            'date_creation': _format_date(getattr(full_mr, 'created_at', None)),
                            'date_mise_jour': _format_date(getattr(full_mr, 'updated_at', None)),
                            'date_fusion': _format_date(getattr(full_mr, 'merged_at', None)),
                            'date_fermeture': _format_date(getattr(full_mr, 'closed_at', None)),
                            'branche_source': getattr(full_mr, 'source_branch', 'N/A'),
                            'branche_cible': getattr(full_mr, 'target_branch', 'N/A'),
                            'id_auteur': author.get('id', 0) if author else 0,
                            'id_assignee': assignee.get('id', 0) if assignee else 0,
                            'id_reviewers': _extract_reviewers_ids(reviewers),
                            'id_fusionneur': merge_user.get('id', 0) if merge_user else 0,
                            'statut_fusion': _translate_merge_status(getattr(full_mr, 'merge_status', 'N/A')),
                            'statut_detaille': _translate_detailed_status(getattr(full_mr, 'detailed_merge_status', 'N/A')),
                            'conflits': "Oui" if getattr(full_mr, 'has_conflicts', False) else "Non",
                            'pipeline_statut': pipeline_status
                        }
                        
                        mrs_data.append(mr_info)
                        filtered_mrs += 1
                        
                    except Exception as mr_error:
                        print(f"⚠️ Erreur MR ID {getattr(mr, 'id', 'N/A')}: {mr_error}")
                        continue
                
                processed_projects += 1
                
                if processed_projects % 10 == 0:
                    print(f"📈 Progression: {processed_projects}/{total_projects} projets traités")
                
                # Limiter à 50 projets pour éviter les timeouts
                if processed_projects >= 50:
                    print("⚠️ Limitation à 50 projets appliquée")
                    break
                    
            except Exception as project_error:
                print(f"⚠️ Erreur projet ID {getattr(project, 'id', 'N/A')}: {project_error}")
                continue
        
        print(f"✅ {filtered_mrs} Merge Requests extraites sur {processed_projects} projets")

        # Créer le DataFrame
        if mrs_data:
            df = pd.DataFrame(mrs_data)
            
            # Trier par date de création (plus récentes en premier)
            df = df.sort_values('date_creation', ascending=False)
            df = df.reset_index(drop=True)
            
            return df
        else:
            return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des Merge Requests: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    """Test de l'extracteur de Merge Requests"""
    print("🧪 Test de l'extracteur de Merge Requests GitLab")
    print("=" * 50)
    
    # Cette partie serait utilisée pour des tests
    # avec un vrai client GitLab
    pass
