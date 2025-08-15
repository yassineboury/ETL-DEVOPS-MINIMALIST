#!/usr/bin/env python3
"""
Constantes globales pour éviter la duplication de code
Identifiées par SonarCloud pour améliorer la maintenabilité
"""

# Formats de date standardisés
DATE_FORMAT_FRENCH = "%d/%m/%Y %H:%M:%S"
DATE_FORMAT_ISO_Z = "%Y-%m-%dT%H:%M:%SZ"

# Chemins d'export
EXPORTS_GITLAB_PATH = "exports/gitlab"

# Messages d'erreur standardisés
ERROR_EXPORT_FAILED = "\n❌ Export échoué!"

# Status de projet - labels français
PROJET_ARCHIVE_STATUS = "archivé"
PROJETS_ARCHIVES_PATH = "projets-archives/"
ERROR_EXTRACTION_FAILED = "❌ Erreur lors de l'extraction"

# Statuts de projets
STATUS_ARCHIVED = "archivé"
STATUS_YES = "Oui"
STATUS_NO = "Non"

# Messages de succès
SUCCESS_EXTRACTION = "✅ Extraction terminée avec succès"

# Configuration par défaut
DEFAULT_EXCEL_ENGINE = "openpyxl"
