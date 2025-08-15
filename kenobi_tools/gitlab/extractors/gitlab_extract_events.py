#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur d'événements GitLab - Version simplifiée
Ce script extrait les événements GitLab avec messages simplifiés et une seule feuille Excel
"""

import sys
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import gitlab as python_gitlab
from pathlib import Path

# Imports locaux - méthode simplifiée
try:
    from kenobi_tools.utils.constants import EXPORTS_GITLAB_PATH
except ImportError:
    EXPORTS_GITLAB_PATH = "exports/gitlab"
def format_gitlab_date(date_str):
    """Format GitLab date string for display"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return date_str

def format_date_columns(df):
    """Format date columns in DataFrame"""
    if 'created_at' in df.columns:
        df['created_at'] = df['created_at'].apply(format_gitlab_date)
    return df

# Import du client GitLab et des utilitaires Excel
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
from client.gitlab_client import create_gitlab_client

# Import des utilitaires Excel (version optimisée pour gros volumes)
utils_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(utils_dir))

# Variables globales pour les imports
export_dataframe_to_excel_light = None
EXCEL_UTILS_AVAILABLE = False

try:
    from kenobi_tools.utils.excel_utils import export_dataframe_to_excel_light
    EXCEL_UTILS_AVAILABLE = True
except ImportError:
    EXCEL_UTILS_AVAILABLE = False
    print("⚠️ excel_utils non disponible - export Excel simple")


def format_user_name(name: str) -> str:
    """Formate un nom d'utilisateur avec la première lettre en majuscule"""
    if not name or name.strip() == "":
        return "N/A"
    formatted_name = name.strip().title()
    return formatted_name if formatted_name else "N/A"


def get_date_filter_choice():
    """Permet à l'utilisateur de choisir un filtre de date"""
    print("\n📅 Choisissez la période des événements:")
    print("1. 30 derniers jours")
    print("2. 3 derniers mois")
    print("3. Année en cours (depuis le début de l'année)")
    print("4. Tous les événements")
    
    while True:
        try:
            choice = input("\nVotre choix (1-4): ").strip()
            
            if choice == "1":
                start_date = datetime.now() - timedelta(days=30)
                after_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
                return after_date, None, "30 derniers jours"
                
            elif choice == "2":
                start_date = datetime.now() - timedelta(days=90)
                after_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
                return after_date, None, "3 derniers mois (90 jours)"
                
            elif choice == "3":
                after_date = f"{datetime.now().year}-01-01T00:00:00Z"
                return after_date, None, f"Année {datetime.now().year}"
                
            elif choice == "4":
                return None, None, "Tous les événements"
                
            else:
                print("❌ Choix invalide. Veuillez saisir 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Extraction annulée par l'utilisateur")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Erreur: {e}")


