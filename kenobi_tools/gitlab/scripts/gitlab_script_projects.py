#!/usr/bin/env python3
"""
Script principal pour l'extraction des projets GitLab
Nomenclature Kenobi : gitlab_script_projects.py
"""

import sys
from pathlib import Path

# Ajout du chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from kenobi_tools.gitlab.extractors.gitlab_extract_projects import extract_projects
from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
from kenobi_tools.gitlab.client.gitlab_client import GitLabClient
import pandas as pd


def main():
    """Script principal d'extraction des projets GitLab"""
    print("🦊 GitLab Projects Extraction - Kenobi Tools")
    print("=" * 50)
    
    try:
        # Connexion GitLab
        client = GitLabClient()
        gl_client = client.connect()
        
        # Extraction des projets
        df_projects = extract_projects(gl_client)
        
        print(f"✅ {len(df_projects)} projets extraits")
        
        # Export Excel
        exporter = GitLabExcelExporter()
        output_file = exporter.export_projects(df_projects)
        
        print(f"📊 Export terminé : {output_file}")
        
        # Déconnexion
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
