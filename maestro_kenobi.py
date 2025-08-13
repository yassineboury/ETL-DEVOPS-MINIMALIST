#!/usr/bin/env python3
"""
� KENOBI MAESTRO - Orchestrateur GitLab Symphonique
Le maître chef d'orchestre pour les exports GitLab et DevSecOps
Dirige les mouvements d'extraction avec précision musicale et élégance !
"""

import contextlib
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv
from tqdm import tqdm

# Ajouter les dossiers au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kenobi_tools.gitlab.client.gitlab_client import GitLabClient
from kenobi_tools.gitlab.exporters.gitlab_export_excel import (
    GitLabExcelExporter,
    export_projects_to_excel,
    export_groups_to_excel,
)
from kenobi_tools.gitlab.extractors.gitlab_extract_active_projects import extract_active_projects
from kenobi_tools.gitlab.extractors.gitlab_extract_archived_projects import extract_archived_projects
from kenobi_tools.gitlab.extractors.gitlab_extract_users import extract_human_users
from kenobi_tools.gitlab.extractors.gitlab_extract_groups import extract_groups
from kenobi_tools.gitlab.extractors.gitlab_extract_events import extract_events_by_project


class MaestroKenobiOrchestrator:
    """
    🎭 MAESTRO KENOBI - Orchestrateur GitLab Intelligent
    Menu interactif avec choix modulaires et gestion fine des extracteurs
    """

    # Messages constants
    NO_GITLAB_CONNECTION = "❌ Pas de connexion GitLab active"
    
    # Configuration des périodes d'événements
    EVENT_PERIODS = {
        "1": {
            "name": "30 derniers jours",
            "duration": "2-5 minutes",
            "after_date": lambda: (datetime.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z",
            "before_date": None
        },
        "2": {
            "name": "3 derniers mois",
            "duration": "5-10 minutes", 
            "after_date": lambda: (datetime.now() - timedelta(days=90)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z",
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

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.exports_dir = self.project_root / "exports" / "gitlab"
        self.gitlab_client = None
        self.gl = None
        self.extracted_data = {}
        self.created_files = []
        
        # Configuration de progression
        self.total_steps = 4  # Utilisateurs, Groupes, Projets, Événements
        self.current_step = 0
        self.main_progress = None

    def show_welcome_banner(self):
        """Bannière d'accueil vraiment minimaliste"""
        print("\n" + "=" * 50)
        print("          MAESTRO KENOBI")
        print("          DevSecOps KPIs")
        print("=" * 50)
        print(f"🕒 {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
        print("⚡ Orchestrateur intelligent")
        print("🎯 GitLab Data Extraction")
        print("=" * 50)

    def show_main_menu(self) -> str:
        """Menu principal vraiment minimaliste"""
        print("\n\n\n" + "=" * 50)
        print("         CHOIX D'EXTRACTION")
        print("=" * 50)
        
        print("1️⃣  MODE COMPLET")
        print("   → Utilisateurs + Groupes + Projets")
        print("   → Evenements avec choix periode")
        print("   → Export Excel optimise")
        print("   → Duree: 5-20 min selon periode")
        
        print("\n2️⃣  MODE PERSONNALISE")
        print("   → Selection modulaire par famille")
        print("   → Controle fin des extracteurs")
        print("   → Options avancees")
        print("   → Duree: Variable selon selection")
        
        print("=" * 50)
        
        while True:
            choice = input("🎯 Votre choix (1 ou 2): ").strip()
        
        while True:
            choice = input("\n🎯 Votre choix (1 ou 2) ► ").strip()
            if choice in ["1", "2"]:
                return choice
            print("❌ Choix invalide, veuillez saisir 1 ou 2")

    def show_events_period_menu(self) -> Optional[Dict[str, Any]]:
        """Menu de choix de période avec design cohérent"""
        print("\n")
        print("┌" + "─" * 55 + "┐")
        print("│" + "       PÉRIODE DES ÉVÉNEMENTS GITLAB".center(55) + "│")
        print("├" + "─" * 55 + "┤")
        print("│                                                     │")
        print("│  📅 1. 30 derniers jours                           │")
        print("│     • Durée estimée: 2-5 minutes                   │")
        print("│     • Volume: Moyen                                │")
        print("│                                                     │")
        print("│  📅 2. 3 derniers mois                             │")
        print("│     • Durée estimée: 5-10 minutes                  │")
        print("│     • Volume: Important                            │")
        print("│                                                     │")
        print("│  📅 3. Année " + str(datetime.now().year) + "                                  │")
        print("│     • Durée estimée: 10-15 minutes                 │")
        print("│     • Volume: Très important                       │")
        print("│                                                     │")
        print("│  📅 4. Tous les événements                         │")
        print("│     • Durée estimée: 15-30 minutes                 │")
        print("│     • Volume: Maximum                              │")
        print("│                                                     │")
        print("└" + "─" * 55 + "┘")
        
        while True:
            choice = input("\n🎯 Votre choix de période (1-4) ► ").strip()
            if choice in self.EVENT_PERIODS:
                config = self.EVENT_PERIODS[choice]
                after_date = config["after_date"]() if config["after_date"] else None
                print(f"\n✅ Période sélectionnée: {config['name']}")
                return {
                    "name": config["name"],
                    "after_date": after_date,
                    "before_date": config["before_date"]
                }
            print("❌ Choix invalide, veuillez saisir 1, 2, 3 ou 4")

    def show_custom_menu(self) -> Dict[str, Any]:
        """Menu personnalisé avec interface élégante"""
        print("\n")
        print("┌" + "─" * 55 + "┐")
        print("│" + "            MODE PERSONNALISÉ".center(55) + "│")
        print("├" + "─" * 55 + "┤")
        print("│                                                     │")
        print("│  📊 DONNÉES DE BASE (obligatoires)                 │")
        print("│     • 👥 Utilisateurs GitLab (~30s)                │")
        print("│     • 🏢 Groupes et sous-groupes (~20s)            │")
        print("│     • 📁 Projets actifs + archivés (~45s)          │")
        print("│                                                     │")
        print("│  📈 DONNÉES D'ACTIVITÉ (optionnelles)              │")
        print("│     • 🔄 Événements GitLab (2-30min)               │")
        print("│       Push, merge, issues, commentaires...         │")
        print("│                                                     │")
        print("└" + "─" * 55 + "┘")
        
        # Choix avec confirmation visuelle
        print("\n🎯 Configuration:")
        print("  ✅ Données de base: Incluses automatiquement")
        
        while True:
            events_choice = input("\n📈 Inclure les événements ? (o/n) ► ").strip().lower()
            if events_choice in ["o", "oui", "y", "yes", "n", "non", "no"]:
                break
            print("❌ Répondez par 'o' (oui) ou 'n' (non)")
        
        config = {
            "include_base": True,
            "include_events": events_choice in ["o", "oui", "y", "yes"],
            "events_config": None
        }
        
        if config["include_events"]:
            print("  ✅ Événements: Activés")
            config["events_config"] = self.show_events_period_menu()
        else:
            print("  ❌ Événements: Désactivés")
            
        return config

    def run_intelligent_extraction(self) -> bool:
        """Point d'entrée principal avec menu intelligent"""
        self.show_welcome_banner()
        
        # Menu principal
        mode = self.show_main_menu()
        
        if mode == "1":
            return self.run_complete_mode()
        else:
            return self.run_custom_mode()
    
    def run_complete_mode(self) -> bool:
        """Mode complet avec affichage élégant des étapes"""
        print("\n")
        print("┌" + "─" * 50 + "┐")
        print("│" + "🚀 MODE COMPLET SÉLECTIONNÉ".center(50) + "│")
        print("└" + "─" * 50 + "┘")
        
        # Étape 1: Choix de période pour les événements
        print("\n📋 Étape 1/3: Configuration")
        events_config = self.show_events_period_menu()
        
        # Étape 2: Affichage du récapitulatif
        print("\n📋 Étape 2/3: Récapitulatif")
        print("┌" + "─" * 45 + "┐")
        print("│" + "✅ Configuration choisie".center(45) + "│")
        print("├" + "─" * 45 + "┤")
        print("│                                             │")
        print("│  📊 Données: Base + Activité               │")
        print("│     • 👥 Utilisateurs                       │")
        print("│     • 🏢 Groupes                            │")
        print("│     • 📁 Projets (actifs + archivés)       │")
        print(f"│     • 📅 Événements: {events_config['name']:<18} │")
        print("│                                             │")
        print("└" + "─" * 45 + "┘")
        
        # Étape 3: Confirmation et lancement
        print("\n📋 Étape 3/3: Confirmation")
        while True:
            confirm = input("🚀 Lancer l'extraction ? (o/n) ► ").strip().lower()
            if confirm in ["o", "oui", "y", "yes"]:
                break
            elif confirm in ["n", "non", "no"]:
                print("❌ Extraction annulée")
                return False
            else:
                print("❌ Répondez par 'o' (oui) ou 'n' (non)")
        
        # Lancer l'extraction complète
        return self.execute_full_extraction(events_config)
    
    def run_custom_mode(self) -> bool:
        """Mode personnalisé avec étapes guidées"""
        print("\n")
        print("┌" + "─" * 55 + "┐")
        print("│" + "⚙️ MODE PERSONNALISÉ SÉLECTIONNÉ".center(55) + "│")
        print("└" + "─" * 55 + "┘")
        
        # Étape 1: Configuration personnalisée
        print("\n📋 Étape 1/3: Configuration personnalisée")
        config = self.show_custom_menu()
        
        # Étape 2: Récapitulatif détaillé
        print("\n📋 Étape 2/3: Récapitulatif de votre sélection")
        print("┌" + "─" * 50 + "┐")
        print("│" + "✅ Configuration personnalisée".center(50) + "│")
        print("├" + "─" * 50 + "┤")
        print("│                                                  │")
        print("│  📊 Données de base: ✅ Incluses                │")
        print("│     • 👥 Utilisateurs                            │")
        print("│     • 🏢 Groupes                                 │")
        print("│     • 📁 Projets                                 │")
        print("│                                                  │")
        if config["include_events"]:
            print("│  � Événements: ✅ Inclus                       │")
            print(f"│     • 📅 Période: {config['events_config']['name']:<23} │")
        else:
            print("│  � Événements: ❌ Exclus                       │")
        print("│                                                  │")
        print("└" + "─" * 50 + "┘")
        
        # Étape 3: Confirmation
        print("\n📋 Étape 3/3: Confirmation finale")
        while True:
            confirm = input("🚀 Lancer l'extraction personnalisée ? (o/n) ► ").strip().lower()
            if confirm in ["o", "oui", "y", "yes"]:
                break
            elif confirm in ["n", "non", "no"]:
                print("❌ Extraction annulée")
                return False
            else:
                print("❌ Répondez par 'o' (oui) ou 'n' (non)")
        
        return self.execute_custom_extraction(config)
    
    def execute_full_extraction(self, events_config: Dict[str, Any]) -> bool:
        """Exécute l'extraction complète avec affichage élégant"""
        print("\n")
        print("🚀" + "═" * 56 + "🚀")
        print("║" + "          DÉMARRAGE EXTRACTION COMPLÈTE          ".center(56) + "║")
        print("🚀" + "═" * 56 + "🚀")
        
        try:
            # Étape 1/4: Connexion GitLab
            print(f"\n⏳ Étape 1/4: Connexion GitLab...")
            if not self._setup_gitlab_connection():
                return False
            print("✅ Connexion établie avec succès")
                
            # Étape 2/4: Extraction des données de base
            print(f"\n⏳ Étape 2/4: Extraction données de base...")
            if not self._extract_base_data():
                return False
            print("✅ Données de base extraites")
                
            # Étape 3/4: Extraction des événements
            print(f"\n⏳ Étape 3/4: Extraction événements ({events_config['name']})...")
            if not self._extract_events_with_config(events_config):
                return False
            print("✅ Événements extraits")
                
            # Étape 4/4: Export Excel
            print(f"\n⏳ Étape 4/4: Export Excel...")
            if not self._export_to_excel():
                return False
            print("✅ Export Excel terminé")
            
            # Succès final
            print("\n")
            print("🎉" + "═" * 56 + "🎉")
            print("║" + "          EXTRACTION COMPLÈTE RÉUSSIE!          ".center(56) + "║")
            print("🎉" + "═" * 56 + "🎉")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")
            print("🚨" + "═" * 56 + "🚨")
            return False
    
    def execute_custom_extraction(self, config: Dict[str, Any]) -> bool:
        """Exécute l'extraction personnalisée avec affichage élégant"""
        print("\n")
        print("⚙️" + "═" * 56 + "⚙️")
        print("║" + "        DÉMARRAGE EXTRACTION PERSONNALISÉE       ".center(56) + "║")
        print("⚙️" + "═" * 56 + "⚙️")
        
        total_steps = 3 if config["include_events"] else 2
        
        try:
            # Étape 1: Connexion GitLab
            print(f"\n⏳ Étape 1/{total_steps}: Connexion GitLab...")
            if not self._setup_gitlab_connection():
                return False
            print("✅ Connexion établie avec succès")
                
            # Étape 2: Extraction des données de base
            print(f"\n⏳ Étape 2/{total_steps}: Extraction données de base...")
            if not self._extract_base_data():
                return False
            print("✅ Données de base extraites")
                
            # Étape 3 conditionnelle: Extraction des événements
            if config["include_events"]:
                print(f"\n⏳ Étape 3/{total_steps}: Extraction événements ({config['events_config']['name']})...")
                if not self._extract_events_with_config(config["events_config"]):
                    return False
                print("✅ Événements extraits")
            
            # Étape finale: Export Excel
            step_final = total_steps + 1
            print(f"\n⏳ Étape {step_final}/{step_final}: Export Excel...")
            if not self._export_to_excel():
                return False
            print("✅ Export Excel terminé")
            
            # Succès final
            print("\n")
            print("🎉" + "═" * 56 + "🎉")
            print("║" + "       EXTRACTION PERSONNALISÉE RÉUSSIE!        ".center(56) + "║")
            print("🎉" + "═" * 56 + "🎉")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")
            print("🚨" + "═" * 56 + "🚨")
            return False
    
    def _setup_gitlab_connection(self) -> bool:
        """Configure la connexion GitLab avec affichage élégant"""
        print("   🔗 Initialisation connexion GitLab...")
        
        try:
            self.gitlab_client = GitLabClient()
            self.gl = self.gitlab_client.get_client()
            
            if not self.gl:
                print("   ❌ Échec de connexion GitLab")
                return False
                
            print("   ✅ Client GitLab initialisé")
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def _extract_base_data(self) -> bool:
        """Extrait les données de base avec progression visuelle"""
        try:
            # Extraction utilisateurs
            print("   👥 Extraction utilisateurs...")
            users_df = extract_human_users(self.gl)
            self.extracted_data["users"] = users_df
            print(f"      ✅ {len(users_df)} utilisateurs")
            
            # Extraction groupes
            print("   🏢 Extraction groupes...")
            groups_df = extract_groups(self.gl)
            self.extracted_data["groups"] = groups_df
            print(f"      ✅ {len(groups_df)} groupes")
            
            # Extraction projets actifs
            print("   📁 Extraction projets actifs...")
            active_projects_df = extract_active_projects(self.gl)
            print(f"      ✅ {len(active_projects_df)} projets actifs")
            
            # Extraction projets archivés
            print("   📁 Extraction projets archivés...")
            archived_projects_df = extract_archived_projects(self.gl)
            print(f"      ✅ {len(archived_projects_df)} projets archivés")
            
            # Combiner les projets
            import pandas as pd
            all_projects_df = pd.concat([active_projects_df, archived_projects_df], ignore_index=True)
            self.extracted_data["projects"] = all_projects_df
            print(f"      📊 Total: {len(all_projects_df)} projets combinés")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def _extract_events_with_config(self, events_config: Dict[str, Any]) -> bool:
        """Extrait les événements avec affichage de progression"""
        try:
            after_date = events_config.get("after_date")
            before_date = events_config.get("before_date")
            
            print(f"   🔍 Période: {events_config['name']}")
            if after_date:
                print(f"   📅 Depuis: {after_date[:10]}")
            
            print("   📊 Extraction en cours...")
            events_df = extract_events_by_project(
                self.gl,
                after_date=after_date,
                before_date=before_date
            )
            
            self.extracted_data["events"] = events_df
            print(f"      ✅ {len(events_df)} événements extraits")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def _export_to_excel(self) -> bool:
        """Exporte vers Excel avec progression détaillée"""
        try:
            # Créer le répertoire d'export
            self.exports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            print("   📄 Génération fichiers Excel...")
            
            # Export des données disponibles
            if "users" in self.extracted_data:
                users_file = self.exports_dir / f"gitlab_users_{timestamp}.xlsx"
                self.extracted_data["users"].to_excel(users_file, index=False)
                print(f"      ✅ {users_file.name}")
                self.created_files.append(users_file)
            
            if "groups" in self.extracted_data:
                groups_file = self.exports_dir / f"gitlab_groups_{timestamp}.xlsx"
                self.extracted_data["groups"].to_excel(groups_file, index=False)
                print(f"      ✅ {groups_file.name}")
                self.created_files.append(groups_file)
            
            if "projects" in self.extracted_data:
                projects_file = self.exports_dir / f"gitlab_projects_{timestamp}.xlsx"
                self.extracted_data["projects"].to_excel(projects_file, index=False)
                print(f"      ✅ {projects_file.name}")
                self.created_files.append(projects_file)
            
            if "events" in self.extracted_data:
                events_file = self.exports_dir / f"gitlab_events_{timestamp}.xlsx"
                self.extracted_data["events"].to_excel(events_file, index=False)
                print(f"      ✅ {events_file.name}")
                self.created_files.append(events_file)
            
            print(f"   📂 Répertoire: {self.exports_dir}")
            print(f"   🎯 {len(self.created_files)} fichier(s) généré(s)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False

    def _update_progress(self, description: str):
        """
        Met à jour la barre de progression principale

        Args:
            description: Description de l'étape en cours
        """
        if self.main_progress:
            self.main_progress.set_description(f"📊 {description}")
            self.main_progress.update(1)
            time.sleep(0.1)  # Petit délai pour voir la progression

    def step_1_cleanup_old_files(self) -> bool:
        """
        Étape 1: Supprimer les anciens fichiers du dossier exports/gitlab

        Returns:
            bool: True si succès, False sinon
        """
        print("🧹 ÉTAPE 1: Nettoyage des anciens fichiers d'export")
        print("-" * 50)

        try:
            if not self.exports_dir.exists():
                print("📁 Le dossier exports/gitlab n'existe pas encore")
                self._update_progress("Nettoyage terminé (aucun fichier)")
                return True

            # Lister les fichiers existants
            existing_files = list(self.exports_dir.glob("*.xlsx"))

            if not existing_files:
                print("✅ Aucun ancien fichier à supprimer")
                self._update_progress("Nettoyage terminé (aucun fichier)")
                return True

            print(f"📋 {len(existing_files)} fichier(s) trouvé(s):")
            for file in existing_files:
                print(f"   • {file.name}")

            # Supprimer les fichiers avec barre de progression
            deleted_count = 0
            with tqdm(
                total=len(existing_files),
                desc="🗑️  Suppression",
                unit="fichier",
                leave=False
            ) as pbar:
                for file in existing_files:
                    try:
                        file.unlink()
                        print(f"   ✅ Supprimé: {file.name}")
                        deleted_count += 1
                        pbar.update(1)
                        time.sleep(0.1)  # Simulation du temps de suppression
                    except Exception as e:
                        print(f"   ❌ Erreur suppression {file.name}: {e}")
                        pbar.update(1)

            print(f"🗑️  {deleted_count} fichier(s) supprimé(s)")
            print("✅ Étape 1 terminée avec succès")
            self._update_progress(f"Nettoyage terminé ({deleted_count} fichiers)")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du nettoyage: {e}")
            self._update_progress("Erreur nettoyage")
            return False

    def step_2_connect_gitlab(self) -> bool:
        """
        Étape 2: Connexion à GitLab ONCF

        Returns:
            bool: True si succès, False sinon
        """
        print("\n🔗 ÉTAPE 2: Connexion à GitLab ONCF")
        print("-" * 50)

        try:
            # Charger les variables d'environnement
            load_dotenv()

            # Créer le client GitLab
            print("🔑 Création du client GitLab...")
            self.gitlab_client = GitLabClient()

            # Se connecter
            print("🌐 Connexion à GitLab ONCF...")
            self.gl = self.gitlab_client.connect()

            if not self.gl:
                print("❌ Impossible de se connecter à GitLab")
                return False

            print("✅ Connexion GitLab établie avec succès")
            self._update_progress("Connexion GitLab établie")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {e}")
            self._update_progress("Erreur connexion GitLab")
            return False

    def step_3_extract_users(self) -> tuple[bool, int]:
        """
        Étape 3: Extraction des utilisateurs GitLab

        Returns:
            tuple: (succès, nombre d'utilisateurs)
        """
        print("\n👥 ÉTAPE 3: Extraction des utilisateurs GitLab")
        print("-" * 50)

        try:
            if not self.gl:
                print(self.NO_GITLAB_CONNECTION)
                return False, 0

            # Extraire les utilisateurs humains
            users_df = extract_human_users(self.gl, include_blocked=True)

            if users_df.empty:
                print("❌ Aucun utilisateur trouvé")
                return False, 0

            user_count = len(users_df)
            print(f"✅ {user_count} utilisateurs humains extraits")

            # Statistiques rapides
            if 'etat' in users_df.columns:
                states = users_df['etat'].value_counts()
                print(f"📊 États: {states.to_dict()}")

            # Sauvegarder temporairement
            self.users_data = users_df
            self._update_progress(f"Extraction utilisateurs ({user_count})")
            return True, user_count

        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des utilisateurs: {e}")
            self._update_progress("Erreur extraction utilisateurs")
            return False, 0

    def step_4_extract_groups(self) -> tuple[bool, int]:
        """
        Étape 4: Extraction des groupes GitLab

        Returns:
            tuple: (succès, nombre de groupes)
        """
        print("\n👥 ÉTAPE 4: Extraction des groupes GitLab")
        print("-" * 50)

        try:
            if not self.gl:
                print(self.NO_GITLAB_CONNECTION)
                return False, 0

            # Extraire les groupes directement
            groups_df = extract_groups(self.gl)

            if groups_df.empty:
                print("❌ Aucun groupe trouvé")
                return False, 0

            groups_count = len(groups_df)
            print(f"✅ {groups_count} groupes extraits")

            # Statistiques rapides
            if 'is_top_level' in groups_df.columns:
                top_level_count = groups_df['is_top_level'].sum()
                sub_groups_count = groups_count - top_level_count
                print(f"📊 Groupes racine: {top_level_count}, Sous-groupes: {sub_groups_count}")

            if 'total_members' in groups_df.columns:
                total_members = groups_df['total_members'].sum()
                print(f"👥 Total membres: {total_members}")

            # Sauvegarder temporairement
            self.groups_data = groups_df
            self._update_progress(f"Extraction groupes ({groups_count})")
            return True, groups_count

        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des groupes: {e}")
            self._update_progress("Erreur extraction groupes")
            return False, 0

    def step_5_extract_projects(self) -> tuple[bool, int]:
        """
        Étape 5: Extraction des projets GitLab

        Returns:
            tuple: (succès, nombre de projets)
        """
        print("\n📁 ÉTAPE 5: Extraction des projets GitLab")
        print("-" * 50)

        try:
            if not self.gl:
                print(self.NO_GITLAB_CONNECTION)
                return False, 0

            # Extraire les projets actifs
            active_projects_df = extract_active_projects(self.gl)
            print(f"✅ {len(active_projects_df)} projets actifs extraits")
            
            # Extraire les projets archivés
            archived_projects_df = extract_archived_projects(self.gl)
            print(f"✅ {len(archived_projects_df)} projets archivés extraits")
            
            # Combiner les deux DataFrames
            import pandas as pd
            projects_df = pd.concat([active_projects_df, archived_projects_df], ignore_index=True)

            if projects_df.empty:
                print("❌ Aucun projet trouvé")
                return False, 0

            project_count = len(projects_df)
            print(f"📊 Total: {project_count} projets extraits")

            # Statistiques rapides
            if 'etat' in projects_df.columns:
                states = projects_df['etat'].value_counts()
                print(f"📊 États: {states.to_dict()}")

            if 'archivé' in projects_df.columns:
                archived = projects_df['archivé'].value_counts()
                print(f"📦 Archivage: {archived.to_dict()}")

            # Sauvegarder temporairement
            self.projects_data = projects_df
            self._update_progress(f"Extraction projets ({project_count})")
            return True, project_count

        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des projets: {e}")
            self._update_progress("Erreur extraction projets")
            return False, 0

    def step_6_export_to_excel(self) -> tuple[bool, list]:
        """
        Étape 6: Export des données vers Excel

        Returns:
            tuple: (succès, liste des fichiers créés)
        """
        print("\n📊 ÉTAPE 6: Export vers fichiers Excel")
        print("-" * 50)

        try:
            required_data = ['users_data', 'projects_data', 'groups_data']
            missing_data = [data for data in required_data if not hasattr(self, data)]
            
            if missing_data:
                print(f"❌ Données manquantes pour l'export: {', '.join(missing_data)}")
                return False, []

            created_files = []

            # Barre de progression pour l'export
            export_tasks = ["utilisateurs", "groupes", "projets"]
            with tqdm(
                total=len(export_tasks),
                desc="📁 Export Excel",
                unit="fichier",
                leave=False
            ) as pbar:

                # Export des utilisateurs
                print("👥 Export des utilisateurs...")
                pbar.set_description("📁 Export utilisateurs")
                exporter = GitLabExcelExporter()
                users_file = exporter.export_users(
                    self.users_data,
                    filename="gitlab_users_filtered.xlsx"
                )
                if users_file:
                    created_files.append(users_file)
                    print(f"   ✅ Utilisateurs: {Path(users_file).name}")
                pbar.update(1)

                # Export des groupes  
                print("👥 Export des groupes...")
                pbar.set_description("📁 Export groupes")
                groups_file = export_groups_to_excel(
                    self.groups_data,
                    filename="gitlab_groups.xlsx"
                )
                if groups_file:
                    created_files.append(groups_file)
                    print(f"   ✅ Groupes: {Path(groups_file).name}")
                pbar.update(1)
                time.sleep(0.2)

                # Export des projets
                print("📁 Export des projets...")
                pbar.set_description("📁 Export projets")
                projects_file = export_projects_to_excel(
                    self.projects_data,
                    filename="gitlab_projects.xlsx"
                )
                if projects_file:
                    created_files.append(projects_file)
                    print(f"   ✅ Projets: {Path(projects_file).name}")
                pbar.update(1)
                time.sleep(0.2)

            if created_files:
                print(f"✅ {len(created_files)} fichier(s) Excel créé(s)")
                self._update_progress(f"Export Excel ({len(created_files)} fichiers)")
                return True, created_files
            else:
                print("❌ Aucun fichier créé")
                self._update_progress("Erreur export Excel")
                return False, []

        except Exception as e:
            print(f"❌ Erreur lors de l'export Excel: {e}")
            self._update_progress("Erreur export Excel")
            return False, []

    def step_7_cleanup_and_summary(
        self, users_count: int, projects_count: int, groups_count: int, created_files: list
    ) -> bool:
        """
        Étape 7: Nettoyage final et résumé

        Args:
            users_count: Nombre d'utilisateurs extraits
            projects_count: Nombre de projets extraits  
            groups_count: Nombre de groupes extraits
            created_files: Liste des fichiers créés

        Returns:
            bool: True si succès
        """
        print("\n🧹 ÉTAPE 7: Nettoyage final et résumé")
        print("-" * 50)

        try:
            # Fermer la connexion GitLab
            if self.gitlab_client:
                self.gitlab_client.disconnect()
                print("🔌 Connexion GitLab fermée")

            # Nettoyer les données temporaires
            if hasattr(self, 'users_data'):
                delattr(self, 'users_data')
            if hasattr(self, 'projects_data'):
                delattr(self, 'projects_data')
            if hasattr(self, 'groups_data'):
                delattr(self, 'groups_data')

            print("🗑️  Données temporaires nettoyées")

            # Résumé final
            print("\n" + "=" * 60)
            print("🎉 EXPORT GITLAB TERMINÉ AVEC SUCCÈS!")
            print("=" * 60)
            print(f"👥 Utilisateurs extraits: {users_count}")
            print(f"👥 Groupes extraits: {groups_count}")
            print(f"📁 Projets extraits: {projects_count}")
            print(f"� Fichiers Excel créés: {len(created_files)}")
            print("=" * 60)

            if created_files:
                print("\n📁 Fichiers générés:")
                for file_path in created_files:
                    file_size = Path(file_path).stat().st_size / 1024  # KB
                    print(f"   ✅ {Path(file_path).name} ({file_size:.1f} KB)")

                print(f"\n📂 Dossier: {self.exports_dir}")

            print(f"\n⏰ Export terminé le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")

            self._update_progress("Nettoyage et résumé terminés")
            return True

        except Exception as e:
            print(f"❌ Erreur lors du nettoyage: {e}")
            self._update_progress("Erreur nettoyage final")
            return False

    def run_full_export(self) -> bool:
        """
        Lance l'export complet en suivant toutes les étapes

        Returns:
            bool: True si tout s'est bien passé
        """
        print("🚀 MAESTRO KENOBI - DevSecOps ETL")
        print("=" * 60)
        print(f"📅 Démarrage le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
        print("=" * 60)

        # Initialiser la barre de progression principale
        with tqdm(
            total=self.total_steps,
            desc="🔄 Étapes d'export",
            unit="étape",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} étapes [{elapsed}<{remaining}]"
        ) as progress:

            self.main_progress = progress

            try:
                # Étape 1: Nettoyage
                if not self.step_1_cleanup_old_files():
                    return False

                # Étape 2: Connexion
                if not self.step_2_connect_gitlab():
                    return False

                # Étape 3: Extraction utilisateurs
                users_success, users_count = self.step_3_extract_users()
                if not users_success:
                    return False

                # Étape 4: Extraction groupes
                groups_success, groups_count = self.step_4_extract_groups()
                if not groups_success:
                    return False

                # Étape 5: Extraction projets
                projects_success, projects_count = self.step_5_extract_projects()
                if not projects_success:
                    return False

                # Étape 6: Export Excel
                export_success, created_files = self.step_6_export_to_excel()
                if not export_success:
                    return False

                # Étape 7: Nettoyage et résumé
                if not self.step_7_cleanup_and_summary(users_count, projects_count, groups_count, created_files):
                    return False

                # Finaliser la barre de progression
                progress.set_description("🎉 Export terminé")
                progress.refresh()

                return True

            except Exception as e:
                print(f"\n❌ ERREUR CRITIQUE: {e}")
                progress.set_description("❌ Erreur critique")
                # Nettoyage d'urgence
                if self.gitlab_client:
                    with contextlib.suppress(Exception):
                        self.gitlab_client.disconnect()
                return False
            finally:
                self.main_progress = None


def main():
    """🚀 Point d'entrée principal - MAESTRO KENOBI Intelligent !"""
    orchestrator = MaestroKenobiOrchestrator()
    
    # Lancer l'extraction avec menu intelligent
    success = orchestrator.run_intelligent_extraction()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
