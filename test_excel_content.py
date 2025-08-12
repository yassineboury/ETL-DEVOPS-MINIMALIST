#!/usr/bin/env python3
"""
🧪 TEST RAPIDE - Vérifier le contenu du fichier Excel events
"""

import pandas as pd
from pathlib import Path

def test_excel_content():
    """Teste le contenu du fichier Excel des événements"""
    
    excel_path = Path("exports/gitlab/gitlab_events_simple.xlsx")
    
    if not excel_path.exists():
        print("❌ Fichier Excel introuvable")
        return
        
    print(f"📂 Fichier trouvé: {excel_path}")
    print(f"📊 Taille: {excel_path.stat().st_size / 1024:.1f} KB")
    
    try:
        # Lire le fichier Excel
        xl_file = pd.ExcelFile(excel_path)
        
        print(f"📋 Feuilles disponibles: {xl_file.sheet_names}")
        
        for sheet_name in xl_file.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"\n📄 Feuille '{sheet_name}':")
            print(f"   📊 Dimensions: {df.shape[0]} lignes x {df.shape[1]} colonnes")
            
            if not df.empty:
                print(f"   📋 Colonnes: {list(df.columns)}")
                print(f"   👁️ Aperçu des 3 premières lignes:")
                print(df.head(3).to_string(index=False))
            else:
                print("   ⚠️ Feuille vide")
                
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {e}")

if __name__ == "__main__":
    test_excel_content()
