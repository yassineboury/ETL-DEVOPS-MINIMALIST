"""
GitLab Commits Extractor

Extracts comprehensive commit data from GitLab projects with DevSecOps analytics.
Features dual approach: Git native data + GitLab user mapping.

Author: DevSecOps Team
Date: 2025-08-12
"""

import logging
import re
from contextlib import suppress
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import gitlab
from gitlab.v4.objects import Project, ProjectCommit


class CommitsExtractor:
    """Extract commits with comprehensive DevSecOps metrics and statistics."""
    
    # File type patterns for analysis
    CODE_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.swift'}
    CONFIG_EXTENSIONS = {'.yml', '.yaml', '.json', '.xml', '.toml', '.ini', '.conf', '.cfg', '.env'}
    DOC_EXTENSIONS = {'.md', '.rst', '.txt', '.doc', '.docx', '.pdf', '.adoc'}
    
    # Commit message patterns
    PATTERNS = {
        'hotfix': re.compile(r'\b(hotfix|fix|bug|patch|urgent)\b', re.IGNORECASE),
        'feature': re.compile(r'\b(feat|feature|add|new)\b', re.IGNORECASE),
        'refactor': re.compile(r'\b(refactor|refact|restructure|cleanup)\b', re.IGNORECASE),
        'documentation': re.compile(r'\b(doc|docs|documentation|readme)\b', re.IGNORECASE)
    }
    
    # Change magnitude thresholds
    MAGNITUDE_THRESHOLDS = {
        'Small': 50,
        'Medium': 200,
        'Large': 500
    }
    
    def __init__(self, gitlab_client: gitlab.Gitlab):
        """Initialize commits extractor with GitLab client."""
        self.gitlab_client = gitlab_client
        self.logger = logging.getLogger(__name__)
        self._user_cache: Dict[str, Optional[Dict[str, Any]]] = {}
    
    def extract_commits(
        self, 
        project_ids: Optional[List[int]] = None,
        branch_name: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        max_commits: int = 1000
    ) -> pd.DataFrame:
        """
        Extract commits from GitLab projects with comprehensive statistics.
        
        Args:
            project_ids: List of project IDs to extract from (None for all accessible)
            branch_name: Specific branch to extract from (None for default branch)
            since: Start date in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            until: End date in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            max_commits: Maximum commits per project
            
        Returns:
            DataFrame with commit data and statistics
        """
        self.logger.info("Starting commits extraction with DevSecOps analytics")
        
        if project_ids is None:
            projects = self._get_accessible_projects()
        else:
            projects = [self._get_project_safely(pid) for pid in project_ids]
            projects = [p for p in projects if p is not None]
        
        if not projects:
            self.logger.warning("No accessible projects found")
            return self._create_empty_dataframe()
        
        all_commits_data = []
        
        for project in projects:
            try:
                self.logger.info(f"Extracting commits from project: {project.name} (ID: {project.id})")
                project_commits = self._extract_project_commits(
                    project, branch_name, since, until, max_commits
                )
                all_commits_data.extend(project_commits)
                
            except Exception as e:
                self.logger.error(f"Error extracting commits from project {project.id}: {e}")
                continue
        
        if not all_commits_data:
            self.logger.warning("No commits data extracted")
            return self._create_empty_dataframe()
        
        df = pd.DataFrame(all_commits_data)
        self.logger.info(f"Successfully extracted {len(df)} commits with statistics")
        return df
    
    def _extract_project_commits(
        self, 
        project: Project, 
        branch_name: Optional[str],
        since: Optional[str],
        until: Optional[str],
        max_commits: int
    ) -> List[Dict[str, Any]]:
        """Extract commits from a single project with full statistics."""
        commits_data = []
        
        try:
            # Build parameters for commits API call
            commit_params = {
                'all': True,
                'with_stats': True,
                'per_page': min(max_commits, 100)
            }
            
            if branch_name:
                commit_params['ref_name'] = branch_name
            if since:
                commit_params['since'] = since
            if until:
                commit_params['until'] = until
            
            # Get commits from GitLab API
            commits = project.commits.list(**commit_params)
            
            for commit in commits[:max_commits]:
                try:
                    commit_data = self._process_commit_data(project, commit, branch_name)
                    if commit_data:
                        commits_data.append(commit_data)
                        
                except Exception as e:
                    self.logger.error(f"Error processing commit {commit.id}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error fetching commits from project {project.id}: {e}")
        
        return commits_data
    
    def _process_commit_data(
        self, 
        project: Project, 
        commit: ProjectCommit, 
        branch_name: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Process individual commit data with comprehensive statistics."""
        try:
            # Get detailed commit info with stats
            detailed_commit = project.commits.get(commit.id, lazy=False)
            
            # Base commit data
            commit_data = {
                # Basic commit info
                'id_commit': detailed_commit.id,
                'short_id': detailed_commit.short_id,
                'author_name': detailed_commit.author_name,
                'author_email': detailed_commit.author_email,
                'authored_date': self._parse_datetime(detailed_commit.authored_date),
                'committer_name': detailed_commit.committer_name,
                'committer_email': detailed_commit.committer_email,
                'committed_date': self._parse_datetime(detailed_commit.committed_date),
                'created_at': self._parse_datetime(detailed_commit.created_at),
                
                # Project context
                'project_id': project.id,
                'branch_name': branch_name,
                
                # Parent analysis
                'parent_ids': detailed_commit.parent_ids or [],
                'parent_count': len(detailed_commit.parent_ids or []),
                'is_merge_commit': len(detailed_commit.parent_ids or []) > 1,
            }
            
            # Add GitLab user mapping
            gitlab_user = self._get_gitlab_user_by_email(detailed_commit.author_email)
            commit_data.update({
                'gitlab_user_id': gitlab_user.get('id') if gitlab_user else None,
                'gitlab_username': gitlab_user.get('username') if gitlab_user else None,
            })
            
            # Add commit statistics
            stats_data = self._extract_commit_stats(detailed_commit)
            commit_data.update(stats_data)
            
            # Add file analysis
            files_data = self._analyze_commit_files(project, detailed_commit)
            commit_data.update(files_data)
            
            # Add pattern analysis
            patterns_data = self._analyze_commit_patterns(detailed_commit)
            commit_data.update(patterns_data)
            
            return commit_data
            
        except Exception as e:
            self.logger.error(f"Error processing commit data for {commit.id}: {e}")
            return None
    
    def _extract_commit_stats(self, commit: ProjectCommit) -> Dict[str, Any]:
        """Extract commit statistics with calculations."""
        stats = {}
        
        # Base statistics from GitLab API
        commit_stats = getattr(commit, 'stats', {})
        if commit_stats:
            additions = commit_stats.get('additions', 0)
            deletions = commit_stats.get('deletions', 0)
            total = commit_stats.get('total', additions + deletions)
            
            stats.update({
                'stats_additions': additions,
                'stats_deletions': deletions,
                'stats_total': total,
            })
            
            # Calculate derived metrics
            if deletions > 0:
                stats['change_ratio'] = round(additions / deletions, 2)
            else:
                stats['change_ratio'] = float('inf') if additions > 0 else 0.0
            
            stats['net_change'] = additions - deletions
            stats['change_magnitude'] = self._calculate_change_magnitude(total)
        else:
            # Default values when stats not available
            stats.update({
                'stats_additions': 0,
                'stats_deletions': 0,
                'stats_total': 0,
                'change_ratio': 0.0,
                'net_change': 0,
                'change_magnitude': 'Small'
            })
        
        return stats
    
    def _analyze_commit_files(self, project: Project, commit: ProjectCommit) -> Dict[str, Any]:
        """Analyze files changed in commit with type categorization."""
        files_data = {
            'files_changed': 0,
            'files_added': 0,
            'files_deleted': 0,
            'files_renamed': 0,
            'code_files_changed': 0,
            'config_files_changed': 0,
            'doc_files_changed': 0,
            'test_files_changed': 0,
        }
        
        try:
            # Get commit diff to analyze files
            diff = project.commits.get(commit.id, lazy=False).diff()
            
            for file_diff in diff:
                files_data['files_changed'] += 1
                self._analyze_file_operation(file_diff, files_data)
                self._analyze_file_type(file_diff, files_data)
                        
        except Exception as e:
            self.logger.error(f"Error analyzing files for commit {commit.id}: {e}")
        
        return files_data
    
    def _analyze_file_operation(self, file_diff: Any, files_data: Dict[str, int]) -> None:
        """Analyze file operation type (add, delete, rename)."""
        if getattr(file_diff, 'new_file', False):
            files_data['files_added'] += 1
        elif getattr(file_diff, 'deleted_file', False):
            files_data['files_deleted'] += 1
        elif getattr(file_diff, 'renamed_file', False):
            files_data['files_renamed'] += 1
    
    def _analyze_file_type(self, file_diff: Any, files_data: Dict[str, int]) -> None:
        """Analyze file type and categorize (code, config, docs, test)."""
        file_path = getattr(file_diff, 'new_path', '') or getattr(file_diff, 'old_path', '')
        if not file_path:
            return
        
        file_extension = self._get_file_extension(file_path)
        file_name = file_path.lower()
        
        if file_extension in self.CODE_EXTENSIONS:
            files_data['code_files_changed'] += 1
        elif file_extension in self.CONFIG_EXTENSIONS:
            files_data['config_files_changed'] += 1
        elif file_extension in self.DOC_EXTENSIONS:
            files_data['doc_files_changed'] += 1
        elif 'test' in file_name or 'spec' in file_name:
            files_data['test_files_changed'] += 1
    
    def _analyze_commit_patterns(self, commit: ProjectCommit) -> Dict[str, bool]:
        """Analyze commit message patterns for type classification."""
        message = getattr(commit, 'title', '') + ' ' + getattr(commit, 'message', '')
        
        return {
            'is_hotfix': bool(self.PATTERNS['hotfix'].search(message)),
            'is_feature': bool(self.PATTERNS['feature'].search(message)),
            'is_refactor': bool(self.PATTERNS['refactor'].search(message)),
            'is_documentation': bool(self.PATTERNS['documentation'].search(message)),
        }
    
    def _calculate_change_magnitude(self, total_changes: int) -> str:
        """Calculate change magnitude category."""
        if total_changes <= self.MAGNITUDE_THRESHOLDS['Small']:
            return 'Small'
        elif total_changes <= self.MAGNITUDE_THRESHOLDS['Medium']:
            return 'Medium'
        elif total_changes <= self.MAGNITUDE_THRESHOLDS['Large']:
            return 'Large'
        else:
            return 'XLarge'
    
    def _get_gitlab_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get GitLab user by email with caching."""
        if email in self._user_cache:
            return self._user_cache[email]
        
        try:
            users = self.gitlab_client.users.list(search=email, per_page=1)
            if users and users[0].email.lower() == email.lower():
                user_data = {
                    'id': users[0].id,
                    'username': users[0].username,
                    'name': getattr(users[0], 'name', ''),
                    'state': getattr(users[0], 'state', ''),
                }
                self._user_cache[email] = user_data
                return user_data
        except Exception:
            pass
        
        self._user_cache[email] = None
        return None
    
    def _get_accessible_projects(self) -> List[Project]:
        """Get list of accessible projects."""
        try:
            return self.gitlab_client.projects.list(
                membership=True,
                per_page=100,
                order_by='last_activity_at'
            )
        except Exception as e:
            self.logger.error(f"Error fetching accessible projects: {e}")
            return []
    
    def _get_project_safely(self, project_id: int) -> Optional[Project]:
        """Get project by ID with error handling."""
        with suppress(Exception):
            return self.gitlab_client.projects.get(project_id, lazy=False)
        return None
    
    def _get_file_extension(self, file_path: str) -> str:
        """Extract file extension from path."""
        return '.' + file_path.split('.')[-1].lower() if '.' in file_path else ''
    
    def _parse_datetime(self, date_str: str) -> Optional[str]:
        """Parse datetime string safely."""
        if not date_str:
            return None
        try:
            # GitLab returns ISO format, keep as string for Excel compatibility
            return date_str
        except Exception:
            return None
    
    def _create_empty_dataframe(self) -> pd.DataFrame:
        """Create empty DataFrame with all expected columns."""
        columns = [
            'id_commit', 'short_id', 'author_name', 'author_email', 'authored_date',
            'committer_name', 'committer_email', 'committed_date', 'created_at',
            'gitlab_user_id', 'gitlab_username', 'parent_ids', 'parent_count', 
            'is_merge_commit', 'project_id', 'branch_name', 'stats_additions',
            'stats_deletions', 'stats_total', 'change_ratio', 'net_change',
            'change_magnitude', 'files_changed', 'files_added', 'files_deleted',
            'files_renamed', 'code_files_changed', 'config_files_changed',
            'doc_files_changed', 'test_files_changed', 'is_hotfix', 'is_feature',
            'is_refactor', 'is_documentation'
        ]
        return pd.DataFrame(columns=columns)
