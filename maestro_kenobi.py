#!/usr/bin/env python3
"""
<<<<<<<< HEAD:kenobi_maestro.py
KENOBI MAESTRO - Orchestrateur d'export GitLab KENOBI DEVOPS
Chef d'orchestre pour gérer les exports GitLab selon un processus clair et par étapes
========
🎯 MAESTRO KENOBI - ETL DevSecOps Orchestrator
Le maître orchestrateur pour les exports GitLab et DevSecOps
Gère les exports selon un processus clair et par étapes avec style !
>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
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
)
from gitlab_tools.extractors.projects_extractor import extract_projects
from gitlab_tools.extractors.users_extractor import extract_human_users


<<<<<<<< HEAD:kenobi_maestro.py
class KenobiMaestro:
    """
    KENOBI MAESTRO - Chef d'orchestre pour gérer les exports GitLab de manière structurée
    Dirige les 6 mouvements de l'export avec précision et élégance
========
class MaestroKenobiOrchestrator:
    """
    🎭 MAESTRO KENOBI - Le maître orchestrateur GitLab
    Gère les exports GitLab avec élégance et puissance
>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.exports_dir = self.project_root / "exports" / "gitlab"
        self.gitlab_client = None
        self.gl = None

        # Configuration de la barre de progression
        self.total_steps = 6
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
<<<<<<<< HEAD:kenobi_maestro.py
        🎼 PREMIER MOUVEMENT: Nettoyage de la scène avant le spectacle
        
========
        Étape 1: Supprimer les anciens fichiers du dossier exports/gitlab

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
        Returns:
            bool: True si succès, False sinon
        """
        print("🧹 PREMIER MOUVEMENT: Nettoyage de la scène")
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
<<<<<<<< HEAD:kenobi_maestro.py
        🎼 DEUXIÈME MOUVEMENT: Accordage avec GitLab ONCF
        
========
        Étape 2: Connexion à GitLab ONCF

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
        Returns:
            bool: True si succès, False sinon
        """
        print("\n🔗 DEUXIÈME MOUVEMENT: Accordage avec GitLab ONCF")
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
<<<<<<<< HEAD:kenobi_maestro.py
        🎼 TROISIÈME MOUVEMENT: Mélodie des utilisateurs GitLab
        
========
        Étape 3: Extraction des utilisateurs GitLab

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
        Returns:
            tuple: (succès, nombre d'utilisateurs)
        """
        print("\n👥 TROISIÈME MOUVEMENT: Mélodie des utilisateurs GitLab")
        print("-" * 50)

        try:
            if not self.gl:
                print("❌ Pas de connexion GitLab active")
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

    def step_4_extract_projects(self) -> tuple[bool, int]:
        """
<<<<<<<< HEAD:kenobi_maestro.py
        🎼 QUATRIÈME MOUVEMENT: Symphonie des projets GitLab
        
========
        Étape 4: Extraction des projets GitLab

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
        Returns:
            tuple: (succès, nombre de projets)
        """
        print("\n📁 QUATRIÈME MOUVEMENT: Symphonie des projets GitLab")
        print("-" * 50)

        try:
            if not self.gl:
                print("❌ Pas de connexion GitLab active")
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

    def step_5_export_to_excel(self) -> tuple[bool, list]:
        """
<<<<<<<< HEAD:kenobi_maestro.py
        🎼 CINQUIÈME MOUVEMENT: Composition des partitions Excel
        
========
        Étape 5: Export vers Excel

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
        Returns:
            tuple: (succès, liste des fichiers créés)
        """
        print("\n📊 CINQUIÈME MOUVEMENT: Composition des partitions Excel")
        print("-" * 50)

        try:
            if not hasattr(self, 'users_data') or not hasattr(self, 'projects_data'):
                print("❌ Données manquantes pour l'export")
                return False, []

            created_files = []

            # Barre de progression pour l'export
            export_tasks = ["utilisateurs", "projets"]
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

    def step_6_cleanup_and_summary(
        self, users_count: int, projects_count: int, created_files: list
    ) -> bool:
        """
<<<<<<<< HEAD:kenobi_maestro.py
        🎼 SIXIÈME MOUVEMENT: Final en apothéose et saluts
        
========
        Étape 6: Nettoyage final et résumé

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
        Args:
            users_count: Nombre d'utilisateurs extraits
            projects_count: Nombre de projets extraits
            created_files: Liste des fichiers créés

        Returns:
            bool: True si succès
        """
        print("\n🧹 SIXIÈME MOUVEMENT: Final en apothéose et saluts")
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

            print("🗑️  Données temporaires nettoyées")

            # Résumé final
            print("\n" + "=" * 60)
            print("🎉 SYMPHONIE GITLAB TERMINÉE AVEC BRIO!")
            print("=" * 60)
            print(f"👥 Utilisateurs extraits: {users_count}")
            print(f"📁 Projets extraits: {projects_count}")
