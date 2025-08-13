#!/usr/bin/env python3
"""
Script principal pour l'extraction des utilisateurs GitLab
Nomenclature Kenobi : gitlab_script_users.py
"""

import sys
from pathlib import Path

# Ajout du chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from kenobi_tools.gitlab.extractors.gitlab_extract_users import extract_human_users
from kenobi_tools.gitlab.exporters.gitlab_export_excel import GitLabExcelExporter
from kenobi_tools.gitlab.client.gitlab_client import GitLabClient
import pandas as pd


def main():
    """Script principal d'extraction des utilisateurs GitLab"""
    print("🦊 GitLab Users Extraction - Kenobi Tools")
    print("=" * 50)
    
    try:
        # Connexion GitLab
        client = GitLabClient()
        gl_client = client.connect()
        
        # Extraction des utilisateurs humains
        users_data = extract_human_users(gl_client)
        
        print(f"✅ {len(users_data)} utilisateurs extraits")
        
        # Conversion en DataFrame
        df_users = pd.DataFrame(users_data)
        
        # Export Excel
        exporter = GitLabExcelExporter()
        output_file = exporter.export_users(df_users)
        
        print(f"📊 Export terminé : {output_file}")
        
        # Déconnexion
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