def extract_events_by_project(
    gl_client: python_gitlab.Gitlab,
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    max_projects: Optional[int] = None,
    action_filter: Optional[str] = None,
    target_type_filter: Optional[str] = None
) -> pd.DataFrame:
    """Extrait les événements GitLab projet par projet"""
    
    try:
        events_data = []
        events_count = 0
        
        print(f"📊 Récupération: TOUS les événements")
        if max_projects:
            print(f"📁 Limite projets: {max_projects} projets maximum")
        if after_date:
            print(f"📅 Après: {format_gitlab_date(after_date)}")
        if before_date:
            print(f"📅 Avant: {format_gitlab_date(before_date)}")

        # Récupérer tous les projets visibles (actifs seulement)
        print("\n📂 Récupération de la liste des projets actifs...")
        try:
            all_projects = gl_client.projects.list(all=True)
            projects = [p for p in all_projects if not getattr(p, 'archived', False)]
            
            print(f"✅ {len(projects)} projets actifs trouvés")
            
            total_projects = len(projects) if max_projects is None else min(len(projects), max_projects)
            print(f"📊 {total_projects} projets à analyser")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des projets: {e}")
            return pd.DataFrame()
        
        # Parcourir chaque projet pour extraire ses événements
        projects_to_process = projects[:max_projects] if max_projects else projects
        
        for i, project in enumerate(projects_to_process):
            print(f"\n📁 Projet {i+1}/{total_projects}: {project.name} (ID: {project.id})")
            
            try:
                # Paramètres pour les événements du projet
                event_params = {}
                
                if after_date:
                    event_params['after'] = after_date
                if before_date:
                    event_params['before'] = before_date
                if action_filter:
                    event_params['action'] = action_filter
                if target_type_filter:
                    event_params['target_type'] = target_type_filter
                
                # Récupérer les événements du projet
                project_events = project.events.list(all=True, **event_params)
                
                if not project_events:
                    print(f"   📭 Aucun événement trouvé")
                    continue
                
                print(f"   📄 {len(project_events)} événements trouvés")
                
                # Traiter chaque événement
                for event in project_events:
                    try:
                        # Extraire les informations de l'événement
                        event_data = {
                            'id': event.id,
                            'project_id': project.id,
                            'project_name': project.name,
                            'project_path': project.path_with_namespace,
                            'action_name': getattr(event, 'action_name', ''),
                            'target_type': getattr(event, 'target_type', ''),
                            'target_id': getattr(event, 'target_id', ''),
                            'target_title': getattr(event, 'target_title', ''),
                            'author_id': event.author.get('id', '') if event.author else '',
                            'author_name': format_user_name(event.author.get('name', '')) if event.author else 'N/A',
                            'author_username': event.author.get('username', '') if event.author else '',
                            'created_at': event.created_at,
                            'imported': getattr(event, 'imported', False),
                            'imported_from': getattr(event, 'imported_from', ''),
                        }
                        
                        # Ajouter les données de push si disponibles
                        if hasattr(event, 'push_data') and event.push_data:
                            push_data = event.push_data
                            event_data.update({
                                'push_commit_count': push_data.get('commit_count', 0),
                                'push_action': push_data.get('action', ''),
                                'push_ref': push_data.get('ref', '').replace('refs/heads/', ''),
                                'push_ref_type': push_data.get('ref_type', ''),
                                'push_commit_from': push_data.get('commit_from', ''),
                                'push_commit_to': push_data.get('commit_to', ''),
                            })
                        else:
                            # Initialiser avec des valeurs vides pour les événements non-push
                            event_data.update({
                                'push_commit_count': 0,
                                'push_action': '',
                                'push_ref': '',
                                'push_ref_type': '',
                                'push_commit_from': '',
                                'push_commit_to': '',
                            })
                        
                        events_data.append(event_data)
                        events_count += 1
                        
                        if events_count % 100 == 0:
                            print(f"   📊 {events_count} événements traités...")
                            
                    except Exception as e:
                        print(f"   ⚠️ Erreur sur événement {getattr(event, 'id', 'N/A')}: {e}")
                        continue
                        
            except Exception as e:
                print(f"   ❌ Erreur pour le projet {project.name}: {e}")
                continue

        print(f"✅ {len(events_data)} événements extraits")
        
        if not events_data:
            print("❌ Aucun événement trouvé")
            return pd.DataFrame()

        # Créer le DataFrame
        df = pd.DataFrame(events_data)
        
        # Appliquer le formatage des dates
        df = format_date_columns(df)
        
        # Trier par ID décroissant (plus récents en premier)
        if not df.empty and 'id' in df.columns:
            df = df.sort_values('id', ascending=False).reset_index(drop=True)
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des événements: {e}")
        return pd.DataFrame()


