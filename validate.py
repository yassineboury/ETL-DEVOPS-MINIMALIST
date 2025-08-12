#!/usr/bin/env python3
"""
Script de validation simple pour l'extracteur GitLab.

Alternative lightweight aux tests complets pytest.
Validation rapide des fonctionnalités essentielles.

Author: DevSecOps Team
Date: 2025-08-12
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from gitlab_tools.config import get_default_config, validate_batch_size
from gitlab_tools.exceptions import GitLabExtractionError, ValidationError


def test_config():
    """Validation rapide de la configuration."""
    print("🔧 Test Configuration...")
    
    try:
        config = get_default_config()
        assert config['batch']['size'] == 10
        assert validate_batch_size(0) == 5  # Min
        assert validate_batch_size(25) == 20  # Max
        print("✅ Configuration OK")
        return True
    except Exception as e:
        print(f"❌ Configuration KO: {e}")
        return False


def test_exceptions():
    """Validation du système d'exceptions."""
    print("🚨 Test Exceptions...")
    
    try:
        # Test création exception
        error = GitLabExtractionError("Test error", project_id=123)
        assert "Test error" in str(error)
        assert "Project: 123" in str(error)
        
        # Test ValidationError
        val_error = ValidationError("Invalid data")
        assert isinstance(val_error, GitLabExtractionError)
        
        print("✅ Exceptions OK")
        return True
    except Exception as e:
        print(f"❌ Exceptions KO: {e}")
        return False


def test_imports():
    """Validation que tous les imports fonctionnent."""
    print("📦 Test Imports...")
    
    try:
        from gitlab_tools.extractors.commits_extractor import CommitsExtractor
        from gitlab_tools.base_extractor import BaseExtractor
        from gitlab_tools.utils.batch_processor import GitLabBatchProcessor
        from gitlab_tools.utils.cache_manager import CacheManager
        print("✅ Imports OK")
        return True
    except Exception as e:
        print(f"❌ Imports KO: {e}")
        return False


def test_real_instantiation():
    """Test d'instanciation réelle avec mock client."""
    print("🏗️ Test Instanciation Réelle...")
    
    try:
        # Mock client simple pour les tests
        class MockGitLabClient:
            def __init__(self):
                self.projects = MockProjects()
                
        class MockProjects:
            def list(self, **_kwargs):
                return []
        
        mock_client = MockGitLabClient()
        
        # Test CommitsExtractor avec typing souple
        from gitlab_tools.extractors.commits_extractor import CommitsExtractor
        extractor = CommitsExtractor(mock_client, batch_size=5, enable_cache=False)  # type: ignore
        
        assert extractor.batch_size == 5
        assert extractor.enable_cache is False
        assert hasattr(extractor, 'config')
        
        print("✅ Instanciation Réelle OK")
        return True
    except Exception as e:
        print(f"❌ Instanciation Réelle KO: {e}")
        return False


def main():
    """Lancer les validations essentielles."""
    print("🚀 Validation ETL DevSecOps Minimalist")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config, 
        test_exceptions,
        test_real_instantiation
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    # Résumé
    passed = sum(results)
    total = len(results)
    
    print("📊 Résultats:")
    print(f"✅ {passed}/{total} validations passées")
    
    if passed == total:
        print("🎉 Tout est OK - Prêt à utiliser !")
        return 0
    else:
        print("⚠️ Certaines validations ont échoué")
        return 1


if __name__ == "__main__":
    sys.exit(main())
