"""
Client de connexion GitLab - VERSION REFACTORISÉE
Module principal pour établir et gérer la connexion à GitLab
Complexité cognitive réduite via séparation des responsabilités
"""
import warnings
from typing import Optional

import gitlab as python_gitlab
import urllib3
from dotenv import load_dotenv

from .config_manager import ConfigManager
from .gitlab_validator import GitLabValidator

# Supprimer les warnings SSL et de pagination
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="gitlab")


class GitLabClient:
    """Client GitLab avec gestion de la connexion et des erreurs - VERSION SIMPLIFIÉE"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le client GitLab
        
        Args:
            config_path: Chemin vers le fichier de configuration (optionnel)
        """
        self.config = None
        self.client = None
        self.is_connected = False

        # Charger les variables d'environnement
        load_dotenv()

        # Charger la configuration via le gestionnaire dédié
        if config_path:
            self.config = ConfigManager.load_config(config_path)
        else:
            self.config = ConfigManager.load_default_config()

    def connect(
        self, url: Optional[str] = None, token: Optional[str] = None
    ) -> python_gitlab.Gitlab:
        """
        Établit la connexion à GitLab
        
        Args:
            url: URL de l'instance GitLab (optionnel, lu depuis config si non fourni)
            token: Token d'accès GitLab (optionnel, lu depuis env/config si non fourni)
            
        Returns:
            Client GitLab authentifié
            
        Raises:
            Exception: En cas d'erreur de connexion
        """
        try:
            # Déterminer les paramètres via le validateur
            gitlab_url = GitLabValidator.determine_url(self.config, url)
            gitlab_token = GitLabValidator.determine_token(self.config, token)

            # Créer et tester le client
            self.client = self._create_gitlab_client(gitlab_url, gitlab_token)
            self._test_connection()

            self.is_connected = True
            return self.client

        except python_gitlab.GitlabAuthenticationError as e:
            print(f"❌ Erreur d'authentification GitLab: {e}")
            print("💡 Vérifiez votre token d'accès")
            raise
        except python_gitlab.GitlabGetError as e:
            print(f"❌ Erreur d'accès GitLab: {e}")
            raise
        except Exception as e:
            print(f"❌ Erreur de connexion GitLab: {e}")
            raise

    def _create_gitlab_client(self, gitlab_url: str, gitlab_token: str) -> python_gitlab.Gitlab:
        """
        Crée le client GitLab avec les paramètres appropriés
        
        Args:
            gitlab_url: URL de l'instance GitLab
            gitlab_token: Token d'authentification
            
        Returns:
            Client GitLab configuré
        """
        print(f"🔗 Connexion à GitLab: {gitlab_url}")

        # Validation sécurisée de l'URL
        if not GitLabValidator.validate_url_format(gitlab_url):
            raise ValueError(f"Format d'URL invalide: {gitlab_url}")

        # Configuration SSL depuis la config ou basée sur le domaine
        ssl_verify = True
        if self.config and 'gitlab' in self.config and 'ssl_verify' in self.config['gitlab']:
            ssl_verify = self.config['gitlab']['ssl_verify']
        else:
            ssl_verify = not GitLabValidator.is_internal_domain(gitlab_url)
        
        if not ssl_verify:
            print("⚠️ Vérification SSL désactivée")
        
        return python_gitlab.Gitlab(
            url=gitlab_url,
            private_token=gitlab_token,
            ssl_verify=ssl_verify,
            timeout=30,
            retry_transient_errors=True
        )

    def _test_connection(self):
        """
        Teste la connexion GitLab
        """
        if not self.client:
            raise ConnectionError("Client GitLab non initialisé")
            
        try:
            # Test basique d'authentification
            self.client.auth()
            
            # Essayer d'obtenir les infos utilisateur
            try:
                current_user = self.client.user
                if current_user and hasattr(current_user, 'name'):
                    print(f"✅ Connecté en tant que: {current_user.name} ({current_user.username})")
                else:
                    # Fallback: essayer d'obtenir les infos via l'API
                    if current_user and hasattr(current_user, 'id'):
                        user_info = self.client.users.get(current_user.id, lazy=True)
                        print(f"✅ Connexion établie - User ID: {user_info.id}")
                    else:
                        print("✅ Connexion GitLab établie (infos utilisateur limitées)")
            except Exception:
                # Si impossible d'obtenir les infos utilisateur, tester l'accès aux projets
                print("✅ Connexion GitLab établie (infos utilisateur non disponibles)")
            
            # Test d'accès aux ressources
            try:
                projects = self.client.projects.list(owned=True, simple=True, per_page=1, get_all=False)
                print(f"🔍 Accès vérifié - {len(projects)} projet(s) accessible(s)")
            except Exception:
                # Essayer un accès plus basique
                try:
                    version = self.client.version()
                    print(f"🔍 Accès API vérifié - Version GitLab: {version}")
                except Exception:
                    print("🔍 Connexion basique établie")
            
        except python_gitlab.GitlabAuthenticationError:
            raise python_gitlab.GitlabAuthenticationError("Token GitLab invalide ou expiré")
        except python_gitlab.GitlabGetError as e:
            if e.response_code == 403:
                raise python_gitlab.GitlabGetError("Permissions insuffisantes")
            raise
        except Exception as e:
            raise ConnectionError(f"Erreur de test de connexion: {e}")

    def get_client(self) -> python_gitlab.Gitlab:
        """
        Retourne le client GitLab (se connecte automatiquement si nécessaire)
        
        Returns:
            Client GitLab authentifié
            
        Raises:
            ValueError: Si la connexion échoue
        """
        if not self.is_connected or not self.client:
            self.connect()

        if not self.client:
            raise ValueError("Impossible d'établir la connexion GitLab")

        return self.client

    def disconnect(self):
        """Ferme la connexion GitLab proprement"""
        if self.client:
            self.client = None
        self.is_connected = False
        print("🔌 Connexion GitLab fermée")

    def is_connection_active(self) -> bool:
        """
        Vérifie si la connexion est toujours active
        
        Returns:
            True si la connexion est active
        """
        if not self.is_connected or not self.client:
            return False

        try:
            # Test simple pour vérifier la validité de la connexion
            self.client.user
            return True
        except Exception:
            return False