def main():
    """Fonction principale"""
    try:
        # Création du client GitLab
        print("🔐 Connexion à GitLab...")
        gitlab_client = create_gitlab_client()
        gl_client = gitlab_client.connect()
        
        print(f"✅ Connecté à GitLab: {gl_client.url}")
        try:
            if hasattr(gl_client, 'user') and gl_client.user and hasattr(gl_client.user, 'username'):
                print(f"👤 Utilisateur: {gl_client.user.username}")
            else:
                print("👤 Utilisateur: (informations non disponibles)")
        except:
            print("👤 Utilisateur: (erreur lors de la récupération)")
        
        # Configuration
        max_projects = None  # Limite de projets (None = tous)
        
        # Choix de la période
        after_date, before_date, period_desc = get_date_filter_choice()
        
        print(f"\n📊 Configuration:")
        print(f"   Période: {period_desc}")
        print(f"   Événements: TOUS (sans limite)")
        if max_projects:
            print(f"   Projets: {max_projects} projets maximum")
        
        # Extraction des événements par projet
        df_events = extract_events_by_project(
            gl_client=gl_client,
            after_date=after_date,
            before_date=before_date,
            max_projects=max_projects
        )
        
        if df_events.empty:
            print("❌ Aucun événement trouvé")
            return

        # Analyser les types d'événements (résumé)
        print(f"\n📊 {len(df_events)} événements trouvés")
        
        # Top 5 des actions les plus fréquentes
        top_actions = df_events['action_name'].value_counts().head(5)
        print(f"   Actions principales: {', '.join([f'{action} ({count})' for action, count in top_actions.items()])}")
        
        # Préparer les données pour Excel
        print(f"📁 Export vers Excel...")
        
        # Préparer toutes les colonnes
        df_all_events = df_events.copy()
        
        # Remplir les valeurs manquantes avec N/A (simple)
        df_all_events = df_all_events.fillna('N/A')
        df_all_events = df_all_events.replace('', 'N/A')
        
        # Colonnes pour Excel (tous les champs disponibles)
        excel_columns = {
            'id': 'ID Evenement',
            'project_id': 'ID Projet', 
            'project_name': 'Nom Projet',
            'project_path': 'Chemin Projet',
            'action_name': 'Action',
            'created_at': 'Date Creation',
            'author_id': 'ID Utilisateur',
            'author_name': 'Nom Utilisateur',
            'push_action': 'Action Push',
            'push_ref': 'Branche',
            'push_ref_type': 'Type Reference',
            'target_type': 'Type Cible',
            'target_title': 'Titre Cible'
        }
        
        # Export vers Excel avec formatage minimal (optimisé gros volumes)
        print(f"� Export vers Excel...")
        
        if EXCEL_UTILS_AVAILABLE and export_dataframe_to_excel_light is not None:
            # Utiliser les utilitaires Excel optimisés
            filepath = export_dataframe_to_excel_light(
                df=df_all_events,
                filename="gitlab_events.xlsx",
                sheet_name="Gitlab Events",
                column_mapping=excel_columns,
                exports_dir=EXPORTS_GITLAB_PATH,
                auto_adjust_columns=True
            )
            filename = filepath
        else:
            # Fallback: export Excel simple
            import os
            os.makedirs(EXPORTS_GITLAB_PATH, exist_ok=True)
            filename = os.path.join(EXPORTS_GITLAB_PATH, "gitlab_events.xlsx")
            
            # Sélectionner et renommer les colonnes
            available_columns = [col for col in excel_columns.keys() if col in df_all_events.columns]
            df_for_export = df_all_events[available_columns].copy()
            df_for_export = df_for_export.rename(columns={col: excel_columns[col] for col in available_columns})
            
            print(f"📝 Écriture Excel simple ({len(df_for_export)} lignes)...")
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_for_export.to_excel(writer, sheet_name='Gitlab Events', index=False)
        
        print(f"\n✅ Export terminé!")
        print(f"📁 Fichier: {filename}")
        print(f"📊 {len(df_all_events)} événements • {df_events['project_id'].nunique() if 'project_id' in df_events.columns else 'N/A'} projets")
        
    except KeyboardInterrupt:
        print("\n👋 Extraction annulée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            if 'gl_client' in locals():
                print("🔌 Connexion GitLab fermée")
        except:
            pass


if __name__ == "__main__":
    main()
