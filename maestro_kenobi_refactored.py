#!/usr/bin/env python3
"""
🎭 KENOBI MAESTRO - Orchestrateur GitLab Symphonique REFACTORISÉ
Le maître chef d'orchestre pour les exports GitLab et DevSecOps
Architecture modulaire pour réduire la complexité cognitive
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ajouter le dossier au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kenobi_tools.orchestrators.export_orchestrator import KenobiExportOrchestrator
from kenobi_tools.ui.kenobi_menu import KenobiMenuInterface


class MaestroKenobiOrchestrator:
    """
    🎭 MAESTRO KENOBI - Orchestrateur GitLab refactorisé
    Architecture modulaire pour réduire la complexité cognitive
    """
    
    def __init__(self):
        """Initialise le maestro avec ses composants"""
        load_dotenv()
        self.menu = KenobiMenuInterface()
        self.orchestrator = KenobiExportOrchestrator()
        self.is_connected = False
    
    def run(self):
        """Point d'entrée principal du programme"""
        try:
            if not self._setup_connection():
                return
            
            self._main_loop()
            
        except KeyboardInterrupt:
            self.menu.display_info_message("Interruption par l'utilisateur")
        except Exception as e:
            self.menu.display_error_message(f"Erreur inattendue: {e}")
        finally:
            self._cleanup()
    
    def _setup_connection(self) -> bool:
        """Configure la connexion GitLab"""
        self.menu.display_processing_header("🔌 CONNEXION GITLAB")
        
        if not self.orchestrator.setup_gitlab_connection():
            self.menu.display_error_message("Impossible de se connecter à GitLab")
            self.menu.display_info_message("Vérifiez votre fichier .env et la connectivité")
            return False
        
        self.is_connected = True
        self.menu.display_success_message("Connexion GitLab établie avec succès!")
        return True
    
    def _main_loop(self):
        """Boucle principale du menu"""
        while True:
            self.menu.display_main_menu()
            
            choice = self.menu.get_user_choice(
                "🎯 Votre choix: ", 
                ['0', '1', '2', '3', '4', '5', '6', '7']
            )
            
            if choice == '0':
                self.menu.display_goodbye_message()
                break
            
            self._handle_menu_choice(choice)
    
    def _handle_menu_choice(self, choice: str):
        """Traite le choix utilisateur"""
        choice_handlers = {
            '1': self._handle_users_export,
            '2': self._handle_groups_export,
            '3': self._handle_events_export,
            '4': self._handle_merge_requests_export,
            '5': self._handle_active_projects_export,
            '6': self._handle_archived_projects_export,
            '7': self._handle_complete_export
        }
        
        handler = choice_handlers.get(choice)
        if handler:
            handler()
        else:
            self.menu.display_error_message("Choix non implémenté")
    
    def _handle_users_export(self):
        """Traite l'export des utilisateurs"""
        self.menu.display_processing_header("👥 EXPORT UTILISATEURS")
        
        if self.orchestrator.extract_and_export_users():
            self.menu.display_success_message("Export utilisateurs terminé avec succès!")
        else:
            self.menu.display_error_message("Échec de l'export des utilisateurs")
    
    def _handle_groups_export(self):
        """Traite l'export des groupes"""
        self.menu.display_processing_header("👥 EXPORT GROUPES")
        
        if self.orchestrator.extract_and_export_groups():
            self.menu.display_success_message("Export groupes terminé avec succès!")
        else:
            self.menu.display_error_message("Échec de l'export des groupes")
    
    def _handle_events_export(self):
        """Traite l'export des événements"""
        self.menu.display_processing_header("📊 EXPORT ÉVÉNEMENTS")
        
        days, period_label = self.menu.get_period_selection()
        
        if self.orchestrator.extract_and_export_events(days, period_label):
            self.menu.display_success_message("Export événements terminé avec succès!")
        else:
            self.menu.display_error_message("Échec de l'export des événements")
    
    def _handle_merge_requests_export(self):
        """Traite l'export des merge requests"""
        self.menu.display_processing_header("🔄 EXPORT MERGE REQUESTS")
        self.menu.display_warning_message("Fonctionnalité non encore implémentée")
    
    def _handle_active_projects_export(self):
        """Traite l'export des projets actifs"""
        self.menu.display_processing_header("📦 EXPORT PROJETS ACTIFS")
        
        if self.orchestrator.extract_and_export_active_projects():
            self.menu.display_success_message("Export projets actifs terminé avec succès!")
        else:
            self.menu.display_error_message("Échec de l'export des projets actifs")
    
    def _handle_archived_projects_export(self):
        """Traite l'export des projets archivés"""
        self.menu.display_processing_header("📦 EXPORT PROJETS ARCHIVÉS")
        
        if self.orchestrator.extract_and_export_archived_projects():
            self.menu.display_success_message("Export projets archivés terminé avec succès!")
        else:
            self.menu.display_error_message("Échec de l'export des projets archivés")
    
    def _handle_complete_export(self):
        """Traite l'export complet"""
        self.menu.display_processing_header("🎭 EXPORT COMPLET")
        
        if not self.menu.confirm_export_complete():
            self.menu.display_info_message("Export complet annulé")
            return
        
        if self.orchestrator.perform_complete_export():
            self.menu.display_completion_message()
        else:
            self.menu.display_error_message("Échec de l'export complet")
    
    def _cleanup(self):
        """Nettoyage final"""
        if self.is_connected:
            self.orchestrator.close_gitlab_connection()
            self.menu.display_info_message("Connexion GitLab fermée")


def main():
    """Point d'entrée du programme"""
    maestro = MaestroKenobiOrchestrator()
    maestro.run()


if __name__ == "__main__":
    main()
