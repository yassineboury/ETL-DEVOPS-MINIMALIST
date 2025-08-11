#!/usr/bin/env python3
"""
Script pour nettoyer uniquement les anciens fichiers d'export GitLab
Exécute seulement l'étape 1 de l'orchestrateur
"""

import sys
from pathlib import Path

# Importer l'orchestrateur
from orchestrator import GitLabExportOrchestrator


def main():
    """Nettoyage simple des anciens fichiers"""
    print("🧹 NETTOYAGE DES ANCIENS FICHIERS GITLAB")
    print("=" * 50)
    
    orchestrator = GitLabExportOrchestrator()
    success = orchestrator.step_1_cleanup_old_files()
    
    if success:
        print("\n✅ Nettoyage terminé avec succès!")
        return True
    else:
        print("\n❌ Erreur lors du nettoyage!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
