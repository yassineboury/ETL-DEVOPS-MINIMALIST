#!/usr/bin/env python3
"""
🧪 TEST - Analyser la structure des événements GitLab
"""

import sys
from pathlib import Path

# Ajouter le projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client

def test_event_structure():
    """Analyse la structure d'un événement GitLab réel"""
    
    try:
        print("🔗 Connexion à GitLab...")
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()
        
        if not gl:
            print("❌ Impossible de se connecter")
            return
            
        print("✅ Connecté")
        
        # Prendre le premier projet avec des événements
        projects = gl.projects.list(all=False, per_page=5)
        
        for project in projects:
            try:
                events = project.events.list(per_page=1)
                if events:
                    event = events[0]
                    print(f"\n📊 Événement du projet '{project.name}':")
                    print(f"🔍 Type d'objet: {type(event)}")
                    print(f"📋 Attributs disponibles:")
                    
                    # Afficher tous les attributs de l'événement
                    for attr in dir(event):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(event, attr)
                                if not callable(value):
                                    print(f"   {attr}: {value}")
                            except:
                                print(f"   {attr}: <error>")
                    
                    # Test des attributs spécifiques
                    print(f"\n🎯 Tests d'attributs spécifiques:")
                    print(f"   event.id: {getattr(event, 'id', 'NONE')}")
                    print(f"   event.project_id: {getattr(event, 'project_id', 'NONE')}")
                    print(f"   event.action_name: {getattr(event, 'action_name', 'NONE')}")
                    print(f"   event.created_at: {getattr(event, 'created_at', 'NONE')}")
                    
                    break
            except Exception as e:
                print(f"⚠️ Erreur projet {project.name}: {e}")
                continue
                
        gitlab_client.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_event_structure()
