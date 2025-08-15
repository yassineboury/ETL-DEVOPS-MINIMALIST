"""
Classification des utilisateurs GitLab
Sépare la logique de classification pour réduire la complexité cognitive
"""


class UserClassifier:
    """Classification et validation des utilisateurs GitLab"""
    
    @staticmethod
    def determine_user_type(user) -> str:
        """
        Détermine si un utilisateur est Humain, Bot ou Service
        
        Args:
            user: Objet utilisateur GitLab
            
        Returns:
            Type d'utilisateur: "Humain", "Bot", "Service"
        """
        # Priorité 1: Vérifier l'attribut natif GitLab
        is_gitlab_bot = getattr(user, 'bot', False)
        if is_gitlab_bot:
            return "Bot"
        
        username = getattr(user, 'username', '').lower()
        name = getattr(user, 'name', '').lower()
        email = getattr(user, 'email', '').lower()

        # Vérifier les patterns de service (comptes techniques organisationnels)
        if UserClassifier._is_service_account(username, name, email):
            return "Service"

        # Vérifier les patterns de bot custom
        if UserClassifier._is_bot_account(username, name, email):
            return "Bot"

        # Par défaut, considérer comme humain
        return "Humain"

    @staticmethod
    def _is_service_account(username: str, name: str, email: str) -> bool:
        """Vérifie si l'utilisateur est un compte de service"""
        service_patterns = [
            'deploy', 'service', 'system', 'backup', 'monitoring', 'alert',
            'scheduler', 'cron', 'batch', 'process', 'gitlabuser', 'sonarqube',
            'nexus', 'artifactory', 'prometheus', 'grafana', 'kibana', 'elastic',
            'gitlab-duo', 'gitlabduo', 'duo', 'pic-', 'jks', 'atman_netopia'
        ]

        return any(pattern in field 
                  for pattern in service_patterns 
                  for field in [username, name, email])

    @staticmethod
    def _is_bot_account(username: str, name: str, email: str) -> bool:
        """Vérifie si l'utilisateur est un bot"""
        bot_patterns = [
            'robot', 'ci', 'cd', 'build', 'jenkins', 'gitlab-ci',
            'admin', 'noreply', 'ghost', 'runner'
        ]

        return any(pattern in field 
                  for pattern in bot_patterns 
                  for field in [username, name, email])

    @staticmethod
    def is_human_user(user) -> bool:
        """
        Filtre pour déterminer si un utilisateur est humain
        
        Args:
            user: Objet utilisateur GitLab
            
        Returns:
            True si l'utilisateur est considéré comme humain
        """
        user_type = UserClassifier.determine_user_type(user)

        # Ne garder que les humains
        if user_type != "Humain":
            return False

        # Exclure les utilisateurs "ghost" (supprimés)
        username = getattr(user, 'username', '').lower()
        if 'ghost' in username or username.startswith('ghost'):
            return False

        # Exclure les comptes techniques avec nom identique au username (sauf prénoms simples)
        name = getattr(user, 'name', '').lower()
        if username == name and len(username) > 5:  # Éviter d'exclure des prénoms courts
            return False

        # Exclure les états non pertinents (garder active, blocked et deactivated)
        state = getattr(user, 'state', 'active')
        return state in ['active', 'blocked', 'deactivated']
