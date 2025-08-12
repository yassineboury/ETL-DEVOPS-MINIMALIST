#!/usr/bin/env python3
"""
🎯 MAESTRO KENOBI - ETL DevSecOps Orchestrator
Le maître orchestrateur pour les exports GitLab et DevSecOps
Gère les exports selon un processus clair et par étapes avec style !
"""

import contextlib
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

# Ajouter les dossiers au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.exporters.excel_exporter import (
    export_projects_to_excel,
    export_users_to_excel,
    export_groups_to_excel,
)
from gitlab_tools.extractors.projects_extractor import extract_projects
from gitlab_tools.extractors.users_extractor import extract_human_users
from gitlab_tools.extractors.groups_extractor import GroupsExtractor


class MaestroKenobiOrchestrator:
    """
    🎭 MAESTRO KENOBI - Le maître orchestrateur GitLab
    Gère les exports GitLab avec élégance et puissance
    """

    # Messages constants
    NO_GITLAB_CONNECTION = "❌ Pas de connexion GitLab active"

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.exports_dir = self.project_root / "exports" / "gitlab"
        self.gitlab_client = None
        self.gl = None

        # Configuration de la barre de progression
        self.total_steps = 7  # Ajout de l'étape groupes
        self.current_step = 0
        self.main_progress = None

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
            self.gitlab_client = create_gitlab_client()

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

            # Créer l'extracteur de groupes
            groups_extractor = GroupsExtractor(self.gl)
            
            # Extraire les groupes
            groups_df = groups_extractor.extract()

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

            # Extraire tous les projets (actifs + archivés)
            projects_df = extract_projects(self.gl, include_archived=True)

            if projects_df.empty:
                print("❌ Aucun projet trouvé")
                return False, 0

            project_count = len(projects_df)
            print(f"✅ {project_count} projets extraits")

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
                users_file = export_users_to_excel(
                    self.users_data,
                    filename="gitlab_users.xlsx"
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
            print("=" * 60)
            print(f"👥 Utilisateurs extraits: {users_count}")
            print(f"📁 Projets extraits: {projects_count}")
            print(f"📊 Fichiers Excel créés: {len(created_files)}")

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
        print("🚀 KENOBI DEVOPS - ORCHESTRATEUR D'EXPORT GITLAB")
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
    """🚀 Point d'entrée principal - MAESTRO KENOBI en action !"""
    print("🎭 MAESTRO KENOBI - Orchestrateur DevSecOps")
    print("=" * 50)

    orchestrator = MaestroKenobiOrchestrator()

    # Lancer l'export complet
    success = orchestrator.run_full_export()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
