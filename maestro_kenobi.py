#!/usr/bin/env python3
"""
🎭 KENOBI MAESTRO - Orchestrateur GitLab Symphonique REFACTORISÉ
Version simplifiée pour réduire la complexité cognitive
Délègue les responsabilités aux modules spécialisés
"""

import contextlib
import sys
import time
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv

# Ajouter les dossiers au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kenobi_tools.gitlab.client.gitlab_client import GitLabClient
from kenobi_tools.ui.menu_components import MenuComponents
from kenobi_tools.processing.extraction_processor import ExtractionProcessor


class MaestroKenobiOrchestrator:
    """
    🎭 MAESTRO KENOBI - Orchestrateur GitLab Simplifié
    Version refactorisée avec séparation des responsabilités
    """

    # Messages constants
    NO_GITLAB_CONNECTION = "❌ Pas de connexion GitLab active"

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.exports_dir = self.project_root / "exports" / "gitlab"
        self.gitlab_client = None
        self.gl = None
        self.menu = MenuComponents()
        self.processor = ExtractionProcessor()

    def run_intelligent_extraction(self) -> bool:
        """Point d'entrée principal avec interface simplifiée"""
        self.menu.show_welcome_banner()

        # Menu principal simplifié - retourne bool directement
        proceed = self.menu.show_main_menu()

        if proceed:
            return self._execute_full_extraction()
        else:
            print("    ❌ Extraction annulée")
            return False

    def _execute_full_extraction(self) -> bool:
        """Exécute l'extraction complète avec choix de période pour les événements"""
        # Étape 1: Configuration des événements
        print("\n    📋 Configuration des événements")
        events_config = self.menu.show_events_period_menu()

        # Étape 2: Validation et lancement direct
        if not events_config:
            print("    ❌ Configuration des événements échouée")
            return False

        print(f"\n    ✅ Configuration terminée: {events_config['name']}")
        
        # Étape 3: Exécution directe
        if not self._setup_gitlab_connection():
            return False

        success = True
        
        # Phase 1: Données de base
        print("\n🚀 Début de l'extraction complète...")
        success = self.processor.process_all_data(self.exports_dir)

        # Phase 2: Événements 
        if events_config and success:
            success &= self.processor.process_events_extraction(events_config)

        return self._finalize_extraction(success)

    def _setup_gitlab_connection(self) -> bool:
        """Configure la connexion GitLab"""
        try:
            print("\n🔐 Connexion à GitLab...")
            self.gitlab_client = GitLabClient()
            self.gl = self.gitlab_client.connect()
            
            if self.gl:
                print("✅ Connexion GitLab établie")
                return True
            else:
                print(self.NO_GITLAB_CONNECTION)
                return False
                
        except Exception as e:
            print(f"❌ Erreur de connexion GitLab: {e}")
            return False

    def _finalize_extraction(self, success: bool) -> bool:
        """Finalise l'extraction et affiche le résumé"""
        if success:
            print("\n" + "=" * 60)
            print("🎭 MAESTRO KENOBI - EXTRACTION TERMINÉE AVEC SUCCÈS !")
            print("=" * 60)
            print("\n✅ Toutes les données ont été extraites et exportées")
            print(f"📁 Fichiers disponibles dans: {self.exports_dir}")
            print("\n🎯 Prêt pour import dans Power BI !")
            return True
        else:
            print("\n❌ Extraction échouée - Vérifiez les logs ci-dessus")
            return False

def main():
    """Fonction principale"""
    # Charger les variables d'environnement
    load_dotenv()
    
    # Créer et lancer l'orchestrateur
    orchestrator = MaestroKenobiOrchestrator()
    
    try:
        success = orchestrator.run_intelligent_extraction()
        if success:
            print("\n✨ Mission accomplie avec succès !")
        else:
            print("\n❌ Mission échouée")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Extraction interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
