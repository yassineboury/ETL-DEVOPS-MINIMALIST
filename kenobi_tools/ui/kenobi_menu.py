"""
Menu Kenobi - Interface utilisateur interactive
Module séparé pour l'interface et les menus utilisateur
"""
from typing import Dict, List, Tuple


class KenobiMenuInterface:
    """Interface utilisateur pour le Maestro Kenobi"""
    
    # Messages constants
    NO_GITLAB_CONNECTION = "❌ Pas de connexion GitLab active"
    INVALID_CHOICE_MESSAGE = "❌ Répondez par 'o' (oui) ou 'n' (non)"
    
    # Configuration des périodes d'événements
    EVENT_PERIODS = {
        "1": {"days": 7, "label": "7 derniers jours"},
        "2": {"days": 30, "label": "30 derniers jours"},
        "3": {"days": 90, "label": "3 derniers mois"},
        "4": {"days": 365, "label": "1 dernière année"},
        "5": {"days": None, "label": "Tous les événements (attention: peut être très long)"}
    }
    
    def display_main_menu(self):
        """Affiche le menu principal"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      🎭 MAESTRO KENOBI - ORCHESTRATEUR GITLAB              ║
║                           Votre chef d'orchestre GitLab !                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎪 FONCTIONNALITÉS DISPONIBLES :                                          ║
║                                                                              ║
║  👥 [1] Utilisateurs GitLab     📦 [5] Projets Actifs                     ║
║  👥 [2] Groupes GitLab          📦 [6] Projets Archivés                   ║
║  📊 [3] Événements GitLab       🎭 [7] Export Complet                     ║
║  🔄 [4] Merge Requests          ❌ [0] Quitter                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
    
    def display_period_selection(self):
        """Affiche le menu de sélection des périodes pour les événements"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      📅 SÉLECTION PÉRIODE - ÉVÉNEMENTS                     ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
        
        for key, period in self.EVENT_PERIODS.items():
            print(f"  [{key}] {period['label']}")
        print()
    
    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """
        Demande un choix à l'utilisateur
        
        Args:
            prompt: Message à afficher
            valid_choices: Liste des choix valides
            
        Returns:
            Choix de l'utilisateur
        """
        while True:
            choice = input(prompt).strip().lower()
            if choice in valid_choices:
                return choice
            print(f"❌ Choix invalide. Options valides: {', '.join(valid_choices)}")
    
    def get_yes_no_choice(self, prompt: str) -> bool:
        """
        Demande une réponse oui/non à l'utilisateur
        
        Args:
            prompt: Question à poser
            
        Returns:
            True pour oui, False pour non
        """
        while True:
            response = input(f"{prompt} (o/n): ").strip().lower()
            if response in ['o', 'oui', 'y', 'yes']:
                return True
            elif response in ['n', 'non', 'no']:
                return False
            else:
                print(self.INVALID_CHOICE_MESSAGE)
    
    def get_period_selection(self) -> Tuple[int, str]:
        """
        Gère la sélection de période pour les événements
        
        Returns:
            Tuple (nombre_de_jours, label_période)
        """
        self.display_period_selection()
        
        valid_periods = list(self.EVENT_PERIODS.keys())
        choice = self.get_user_choice("Choisissez une période: ", valid_periods)
        
        selected_period = self.EVENT_PERIODS[choice]
        return selected_period["days"], selected_period["label"]
    
    def display_processing_header(self, title: str):
        """Affiche un en-tête de traitement"""
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  {title:<76} ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
    
    def display_success_message(self, message: str):
        """Affiche un message de succès"""
        print(f"✅ {message}")
    
    def display_error_message(self, message: str):
        """Affiche un message d'erreur"""
        print(f"❌ {message}")
    
    def display_info_message(self, message: str):
        """Affiche un message d'information"""
        print(f"ℹ️  {message}")
    
    def display_warning_message(self, message: str):
        """Affiche un message d'avertissement"""
        print(f"⚠️  {message}")
    
    def confirm_export_complete(self) -> bool:
        """Demande confirmation pour l'export complet"""
        print("""
⚠️  ATTENTION: L'export complet va extraire TOUTES les données:
   - Utilisateurs, Groupes, Projets actifs/archivés
   - Événements des 30 derniers jours
   - Merge Requests
   
   Cela peut prendre plusieurs minutes selon la taille de votre GitLab.
""")
        return self.get_yes_no_choice("Confirmer l'export complet ?")
    
    def display_completion_message(self):
        """Affiche le message de fin"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🎉 MAESTRO KENOBI TERMINÉ !                       ║
║                     Tous vos fichiers sont prêts ! 🚀                      ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
    
    def display_goodbye_message(self):
        """Affiche le message d'au revoir"""
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         👋 AU REVOIR ET MERCI !                            ║
║              Que la Force GitLab soit avec vous ! ⭐                       ║
╚══════════════════════════════════════════════════════════════════════════════╝""")
