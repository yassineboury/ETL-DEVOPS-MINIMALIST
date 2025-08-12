#!/usr/bin/env python3
"""
📅 EXTRACTION EVENTS GITLAB - VERSION SIMPLE        # Limiter le nombre de lignes si trop volumineux - SUPPRIMÉ
        # if len(df_events) > 10000:
        #     print(f"⚠️ Fichier volumineux ({len(df_events)} événements). Limitation à 10 000 lignes les plus récentes.")
        #     df_events_sorted = df_events.sort_values('created_at', ascending=False)
        #     df_events = df_events_sorted.head(10000).copy()n simplifiée pour résoudre les problèmes d'ouverture Excel
"""

import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le projet au path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.events_extractor import extract_events


def choose_period():
    """
    Propose un menu interactif pour choisir la période d'extraction
    
    Returns:
        int: Nombre de jours en arrière (ou None pour toutes les dates)
    """
    print("📅 CHOIX DE LA PÉRIODE D'EXTRACTION")
    print("=" * 40)
    print("1️⃣  30 derniers jours")
    print("2️⃣  Dernière année (365 jours)")
    print("3️⃣  Toutes les dates (extraction complète)")
    print("=" * 40)
    
    while True:
        try:
            choice = input("Votre choix (1, 2 ou 3): ").strip()
            
            if choice == "1":
                print("✅ Sélection: 30 derniers jours")
                return 30
            elif choice == "2":
                print("✅ Sélection: Dernière année (365 jours)")
                return 365
            elif choice == "3":
                print("✅ Sélection: Toutes les dates")
                return None  # None = pas de limitation
            else:
                print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
                
        except KeyboardInterrupt:
            print("\n❌ Extraction annulée par l'utilisateur")
            sys.exit(1)
        except Exception:
            print("❌ Erreur de saisie. Veuillez réessayer.")


def export_events_simple(df_events: pd.DataFrame, filename: str = "gitlab_events_simple.xlsx"):
    """
    Export Excel simplifié sans formatage complexe
    
    Args:
        df_events: DataFrame des événements
        filename: Nom du fichier
        
    Returns:
        str: Chemin du fichier créé
    """
    try:
        # Créer le répertoire d'export s'il n'existe pas
        export_dir = Path("exports/gitlab")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = export_dir / filename
        
        # PAS DE LIMITATION - extraire tous les événements pour Power BI
        # (ancienne limitation supprimée)
        
        # Export simple sans formatage complexe
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Feuille principale
            df_events.to_excel(writer, sheet_name='Événements', index=False)
            
            # Feuille de statistiques simples
            stats_data = {
                'Métrique': [
                    'Nombre total d\'événements',
                    'Période d\'extraction', 
                    'Date d\'export',
                    'Types d\'actions uniques',
                    'Projets concernés'
                ],
                'Valeur': [
                    len(df_events),
                    'Variable selon sélection',
                    pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S'),
                    df_events['nom_action'].nunique() if 'nom_action' in df_events.columns else 'N/A',
                    df_events['nom_projet'].nunique() if 'nom_projet' in df_events.columns else 'N/A'
                ]
            }
            
            # SUPPRESSION DE LA FEUILLE STATISTIQUES - UNE SEULE FEUILLE DEMANDÉE
            # stats_df = pd.DataFrame(stats_data)
            # stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
            
        print(f"✅ Export simple réussi: {file_path}")
        file_size = file_path.stat().st_size / 1024  # KB
        print(f"📊 Fichier créé: {file_path.name} ({file_size:.1f} KB)")
        return str(file_path)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export simple: {e}")
        return ""


def extract_events_to_excel_simple(days_back=None):
    """
    Extraction simple des events GitLab vers Excel (sans formatage complexe)
    
    Args:
        days_back: Nombre de jours en arrière pour filtrer les événements (None = toutes les dates)
    """
    print("📅 EXTRACTION EVENTS GITLAB - VERSION SIMPLE")
    print("=" * 50)
    
    if days_back is not None:
        print(f"📅 Période: {days_back} derniers jours")
    else:
        print("📅 Période: Toutes les dates")
    print()
    
    gitlab_client = None  # Initialiser la variable
    
    try:
        # 1. Charger la configuration
        print("🔑 Chargement de la configuration...")
        load_dotenv()
        
        # 2. Connexion GitLab
        print("🌐 Connexion à GitLab ONCF...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        if not gl:
            print("❌ Impossible de se connecter à GitLab")
            return False
            
        print("✅ Connexion GitLab établie")
        
        # 3. Extraction des events
        if days_back is not None:
            print(f"📅 Extraction des events GitLab ({days_back} derniers jours)...")
        else:
            print("📅 Extraction de tous les events GitLab...")
        events_df = extract_events(gl, include_archived=False, days_back=days_back)
        
        if events_df.empty:
            print("❌ Aucun event trouvé")
            return False
            
        events_count = len(events_df)
        print(f"✅ {events_count} events extraits")
        
        # 4. Export vers Excel (version simple)
        print("📊 Export vers Excel (version simple)...")
        excel_file = export_events_simple(events_df, filename="gitlab_events_simple.xlsx")
        
        if excel_file:
            print(f"✅ Fichier créé: {Path(excel_file).name}")
            print(f"📂 Emplacement: {excel_file}")
            return True
        else:
            print("❌ Erreur lors de la création du fichier Excel")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Fermer la connexion
        if gitlab_client is not None:
            gitlab_client.disconnect()
            print("🔌 Connexion fermée")


if __name__ == "__main__":
    print("🚀 Lancement de l'extraction events (version simple)...")
    
    # Menu interactif pour choisir la période
    days_back = choose_period()
    
    # Lancer l'extraction avec la période choisie
    success = extract_events_to_excel_simple(days_back)
    
    if success:
        if days_back is not None:
            print(f"\n🎉 Extraction terminée avec succès! (événements des {days_back} derniers jours)")
        else:
            print("\n🎉 Extraction terminée avec succès! (tous les événements)")
    else:
        print("\n❌ Extraction échouée")
    
    sys.exit(0 if success else 1)
