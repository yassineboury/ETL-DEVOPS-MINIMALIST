#!/usr/bin/env python3
"""
Exemple d'utilisation du traitement par batch pour GitLab
Démontre l'avantage pour 200 projets
"""

import os
import sys
from pathlib import Path

# Ajouter le path du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.commits_extractor import CommitsExtractor
from gitlab_tools.utils.batch_processor import GitLabBatchProcessor


def demo_without_batch(gitlab_client, project_ids):
    """❌ Approche sans batch - problématique pour 200 projets"""
    print("❌ SANS BATCH - Traitement séquentiel de tous les projets:")
    print("-" * 60)
    
    extractor = CommitsExtractor(gitlab_client)
    
    # Simulation: tous les projets d'un coup
    try:
        df = extractor.extract_commits(project_ids)
        print(f"✅ Résultat: {len(df)} commits extraits")
    except Exception as e:
        print(f"💥 ÉCHEC: {e}")
        print("👆 Typique avec 200 projets: timeout, mémoire, tout est perdu!")


def demo_with_batch(gitlab_client, project_ids):
    """✅ Approche avec batch - optimale pour 200 projets"""
    print("\n✅ AVEC BATCH - Traitement intelligent par lots:")
    print("-" * 60)
    
    # Créer le processeur batch
    batch_processor = GitLabBatchProcessor(batch_size=10)
    extractor = CommitsExtractor(gitlab_client)
    
    def extract_batch(batch_project_ids):
        """Fonction qui traite un batch de projets"""
        return extractor.extract_commits(batch_project_ids)
    
    # Traitement avec batch
    try:
        df = batch_processor.process_projects_batch(
            project_ids=project_ids,
            extractor_func=extract_batch
        )
        print(f"✅ Résultat: {len(df)} commits extraits")
        print("📊 Avantages observés:")
        print("   • Mémoire contrôlée: max 10 projets simultanés")
        print("   • Récupération: échec d'un batch ≠ échec total")
        print("   • Progress tracking: visibilité en temps réel")
        print("   • Fichiers temp: sauvegarde intermédiaire")
        
    except Exception as e:
        print(f"⚠️  Erreur partielle: {e}")
        print("👆 Avec batch: on récupère les projets réussis!")


def main():
    """Démonstration des avantages du batch processing"""
    
    print("🚀 DÉMONSTRATION: Batch Processing pour GitLab")
    print("=" * 80)
    print("Contexte: 200 projets, extractions hebdomadaires")
    print("Librairie: python-gitlab")
    print()
    
    # Simulation avec quelques projets
    fake_project_ids = list(range(1, 21))  # Simule 20 projets
    
    print(f"📋 Test avec {len(fake_project_ids)} projets (simulation de 200)")
    
    try:
        # Connexion GitLab (optionnelle pour demo)
        if os.getenv('GITLAB_TOKEN'):
            gitlab_client = create_gitlab_client()
            demo_without_batch(gitlab_client, fake_project_ids[:5])  # Petit test
            demo_with_batch(gitlab_client, fake_project_ids)
        else:
            print("💡 Pour test réel: configurez GITLAB_TOKEN dans .env")
            print("\n🎯 AVANTAGES THÉORIQUES DU BATCH PROCESSING:")
            print("-" * 50)
            print("📈 PERFORMANCE:")
            print("   • Sans batch: 200 projets × 1000 commits = 200k objets RAM")  
            print("   • Avec batch: 10 projets × 1000 commits = 10k objets RAM max")
            print()
            print("🛡️  RÉSILIENCE:")
            print("   • Sans batch: échec projet 150 → perte de 4h de travail")
            print("   • Avec batch: échec batch 15 → perte de 10 projets seulement")
            print()
            print("⚡ EXPÉRIENCE UTILISATEUR:")
            print("   • Sans batch: attente silencieuse de 2h")
            print("   • Avec batch: progress bar temps réel, ETA précis")
            print()
            print("🔄 API GITLAB:")
            print("   • Sans batch: requêtes longues qui timeout")
            print("   • Avec batch: requêtes courtes, retry possible")
            
    except Exception as e:
        print(f"Erreur: {e}")
    
    print("\n" + "=" * 80)
    print("💡 CONCLUSION: Batch processing = INDISPENSABLE pour 200 projets!")
    

if __name__ == "__main__":
    main()
