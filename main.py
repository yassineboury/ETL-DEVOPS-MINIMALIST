"""
Point d'entrée principal de l'ETL DevSecOps
"""
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Ajout du dossier parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
import yaml
import gitlab
import pandas as pd

# Imports des modules d'extraction
from gitlab.gitlab_projects import extract_projects, extract_projects_by_ids
from gitlab.gitlab_users import extract_users
from sonar.sonar_coverage import extract_coverage


def load_config():
    """Charge la configuration depuis config.yaml"""
    try:
        with open('config/config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print("❌ Fichier config/config.yaml introuvable")
        print("💡 Copiez config/config.example.yaml vers config/config.yaml")
        sys.exit(1)


def load_projects_config():
    """Charge la liste des projets depuis projects.yaml"""
    try:
        with open('config/projects.yaml', 'r', encoding='utf-8') as file:
            projects_config = yaml.safe_load(file)
        return projects_config
    except FileNotFoundError:
        print("❌ Fichier config/projects.yaml introuvable")
        sys.exit(1)


def create_gitlab_client(config):
    """Crée et retourne un client GitLab authentifié"""
    try:
        gitlab_url = config['gitlab']['url']
        gitlab_token = os.getenv('GITLAB_TOKEN') or config['gitlab']['token']
        
        if not gitlab_token or gitlab_token.startswith('${'):
            print("❌ Token GitLab manquant. Vérifiez votre fichier .env")
            sys.exit(1)
            
        gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        gl.auth()  # Test de la connexion
        print(f"✅ Connexion GitLab réussie: {gitlab_url}")
        return gl
        
    except Exception as e:
        print(f"❌ Erreur de connexion GitLab: {e}")
        sys.exit(1)


def create_output_directory():
    """Crée le dossier de sortie s'il n'existe pas"""
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_to_excel(dataframes: dict, filename: str):
    """Sauvegarde plusieurs DataFrames dans un fichier Excel multi-onglets"""
    output_path = create_output_directory() / filename
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in dataframes.items():
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"📊 Onglet '{sheet_name}': {len(df)} lignes")
                else:
                    print(f"⚠️ Onglet '{sheet_name}': aucune donnée")
                    
        print(f"✅ Fichier Excel créé: {output_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier Excel: {e}")


def extract_gitlab_data(gl_client, projects_config):
    """Extrait toutes les données GitLab"""
    print("\n" + "="*50)
    print("🚀 EXTRACTION GITLAB")
    print("="*50)
    
    gitlab_data = {}
    
    # 1. Extraction des projets
    if projects_config.get('projects'):
        # Projets spécifiques par ID
        project_ids = [p['id'] for p in projects_config['projects'] if 'id' in p]
        if project_ids:
            gitlab_data['Projets'] = extract_projects_by_ids(gl_client, project_ids)
    else:
        # Tous les projets
        gitlab_data['Projets'] = extract_projects(gl_client)
    
    # 2. Extraction des utilisateurs
    gitlab_data['Utilisateurs'] = extract_users(gl_client)
    
    return gitlab_data


def extract_sonar_data(config, project_keys):
    """Extrait toutes les données SonarQube"""
    print("\n" + "="*50)
    print("🚀 EXTRACTION SONARQUBE")
    print("="*50)
    
    sonar_data = {}
    
    sonar_url = config['sonar']['url']
    sonar_token = os.getenv('SONAR_TOKEN') or config['sonar']['token']
    
    if not sonar_token or sonar_token.startswith('${'):
        print("⚠️ Token SonarQube manquant, extraction SonarQube ignorée")
        return sonar_data
    
    # 1. Extraction de la couverture
    if project_keys:
        sonar_data['Couverture'] = extract_coverage(sonar_url, sonar_token, project_keys)
    
    return sonar_data


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='ETL DevSecOps - Extraction GitLab et SonarQube')
    parser.add_argument('--gitlab-only', action='store_true', help='Extraire uniquement GitLab')
    parser.add_argument('--sonar-only', action='store_true', help='Extraire uniquement SonarQube')
    
    args = parser.parse_args()
    
    print("🚀 ETL DevSecOps - Démarrage")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Chargement de la configuration
    load_dotenv()  # Charge les variables d'environnement depuis .env
    config = load_config()
    projects_config = load_projects_config()
    
    # Liste des clés de projets pour SonarQube (à adapter selon vos projets)
    project_keys = ['your-project-key-1', 'your-project-key-2']  # À personnaliser
    
    # Extraction GitLab
    if not args.sonar_only:
        gl_client = create_gitlab_client(config)
        gitlab_data = extract_gitlab_data(gl_client, projects_config)
        
        if gitlab_data:
            save_to_excel(gitlab_data, 'gitlab_indicators.xlsx')
    
    # Extraction SonarQube
    if not args.gitlab_only:
        sonar_data = extract_sonar_data(config, project_keys)
        
        if sonar_data:
            save_to_excel(sonar_data, 'sonar_indicators.xlsx')
    
    print("\n🎉 ETL terminé avec succès!")
    print(f"📁 Fichiers générés dans le dossier: {create_output_directory()}")


if __name__ == "__main__":
    main()
