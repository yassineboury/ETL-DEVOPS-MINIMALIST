# kenobi_tools/sonar/client/sonar_client.py
import os
import warnings
import urllib3
from dotenv import load_dotenv
from sonarqube import SonarQubeClient

# Supprimer les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class SonarClient:
    """
    Client pour interagir avec l'API SonarQube en utilisant la bibliothèque python-sonarqube-api.
    Sa seule responsabilité est de fournir un client SonarQube configuré et authentifié.
    """
    def __init__(self):
        """
        Initialise le client SonarQube en chargeant la configuration.
        """
        load_dotenv()
        self.sonar_url = os.getenv("SONAR_URL")
        self.sonar_token = os.getenv("SONAR_TOKEN")
        
        if not self.sonar_url or not self.sonar_token:
            raise ValueError("Les variables d'environnement SONAR_URL et SONAR_TOKEN sont requises.")
            
        self.client: SonarQubeClient | None = None # Préciser le type
        self.is_connected = False

    def _is_internal_domain(self, url: str) -> bool:
        """
        Vérifie si l'URL correspond à un domaine interne.
        """
        internal_domains = ['.oncf.net', 'localhost', '127.0.0.1', '192.168.', '10.', '172.']
        return any(domain in url for domain in internal_domains)

    def connect(self) -> SonarQubeClient:
        """
        Établit la connexion à l'API SonarQube et la teste.
        
        Returns:oui
            Un client SonarQube authentifié.
        """
        if self.is_connected and self.client:
            return self.client

        try:
            print(f"🔗 Connexion à SonarQube: {self.sonar_url}")
            
            # Configuration SSL pour domaines internes
            # Assertion de type : self.sonar_url ne peut pas être None ici car vérifié dans __init__
            assert self.sonar_url is not None
            ssl_verify = not self._is_internal_domain(self.sonar_url)
            if not ssl_verify:
                print("⚠️ Vérification SSL désactivée pour domaine interne")
            
            self.client = SonarQubeClient(
                sonarqube_url=self.sonar_url, 
                token=self.sonar_token,
                verify=ssl_verify
            )
            
            # Test de la connexion en récupérant la version du serveur
            version = self.client.server.get_server_version()
            print(f"✅ Connexion à SonarQube réussie (Version: {version}).")
            self.is_connected = True
            return self.client

        except Exception as e:
            print(f"❌ Erreur de l'API SonarQube: {e}")
            self.is_connected = False
            self.client = None # S'assurer que le client est None en cas d'erreur
            raise ConnectionError(f"Impossible de se connecter à SonarQube: {e}") from e


    def get_client(self) -> SonarQubeClient:
        """
        Retourne le client SonarQube (se connecte si nécessaire).
        Lève une ConnectionError si la connexion échoue.
        """
        if not self.client or not self.is_connected:
            self.connect()
        
        # Cette vérification garantit que nous ne retournons jamais None
        if not self.client:
            raise ConnectionError("La connexion à SonarQube a échoué et le client n'est pas disponible.")
            
        return self.client
