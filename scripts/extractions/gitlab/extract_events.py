#!/usr/bin/env python3
"""
📅 EXTRACTION EVENTS GITLAB SEULEMENT
Script simple pour extraire uniquement les events GitLab vers Excel
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le projet au path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.events_extractor import extract_events
from gitlab_tools.exporters.excel_exporter import export_events_to_excel


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


def extract_events_to_excel(days_back=None):
    """
    Extraction simple des events GitLab vers Excel
    
    Args:
        days_back: Nombre de jours en arrière pour filtrer les événements (None = toutes les dates)
    """
    print("📅 EXTRACTION EVENTS GITLAB")
    print("=" * 40)
    
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
        
        # Statistiques rapides
        if 'type_action' in events_df.columns:
            action_types = events_df['type_action'].value_counts()
            print(f"📊 Types d'actions: {dict(list(action_types.items())[:5])}{'...' if len(action_types) > 5 else ''}")
            
        if 'type_cible' in events_df.columns:
            target_types = events_df['type_cible'].value_counts()
            print(f"🎯 Types de cibles: {dict(list(target_types.items())[:5])}{'...' if len(target_types) > 5 else ''}")
            
        # 4. Export vers Excel
        print("📊 Export vers Excel...")
        excel_file = export_events_to_excel(events_df, filename="gitlab_events.xlsx")
        
        if excel_file:
            file_size = Path(excel_file).stat().st_size / 1024  # KB
            print(f"✅ Fichier créé: {Path(excel_file).name} ({file_size:.1f} KB)")
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
    import sys
    
    print("🚀 Lancement de l'extraction events...")
    
    # Menu interactif pour choisir la période
    days_back = choose_period()
    
    # Lancer l'extraction avec la période choisie
    success = extract_events_to_excel(days_back)
    
    if success:
        if days_back is not None:
            print(f"\n🎉 Extraction terminée avec succès! (événements des {days_back} derniers jours)")
        else:
            print("\n🎉 Extraction terminée avec succès! (tous les événements)")
    else:
        print("\n❌ Extraction échouée")
    
    sys.exit(0 if success else 1)
