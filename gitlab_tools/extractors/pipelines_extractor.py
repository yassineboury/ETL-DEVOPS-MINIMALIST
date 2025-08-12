"""
Extracteur de pipelines GitLab
Module pour extraire les informations des pipelines CI/CD selon les spécifications DevSecOps
"""
import contextlib
from datetime import datetime
from typing import Any, Dict, List, Optional

import gitlab as python_gitlab
import pandas as pd


def _format_date(date_string: Optional[str]) -> str:
    """
    Formate une date ISO vers le format DD/MM/YYYY HH:MM:SS

    Args:
        date_string: Date au format ISO (ex: "2024-01-15T14:30:25.123Z")

    Returns:
        Date formatée (ex: "15/01/2024 14:30:25") ou "N/A" si None
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


def _calculate_duration_minutes(start_time: Optional[str], end_time: Optional[str]) -> float:
    """
    Calcule la durée entre deux timestamps en minutes

    Args:
        start_time: Timestamp de début
        end_time: Timestamp de fin

    Returns:
        Durée en minutes (arrondie à 2 décimales)
    """
    if not start_time or not end_time:
        return 0.0

    try:
        # Convertir les timestamps en objets datetime
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

        # Calculer la différence en minutes
        duration = (end - start).total_seconds() / 60
        return round(duration, 2)

    except Exception:
        return 0.0


def _calculate_queue_time_minutes(created_at: Optional[str], started_at: Optional[str]) -> float:
    """
    Calcule le temps d'attente en file d'attente

    Args:
        created_at: Timestamp de création du pipeline
        started_at: Timestamp de début d'exécution

    Returns:
        Temps d'attente en minutes
    """
    return _calculate_duration_minutes(created_at, started_at)


def _calculate_success_rate(pipeline_jobs: List) -> float:
    """
    Calcule le taux de réussite des jobs

    Args:
        pipeline_jobs: Liste des jobs du pipeline

    Returns:
        Taux de réussite en pourcentage
    """
    if not pipeline_jobs:
        return 0.0

    try:
        total_jobs = len(pipeline_jobs)
        success_jobs = sum(1 for job in pipeline_jobs if getattr(job, 'status', '') == 'success')

        if total_jobs > 0:
            return round((success_jobs / total_jobs) * 100, 2)

        return 0.0

    except Exception:
        return 0.0


def _get_environment_from_ref(ref_lower: str) -> str:
    """Détermine l'environnement basé sur la branche"""
    if 'main' in ref_lower or 'master' in ref_lower:
        return "production"
    elif 'staging' in ref_lower or 'preprod' in ref_lower:
        return "staging"
    elif 'develop' in ref_lower or 'dev' in ref_lower:
        return "development"
    elif 'test' in ref_lower or 'qa' in ref_lower:
        return "test"
    elif 'feature' in ref_lower:
        return "development"
    elif 'hotfix' in ref_lower or 'fix' in ref_lower:
        return "production"
    return "unknown"


def _determine_environment(pipeline_ref: str) -> str:
    """
    Détermine l'environnement cible basé sur la branche

    Args:
        pipeline_ref: Branche du pipeline

    Returns:
        Environnement cible
    """
    ref_lower = pipeline_ref.lower() if pipeline_ref else ""
    return _get_environment_from_ref(ref_lower)


def _translate_pipeline_source(source: str) -> str:
    """
    Traduit la source du pipeline en français

    Args:
        source: Source technique GitLab

    Returns:
        Source traduite
    """
    source_translations = {
        'push': 'Push',
        'web': 'Manuel',
        'trigger': 'Déclencheur',
        'schedule': 'Planifié',
        'api': 'API',
        'external': 'Externe',
        'pipeline': 'Pipeline',
        'chat': 'Chat',
        'merge_request_event': 'Merge Request'
    }

    return source_translations.get(source.lower() if source else '', source or 'Inconnu')


def _process_pipeline_data(pipeline) -> Optional[Dict[str, Any]]:
    """
    Traite les données d'un pipeline individuel

    Args:
        pipeline: Objet pipeline GitLab

    Returns:
        Dictionnaire avec les données formatées du pipeline ou None si erreur
    """
    try:
        # Récupérer les jobs du pipeline pour calculer le taux de réussite
        pipeline_jobs = []
        with contextlib.suppress(Exception):
            # Si on ne peut pas récupérer les jobs, continuer sans
            pipeline_jobs = pipeline.jobs.list(all=True)

        # Calculer les métriques temporelles
        duree_totale = _calculate_duration_minutes(
            getattr(pipeline, 'started_at', None),
            getattr(pipeline, 'finished_at', None)
        )

        temps_attente = _calculate_queue_time_minutes(
            getattr(pipeline, 'created_at', None),
            getattr(pipeline, 'started_at', None)
        )

        # Déterminer l'environnement
        environnement = _determine_environment(getattr(pipeline, 'ref', ''))

        return {
            'id_pipeline': getattr(pipeline, 'id', 0),
            'id_projet': getattr(pipeline, 'project_id', 0),
            'numero_pipeline': getattr(pipeline, 'iid', 0),
            'ref_branche': getattr(pipeline, 'ref', 'N/A'),
            'statut': getattr(pipeline, 'status', 'unknown'),
            'duree_totale_minutes': duree_totale,
            'date_creation': _format_date(getattr(pipeline, 'created_at', None)),
            'date_debut': _format_date(getattr(pipeline, 'started_at', None)),
            'date_fin': _format_date(getattr(pipeline, 'finished_at', None)),
            'temps_attente_minutes': temps_attente,
            'taux_reussite_pourcent': _calculate_success_rate(pipeline_jobs),
            'environnement_cible': environnement,
            'source_declenchement': _translate_pipeline_source(getattr(pipeline, 'source', ''))
        }

    except Exception as e:
        print(f"⚠️ Erreur traitement pipeline ID {getattr(pipeline, 'id', 'N/A')}: {e}")
        return None


