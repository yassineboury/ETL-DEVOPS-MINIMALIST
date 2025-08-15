"""
Gestionnaire de configuration pour GitLab Client
Sépare la logique de configuration pour réduire la complexité
"""
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Gestionnaire de configuration GitLab"""
    
    @staticmethod
    def load_config(config_path: str) -> Dict[Any, Any]:
        """
        Charge la configuration depuis un fichier YAML
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Configuration sous forme de dictionnaire
        """
        try:
            with open(config_path, encoding='utf-8') as file:
                config = yaml.safe_load(file)
            print(f"✅ Configuration chargée depuis: {config_path}")
            return config
        except FileNotFoundError:
            print(f"❌ Fichier de configuration introuvable: {config_path}")
            raise
        except yaml.YAMLError as e:
            print(f"❌ Erreur de format YAML: {e}")
            raise

    @staticmethod
    def load_default_config() -> Dict[Any, Any]:
        """
        Charge la configuration par défaut depuis config/config.yaml
        
        Returns:
            Configuration par défaut
        """
        # Chemin vers le fichier de configuration global (pas dans kenobi_tools)
        config_path = Path(__file__).parent.parent.parent.parent / 'config' / 'config.yaml'

        if not config_path.exists():
            print("❌ Fichier config/config.yaml introuvable")
            print("💡 Copiez config/config.example.yaml vers config/config.yaml")
            raise FileNotFoundError(f"Configuration manquante: {config_path}")

        return ConfigManager.load_config(str(config_path))
