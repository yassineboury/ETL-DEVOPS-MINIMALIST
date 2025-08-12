#!/usr/bin/env python3
"""
🔍 Analyser les types d'actions dans l'extraction
"""

import pandas as pd

def analyze_actions():
    """Analyse les types d'actions dans le fichier Excel"""
    
    try:
        df = pd.read_excel('exports/gitlab/gitlab_events_simple.xlsx')
        
        print("=== TYPES D'ACTIONS ===")
        print(df['nom_action'].value_counts().head(10))
        
        print("\n=== ÉVÉNEMENTS PUSH ===")
        push_events = df[df['nom_action'].str.contains('push', case=False, na=False)]
        print(f"Nombre d'événements push: {len(push_events)}")
        
        if len(push_events) > 0:
            print("\nExemples d'événements push:")
            print(push_events[['nom_action', 'action_push', 'nom_branche']].head(3))
        else:
            print("❌ Aucun événement push trouvé!")
            
        print(f"\n=== RÉSUMÉ ===")
        print(f"Total événements: {len(df)}")
        print(f"Événements push: {len(push_events)}")
        print(f"Événements MR: {len(df[df['type_cible'] == 'MergeRequest'])}")
        print(f"Autres types: {len(df[(df['type_cible'] != 'MergeRequest') & (~df['nom_action'].str.contains('push', case=False, na=False))])}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    analyze_actions()