def _process_project_pipelines(project, limit_per_project: int) -> List[Dict[str, Any]]:
    """
    Traite les pipelines d'un projet

    Args:
        project: Projet GitLab
        limit_per_project: Limite de pipelines par projet

    Returns:
        Liste des données de pipelines
    """
    project_pipelines = []
    project_name = getattr(project, 'name', f'Project-{getattr(project, "id", "unknown")}')

    try:
        print(f"🔍 Traitement projet: {project_name}")

        # Récupérer les pipelines du projet (limités)
        pipelines = project.pipelines.list(per_page=limit_per_project, page=1)

        if not pipelines:
            print(f"   ℹ️ Aucun pipeline trouvé pour {project_name}")
            return project_pipelines

        print(f"   📊 {len(pipelines)} pipelines trouvés")

        for pipeline in pipelines:
            try:
                # Obtenir les détails complets du pipeline
                pipeline_detail = project.pipelines.get(pipeline.id, lazy=True)

                # Traiter les données du pipeline
                pipeline_data = _process_pipeline_data(pipeline_detail)

                if pipeline_data:
                    project_pipelines.append(pipeline_data)

            except Exception as pipeline_error:
                print(f"   ⚠️ Erreur pipeline {getattr(pipeline, 'id', 'N/A')}: {pipeline_error}")
                continue

    except Exception as project_error:
        print(f"   ❌ Erreur projet {project_name}: {project_error}")

    return project_pipelines


def extract_pipelines(gl_client: python_gitlab.Gitlab, project_ids: Optional[List[int]] = None,
                     limit_per_project: int = 50) -> pd.DataFrame:
    """
    Extrait les pipelines GitLab avec leurs métriques DevSecOps

    Args:
        gl_client: Client GitLab authentifié
        project_ids: Liste des IDs de projets (optionnel, sinon tous les projets)
        limit_per_project: Limite de pipelines par projet (défaut: 50)

    Returns:
        DataFrame avec les informations des pipelines
    """
    print("🔄 Extraction des pipelines GitLab...")

    pipelines_data = []
    processed_projects = 0

    try:
        # Récupérer les projets à traiter
        if project_ids:
            projects = [gl_client.projects.get(pid) for pid in project_ids]
        else:
            projects = gl_client.projects.list(all=True, archived=False)

        print(f"📊 {len(projects)} projets à traiter")

        for project in projects:
            project_pipelines = _process_project_pipelines(project, limit_per_project)
            pipelines_data.extend(project_pipelines)
            processed_projects += 1

        total_pipelines = len(pipelines_data)
        print(f"✅ {total_pipelines} pipelines extraits de {processed_projects} projets")

        # Créer et retourner le DataFrame
        df = pd.DataFrame(pipelines_data)

        # Trier par date de création (plus récent d'abord)
        if not df.empty and 'date_creation' in df.columns:
            df = df.sort_values('date_creation', ascending=False)
            df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des pipelines: {e}")
        return pd.DataFrame()


def extract_pipelines_by_project(gl_client: python_gitlab.Gitlab, project_id: int,
                                limit: int = 100) -> pd.DataFrame:
    """
    Extrait les pipelines d'un projet spécifique

    Args:
        gl_client: Client GitLab authentifié
        project_id: ID du projet GitLab
        limit: Nombre maximum de pipelines à extraire

    Returns:
        DataFrame avec les pipelines du projet
    """
    print(f"🔄 Extraction des pipelines du projet ID {project_id}...")

    try:
        project = gl_client.projects.get(project_id)
        project_name = getattr(project, 'name', f'Project-{project_id}')

        print(f"📊 Projet: {project_name}")

        # Utiliser la fonction principale avec un seul projet
        return extract_pipelines(gl_client, project_ids=[project_id], limit_per_project=limit)

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction du projet {project_id}: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    """Test de l'extracteur de pipelines"""
    import sys
    from pathlib import Path

    # Ajouter les chemins pour les imports
    current_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(current_dir))

    from client.gitlab_client import create_gitlab_client

    print("🧪 Test de l'extracteur de pipelines GitLab")
    print("=" * 60)

    try:
        # Créer le client GitLab
        gitlab_client = create_gitlab_client()
        gl = gitlab_client.connect()

        # Test 1: Extraction pipelines de tous les projets (limité)
        print("\n1️⃣ Extraction pipelines (échantillon) :")
        pipelines_sample = extract_pipelines(gl, limit_per_project=5)

        if not pipelines_sample.empty:
            print(f"   📊 {len(pipelines_sample)} pipelines extraits")
            print(f"   Colonnes: {', '.join(pipelines_sample.columns)}")

            # Statistiques rapides
            if 'statut' in pipelines_sample.columns:
                print(f"   États: {pipelines_sample['statut'].value_counts().to_dict()}")

            if 'environnement_cible' in pipelines_sample.columns:
                envs = pipelines_sample['environnement_cible'].value_counts().to_dict()
                print(f"   Environnements: {envs}")

            print("   Premiers pipelines:")
            for _, pipeline in pipelines_sample.head(3).iterrows():
                print(f"     - Pipeline #{pipeline.get('numero_pipeline', 'N/A')} "
                      f"({pipeline.get('statut', 'N/A')}) - "
                      f"Branche: {pipeline.get('ref_branche', 'N/A')}")

        gitlab_client.disconnect()

    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        sys.exit(1)

    print("\n🎉 Test terminé avec succès!")
