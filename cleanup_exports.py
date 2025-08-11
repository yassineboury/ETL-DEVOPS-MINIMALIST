#!/usr/bin/env python3
"""
KENOBI MAESTRO - Nettoyage de la scène
Exécute seulement le premier mouvement (nettoyage) du Maestro
"""

import sys
from pathlib import Path

# Importer le maestro
from kenobi_maestro import KenobiMaestro


def main():
    """Nettoyage simple de la scène avant spectacle"""
    print("🎭 KENOBI MAESTRO - NETTOYAGE DE LA SCÈNE")
    print("=" * 50)
    
    maestro = KenobiMaestro()
    success = maestro.step_1_cleanup_old_files()
    
    if success:
        print("\n✅ Scène prête pour le spectacle!")
        return True
    else:
        print("\n❌ Problème de préparation de scène!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
