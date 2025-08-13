#!/usr/bin/env python3
"""
Script principal pour l'extraction des groupes GitLab
Nomenclature Kenobi : gitlab_script_groups.py
"""

import sys
from pathlib import Path

# Ajout du chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from kenobi_tools.gitlab.extractors.gitlab_extract_groups import extract_groups
from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
from kenobi_tools.gitlab.client.gitlab_client import GitLabClient


def main():
    """Script principal d'extraction des groupes GitLab"""
    print("🦊 GitLab Groups Extraction - Kenobi Tools")
    print("=" * 50)
    
    try:
        # Connexion GitLab
        client = GitLabClient()
        gl_client = client.connect()
        
        # Extraction des groupes
        df_groups = extract_groups(gl_client)
        
        print(f"✅ {len(df_groups)} groupes extraits")
        
        # Export Excel
        exporter = GitLabExcelExporter()
        output_file = exporter.export_groups(df_groups)
        
        print(f"📊 Export terminé : {output_file}")
        
        # Déconnexion
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