<<<<<<<< HEAD:kenobi_maestro.py
            print(f"📊 Partitions Excel créées: {len(created_files)}")
            
========
            print(f"📊 Fichiers Excel créés: {len(created_files)}")

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
            if created_files:
                print("\n🎼 Œuvres créées:")
                for file_path in created_files:
                    file_size = Path(file_path).stat().st_size / 1024  # KB
                    print(f"   ✅ {Path(file_path).name} ({file_size:.1f} KB)")
<<<<<<<< HEAD:kenobi_maestro.py
                
                print(f"\n📂 Conservatoire: {self.exports_dir}")
            
            print(f"\n🎭 Rideau tombé le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
            
            self._update_progress("🎉 Symphonie terminée")
========

                print(f"\n📂 Dossier: {self.exports_dir}")

            print(f"\n⏰ Export terminé le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")

            self._update_progress("Nettoyage et résumé terminés")
>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
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
        print("🎭 KENOBI MAESTRO - CHEF D'ORCHESTRE GITLAB")
        print("=" * 60)
        print(f"🎼 Début de la symphonie le: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
        print("=" * 60)

        # Initialiser la barre de progression principale
<<<<<<<< HEAD:kenobi_maestro.py
        with tqdm(total=self.total_steps, desc="🎼 Mouvements symphoniques", unit="mouvement", 
                 bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} mouvements [{elapsed}<{remaining}]") as progress:
            
========
        with tqdm(
            total=self.total_steps,
            desc="🔄 Étapes d'export",
            unit="étape",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} étapes [{elapsed}<{remaining}]"
        ) as progress:

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
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

                # Étape 4: Extraction projets
                projects_success, projects_count = self.step_4_extract_projects()
                if not projects_success:
                    return False

                # Étape 5: Export Excel
                export_success, created_files = self.step_5_export_to_excel()
                if not export_success:
                    return False

                # Étape 6: Nettoyage et résumé
                if not self.step_6_cleanup_and_summary(users_count, projects_count, created_files):
                    return False

                # Finaliser la barre de progression
                progress.set_description("� Symphonie terminée")
                progress.refresh()

                return True

            except Exception as e:
                print(f"\n❌ DISSONANCE CRITIQUE: {e}")
                progress.set_description("❌ Fausse note critique")
                # Nettoyage d'urgence
                if self.gitlab_client:
                    with contextlib.suppress(Exception):
                        self.gitlab_client.disconnect()
                return False
            finally:
                self.main_progress = None


def main():
<<<<<<<< HEAD:kenobi_maestro.py
    """Point d'entrée principal - Le chef prend sa baguette"""
    maestro = KenobiMaestro()
    
    # Lancer la symphonie complète
    success = maestro.run_full_export()
    
========
    """🚀 Point d'entrée principal - MAESTRO KENOBI en action !"""
    print("🎭 MAESTRO KENOBI - Orchestrateur DevSecOps")
    print("=" * 50)

    orchestrator = MaestroKenobiOrchestrator()

    # Lancer l'export complet
    success = orchestrator.run_full_export()

>>>>>>>> 94bf882fd747fe58626033a054dc30991534a683:maestro_kenobi.py
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
