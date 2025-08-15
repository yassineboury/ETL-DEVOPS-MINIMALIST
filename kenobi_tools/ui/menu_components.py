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
    def show_main_menu() -> str:
        """Menu principal fluide sans bordures"""
        print("           MODES D'EXTRACTION")
        print("    " + "─" * 35)
        print("\n")

        print("    🚀 MODE COMPLET                    [Recommandé]")
        print("       ├─ 👥 Utilisateurs & Groupes")
        print("       ├─ 📁 Projets (actifs + archivés)")
        print("       ├─ 📊 Événements avec période configurable")
        print("       └─ ⏱️  Durée: 5-20 minutes")
        print("\n")

        print("    ⚙️  MODE PERSONNALISÉ                  [Avancé]")
        print("       ├─ 🎛️  Sélection modulaire des données")
        print("       ├─ 🔧 Contrôle fin des extracteurs")
        print("       └─ ⏱️  Durée: Variable selon sélection")
        print("\n")
        print("    " + "─" * 43)
        print("")

        return MenuComponents._get_menu_choice(["1", "2"], "🎯 Votre choix (1 ou 2) ► ")

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
    def show_custom_menu() -> Dict[str, Any]:
        """Menu personnalisé fluide sans bordures"""
        print("\n")
        print("            MODE PERSONNALISÉ")
        print("    " + "─" * 30)
        print("\n")
        print("    📊 DONNÉES DE BASE (obligatoires)")
        print("       • 👥 Utilisateurs GitLab (~30s)")
        print("       • 🏢 Groupes et sous-groupes (~20s)")
        print("       • 📁 Projets actifs + archivés (~45s)")
        print("\n")
        print("    📈 DONNÉES D'ACTIVITÉ (optionnelles)")
        print("       • 🔄 Événements GitLab (2-30min)")
        print("         Push, merge, issues, commentaires...")
        print("\n")

        # Choix avec confirmation visuelle
        print("    🎯 Configuration:")
        print("       ✅ Données de base: Incluses automatiquement")
        print("")

        events_choice = MenuComponents._get_yes_no_choice(
            "📈 Inclure les événements ? (o/n) ► "
        )

        config = {
            "include_base": True,
            "include_events": events_choice,
            "events_config": None
        }

        if config["include_events"]:
            print("  ✅ Événements: Activés")
            config["events_config"] = MenuComponents.show_events_period_menu()
        else:
            print("  ❌ Événements: Désactivés")

        return config

    @staticmethod
    def show_complete_mode_steps(events_config: Dict[str, Any] | None) -> bool:
        """Affichage des étapes du mode complet avec confirmation"""
        print("\n\n")
        print("        🚀 MODE COMPLET SÉLECTIONNÉ")
        print("    " + "─" * 35)
        print("")

        # Étape 2: Affichage du récapitulatif
        print("\n    📋 Récapitulatif de configuration")
        print("        ✅ Configuration choisie")
        print("    " + "─" * 30)
        print("")
        print("      📊 Données: Base + Activité")
        print("         • 👥 Utilisateurs")
        print("         • 🏢 Groupes")
        print("         • 📁 Projets (actifs + archivés)")
        if events_config:
            print(f"         • 📅 Événements: {events_config['name']}")
        else:
            print("         • 📅 Événements: Non configuré")
        print("\n")

        # Étape 3: Confirmation et lancement
        print("    📋 Confirmation")
        print("")
        
        return MenuComponents._get_yes_no_choice("🚀 Lancer l'extraction ? (o/n) ► ")

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
