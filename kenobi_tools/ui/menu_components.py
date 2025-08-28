"""
Composants de menu pour l'interface utilisateur Kenobi
Sépare la logique de présentation de l'orchestration principale
"""
from datetime import datetime, timedelta
from typing import Any, Dict


class MenuComponents:
    """Gestionnaire des composants d'interface utilisateur"""

    # Messages constants
    INVALID_CHOICE_MESSAGE = "❌ Répondez par 'o' (oui) ou 'n' (non)"

    # Configuration des périodes d'événements
    EVENT_PERIODS = {
        "1": {
            "name": "30 derniers jours",
            "duration": "2-5 minutes",
            "after_date": lambda: (datetime.now() - timedelta(days=30))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .isoformat() + "Z",
            "before_date": None
        },
        "2": {
            "name": "3 derniers mois",
            "duration": "5-10 minutes",
            "after_date": lambda: (datetime.now() - timedelta(days=90))
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .isoformat() + "Z",
            "before_date": None
        },
        "3": {
            "name": f"Année {datetime.now().year}",
            "duration": "10-15 minutes",
            "after_date": lambda: f"{datetime.now().year}-01-01T00:00:00Z",
            "before_date": None
        },
        "4": {
            "name": "Tous les événements",
            "duration": "15-30 minutes",
            "after_date": None,
            "before_date": None
        }
    }

    @staticmethod
    def show_welcome_banner():
        """Bannière d'accueil moderne sans bordures"""
        print("\n\n")
        print("           🎭 MAESTRO KENOBI")
        print("        GitLab DevSecOps Engine")
        print("")
        print(f"    🕒 {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}  ⚡ v2.0  🎯 Ready")
        print("    " + "─" * 45)
        print("\n\n")

    @staticmethod
    def show_main_menu() -> bool:
        """Menu principal simplifié - extraction complète directe"""
        print("           🚀 EXTRACTION GITLAB COMPLÈTE")
        print("    " + "─" * 40)
        print("\n")

        print("    � DONNÉES EXTRAITES AUTOMATIQUEMENT:")
        print("       ├─ 👥 Utilisateurs GitLab (~30s)")
        print("       ├─ 🏢 Groupes et sous-groupes (~20s)")
        print("       ├─ 📁 Projets actifs + archivés (~45s)")
        print("       └─ � Événements avec période configurable")
        print("\n")
        
        print("    ⏱️  Durée estimée: 5-20 minutes")
        print("    � Export: Fichiers Excel Power BI ready")
        print("\n")
        print("    " + "─" * 43)
        print("")

        return MenuComponents._get_yes_no_choice("🚀 Lancer l'extraction complète ? (o/n) ► ")

    @staticmethod
    def show_events_period_menu() -> Dict[str, Any] | None:
        """Menu de choix de période simplifié"""
        print("\n")
        print("       📅 PÉRIODE DES ÉVÉNEMENTS GITLAB")
        print("    " + "─" * 35)
        print("")
        print("    1️⃣ Les 30 derniers jours")
        print("    2️⃣ Les 3 derniers mois")
        print("    3️⃣ Année " + str(datetime.now().year))
        print("    4️⃣ Tous les événements disponibles")
        print("")
        print("    " + "─" * 43)
        print("")

        choice = MenuComponents._get_menu_choice(
            list(MenuComponents.EVENT_PERIODS.keys()),
            "🎯 Votre choix de période (1-4) ► "
        )

        if choice in MenuComponents.EVENT_PERIODS:
            config = MenuComponents.EVENT_PERIODS[choice]
            after_date = config["after_date"]() if config["after_date"] else None
            print(f"\n    ✅ Période sélectionnée: {config['name']}")
            return {
                "name": config["name"],
                "after_date": after_date,
                "before_date": config["before_date"]
            }
        return None

    @staticmethod
    def _get_menu_choice(valid_choices: list, prompt: str) -> str:
        """Helper pour obtenir un choix valide dans une liste"""
        while True:
            choice = input(f"\n    {prompt}").strip()
            if choice in valid_choices:
                return choice
            print(f"    ❌ Choix invalide, veuillez saisir {' ou '.join(valid_choices)}")

    @staticmethod
    def _get_yes_no_choice(prompt: str) -> bool:
        """Helper pour obtenir une confirmation oui/non"""
        while True:
            choice = input(f"\n{prompt}").strip().lower()
            if choice in ["o", "oui", "y", "yes"]:
                return True
            elif choice in ["n", "non", "no"]:
                return False
            else:
                print(MenuComponents.INVALID_CHOICE_MESSAGE)
