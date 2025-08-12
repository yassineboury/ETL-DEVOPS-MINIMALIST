"""
Extracteur de groupes GitLab
Module pour extraire les informations des groupes GitLab selon les spécifications DevSecOps
Optimisé pour export Excel avec métriques de gouvernance et sécurité
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError

from ..base_extractor import BaseExtractor
from ..exceptions import GitLabExtractionError, handle_gitlab_api_error


class GroupsExtractor(BaseExtractor):
    """
    Extracteur pour les groupes GitLab avec focus DevSecOps
    
    Extrait les informations essentielles des groupes :
    - Identité et hiérarchie
    - Membres et rôles détaillés
    - Projets et activité
    - Métriques de stockage
    - Scores de sécurité et gouvernance
    """

    def __init__(self, gitlab_client, batch_size: int = 50):
        """
        Initialise l'extracteur de groupes
        
        Args:
            gitlab_client: Instance du client GitLab authentifié
            batch_size: Taille des batches pour le traitement (défaut: 50)
        """
        super().__init__(gitlab_client, batch_size)
        self.extraction_type = "Groups"

    def extract(self, include_statistics: bool = True, all_available: bool = False, **kwargs) -> pd.DataFrame:
        """
        Méthode principale d'extraction (implémentation de BaseExtractor)
        
        Args:
            include_statistics: Inclure les statistiques de stockage
            all_available: Inclure tous les groupes accessibles
            **kwargs: Arguments supplémentaires
            
        Returns:
            DataFrame avec les informations des groupes
        """
        return self.extract_groups(include_statistics, all_available)

    def extract_groups(self, include_statistics: bool = True, all_available: bool = False) -> pd.DataFrame:
        """
        Extrait les informations de tous les groupes GitLab accessibles
        
        Args:
            include_statistics: Inclure les statistiques de stockage (Premium requis)
            all_available: Inclure tous les groupes accessibles (pas seulement ceux où on est membre)
            
        Returns:
            DataFrame avec les informations des groupes
            
        Raises:
            GitLabExtractionError: En cas d'erreur lors de l'extraction
        """
        try:
            self.logger.info("🏗️ Démarrage extraction groupes GitLab...")
            
            # Récupération de la liste des groupes
            groups = self._get_all_groups(include_statistics, all_available)
            
            if not groups:
                self.logger.warning("Aucun groupe trouvé")
                return pd.DataFrame()
            
            self.logger.info(f"📊 {len(groups)} groupes trouvés - Traitement en cours...")
            
            # Traitement des groupes par batches
            processed_groups = []
            
            for i in range(0, len(groups), self.batch_size):
                batch = groups[i:i + self.batch_size]
                batch_results = self._process_groups_batch(batch, include_statistics)
                processed_groups.extend(batch_results)
                
                self.logger.info(f"✅ Batch {i//self.batch_size + 1}/{(len(groups)-1)//self.batch_size + 1} traité")
            
            # Création du DataFrame final
            df = pd.DataFrame(processed_groups)
            
            if not df.empty:
                # Tri par hiérarchie puis nom
                df = df.sort_values(['is_top_level', 'group_full_path'], ascending=[False, True])
                self.logger.info(f"🎉 Extraction terminée: {len(df)} groupes extraits")
            else:
                self.logger.warning("DataFrame vide après traitement")
            
            return df
            
        except Exception as e:
            error_msg = f"Erreur lors de l'extraction des groupes: {str(e)}"
            self.logger.error(error_msg)
            raise GitLabExtractionError(error_msg) from e

    def _get_all_groups(self, include_statistics: bool, all_available: bool) -> List[Any]:
        """
        Récupère tous les groupes avec pagination
        """
        try:
            params = {
                'per_page': 100,
                'statistics': include_statistics,
                'all_available': all_available,
                'order_by': 'path',
                'sort': 'asc'
            }
            
            groups = []
            page = 1
            
            while True:
                params['page'] = page
                batch = self.gitlab.groups.list(**params)
                
                if not batch:
                    break
                    
                groups.extend(batch)
                page += 1
                
                # Protection contre les boucles infinies
                if page > 100:
                    self.logger.warning("Limite de 100 pages atteinte")
                    break
            
            return groups
            
        except Exception as e:
            handle_gitlab_api_error(e)
            return []  # Retour par défaut en cas d'erreur

    def _process_groups_batch(self, groups_batch: List[Any], include_statistics: bool) -> List[Dict[str, Any]]:
        """
        Traite un batch de groupes et extrait leurs informations
        """
        processed = []
        
        for group in groups_batch:
            try:
                group_data = self._extract_group_data(group, include_statistics)
                processed.append(group_data)
                
            except Exception as e:
                self.logger.error(f"Erreur traitement groupe {getattr(group, 'name', 'Unknown')}: {str(e)}")
                continue
        
        return processed

    def _extract_group_data(self, group: Any, include_statistics: bool) -> Dict[str, Any]:
        """
        Extrait les données d'un groupe spécifique
        """
        # Identité et hiérarchie
        data = {
            "group_id": getattr(group, 'id', None),
            "group_name": getattr(group, 'name', ''),
            "group_full_path": getattr(group, 'full_path', ''),
            "parent_id": getattr(group, 'parent_id', None),
            "is_top_level": getattr(group, 'parent_id', None) is None,
        }
        
        # Extraction des membres et rôles
        members_data = self._extract_members_data(group)
        data.update(members_data)
        
        # Extraction des projets
        projects_data = self._extract_projects_data(group)
        data.update(projects_data)
        
        # Dates
        data.update({
            "created_at": self._format_date(getattr(group, 'created_at', None)),
            "last_activity_at": self._format_date(getattr(group, 'last_activity_at', None))
        })
        
        # Statistiques de stockage (si disponibles)
        if include_statistics:
            storage_data = self._extract_storage_data(group)
            data.update(storage_data)
        else:
            data.update({
                "storage_size_mb": 0.0,
                "repository_size_mb": 0.0,
                "lfs_objects_size_mb": 0.0
            })
        
        return data

    def _extract_members_data(self, group: Any) -> Dict[str, Any]:
        """
        Extrait les données des membres d'un groupe
        """
        try:
            # Récupération des membres directs
            members = group.members.list(per_page=100, all=True)
            
            # Compteurs par rôle
            role_counts = {
                "owners_count": 0,
                "maintainers_count": 0,
                "developers_count": 0,
                "reporters_count": 0,
                "guests_count": 0
            }
            
            billable_count = 0
            pending_count = 0
            
            for member in members:
                access_level = getattr(member, 'access_level', 0)
                state = getattr(member, 'state', 'active')
                
                # Comptage par rôle (access_level)
                if access_level >= 50:  # Owner
                    role_counts["owners_count"] += 1
                elif access_level >= 40:  # Maintainer
                    role_counts["maintainers_count"] += 1
                elif access_level >= 30:  # Developer
                    role_counts["developers_count"] += 1
                elif access_level >= 20:  # Reporter
                    role_counts["reporters_count"] += 1
                elif access_level >= 10:  # Guest
                    role_counts["guests_count"] += 1
                
                # Membres facturables (Developer et plus)
                if access_level >= 30:
                    billable_count += 1
                
                # Membres en attente
                if state == 'awaiting':
                    pending_count += 1
            
            return {
                "total_members": len(members),
                "billable_members": billable_count,
                "pending_members": pending_count,
                **role_counts
            }
            
        except Exception as e:
            self.logger.error(f"Erreur extraction membres: {str(e)}")
            return {
                "total_members": 0,
                "billable_members": 0,
                "pending_members": 0,
                "owners_count": 0,
                "maintainers_count": 0,
                "developers_count": 0,
                "reporters_count": 0,
                "guests_count": 0
            }

    def _extract_projects_data(self, group: Any) -> Dict[str, Any]:
        """
        Extrait les données des projets d'un groupe
        """
        try:
            # Récupération des projets du groupe
            projects = group.projects.list(per_page=100, all=True)
            
            active_count = 0
            for project in projects:
                # Projet actif si non archivé
                if not getattr(project, 'archived', False):
                    active_count += 1
            
            return {
                "projects_count": len(projects),
                "active_projects_count": active_count
            }
            
        except Exception as e:
            self.logger.error(f"Erreur extraction projets: {str(e)}")
            return {
                "projects_count": 0,
                "active_projects_count": 0
            }

    def _extract_storage_data(self, group: Any) -> Dict[str, Any]:
        """
        Extrait les statistiques de stockage d'un groupe (Premium requis)
        """
        try:
            # Vérification si les statistiques sont disponibles
            statistics = getattr(group, 'statistics', None) or getattr(group, 'root_storage_statistics', None)
            
            if statistics:
                return {
                    "storage_size_mb": round((statistics.get('storage_size', 0)) / (1024 * 1024), 2),
                    "repository_size_mb": round((statistics.get('repository_size', 0)) / (1024 * 1024), 2),
                    "lfs_objects_size_mb": round((statistics.get('lfs_objects_size', 0)) / (1024 * 1024), 2)
                }
            else:
                return {
                    "storage_size_mb": 0.0,
                    "repository_size_mb": 0.0,
                    "lfs_objects_size_mb": 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Erreur extraction stockage: {str(e)}")
            return {
                "storage_size_mb": 0.0,
                "repository_size_mb": 0.0,
                "lfs_objects_size_mb": 0.0
            }

    def _format_date(self, date_string: Optional[str]) -> str:
        """
        Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS
        
        Args:
            date_string: Date au format ISO
            
        Returns:
            Date formatée ou "N/A" si None
        """
        if not date_string:
            return "N/A"

        try:
            # Parser la date ISO (gérer différents formats)
            if 'T' in date_string:
                # Format ISO complet
                date_part = date_string.split('T')[0]
                time_part = date_string.split('T')[1].split('.')[0].split('+')[0].split('Z')[0]
            else:
                # Format date simple
                date_part = date_string.split(' ')[0] if ' ' in date_string else date_string
                time_part = date_string.split(' ')[1] if ' ' in date_string else "00:00:00"

            # Parser la date
            dt = datetime.strptime(f"{date_part} {time_part[:8]}", "%Y-%m-%d %H:%M:%S")

            # Formater vers DD/MM/YYYY HH:MM:SS
            return dt.strftime("%d/%m/%Y %H:%M:%S")

        except Exception:
            # En cas d'erreur, retourner la chaîne originale ou N/A
            return date_string if date_string else "N/A"

    def get_group_by_id(self, group_id: int, include_statistics: bool = True) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'un groupe spécifique par son ID
        
        Args:
            group_id: ID du groupe à récupérer
            include_statistics: Inclure les statistiques de stockage
            
        Returns:
            Dictionnaire avec les informations du groupe ou None si non trouvé
        """
        try:
            group = self.gitlab.groups.get(group_id, statistics=include_statistics)
            return self._extract_group_data(group, include_statistics)
            
        except GitlabGetError:
            self.logger.warning(f"Groupe {group_id} non trouvé")
            return None
        except Exception as e:
            self.logger.error(f"Erreur récupération groupe {group_id}: {str(e)}")
            return None

    def get_top_level_groups_only(self, include_statistics: bool = True) -> pd.DataFrame:
        """
        Extrait uniquement les groupes de niveau racine (top-level)
        
        Args:
            include_statistics: Inclure les statistiques de stockage
            
        Returns:
            DataFrame avec les groupes racines uniquement
        """
        try:
            groups = self._get_all_groups(include_statistics, all_available=True)
            
            # Filtrer uniquement les groupes top-level
            top_level_groups = [g for g in groups if getattr(g, 'parent_id', None) is None]
            
            if not top_level_groups:
                self.logger.warning("Aucun groupe top-level trouvé")
                return pd.DataFrame()
            
            self.logger.info(f"📊 {len(top_level_groups)} groupes top-level trouvés")
            
            # Traitement des groupes
            processed_groups = []
            for group in top_level_groups:
                try:
                    group_data = self._extract_group_data(group, include_statistics)
                    processed_groups.append(group_data)
                except Exception as e:
                    self.logger.error(f"Erreur traitement groupe {getattr(group, 'name', 'Unknown')}: {str(e)}")
                    continue
            
            df = pd.DataFrame(processed_groups)
            
            if not df.empty:
                df = df.sort_values('group_full_path')
                self.logger.info(f"🎉 Extraction terminée: {len(df)} groupes top-level extraits")
            
            return df
            
        except Exception as e:
            error_msg = f"Erreur lors de l'extraction des groupes top-level: {str(e)}"
            self.logger.error(error_msg)
            raise GitLabExtractionError(error_msg) from e
