#!/usr/bin/env python3
"""
🔍 Script de debug pour examiner la structure d'un projet GitLab
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le projet au path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client


def debug_project_structure():
    """
    Examine la structure d'un projet GitLab pour comprendre les données disponibles
    """
    print("🔍 DEBUG: Examen structure projet GitLab")
    print("=" * 50)
    
    try:
        # 1. Connexion
        load_dotenv()
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        if not gl:
            print("❌ Connexion échouée")
            return
            
        print("✅ Connexion établie")
        
        # 2. Récupérer le premier projet
        projects = gl.projects.list(per_page=1)
        
        if not projects:
            print("❌ Aucun projet trouvé")
            return
            
        project = projects[0]
        print(f"📁 Projet d'exemple: {getattr(project, 'name', 'N/A')}")
        print()
        
        # 3. Examiner les attributs disponibles
        print("🔍 ATTRIBUTS DISPONIBLES:")
        print("-" * 30)
        
        attrs_to_check = [
            'id', 'name', 'path', 'path_with_namespace',
            'namespace', 'owner', 'creator_id', 
            'web_url', 'default_branch'
        ]
        
        for attr in attrs_to_check:
            value = getattr(project, attr, "ATTRIBUTE_NOT_FOUND")
            print(f"{attr:20}: {value}")
            
            # Si c'est un objet complexe, examiner sa structure
            if hasattr(value, '__dict__') and attr in ['namespace', 'owner']:
                print(f"  └─ Structure de {attr}:")
                if hasattr(value, '__dict__'):
                    for key, val in value.__dict__.items():
                        print(f"     {key}: {val}")
                elif isinstance(value, dict):
                    for key, val in value.items():
                        print(f"     {key}: {val}")
                        
        print()
        
        # 4. Tester la récupération des langages
        print("🔍 TEST LANGAGES:")
        print("-" * 20)
        try:
            languages = project.languages()
            print(f"Langages: {languages}")
        except Exception as e:
            print(f"Erreur langages: {e}")
            
        gitlab_client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    debug_project_structure()
