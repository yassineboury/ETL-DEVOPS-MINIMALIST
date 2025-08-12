#!/usr/bin/env python3
"""
Export GitLab Commits to Excel

Script to extract commits data from GitLab with comprehensive DevSecOps statistics
and export to Excel format with professional formatting.

Usage:
    python scripts/export_gitlab_commits.py

Features:
    - 33 comprehensive commit fields including statistics
    - GitLab user mapping with email correlation  
    - File type analysis and commit pattern detection
    - Change magnitude and complexity scoring
    - Professional Excel export with auto-formatting

Author: DevSecOps Team
Date: 2025-08-12
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gitlab_tools.client.gitlab_client import create_gitlab_client
from gitlab_tools.extractors.commits_extractor import CommitsExtractor
from gitlab_tools.exporters.excel_exporter import export_to_excel


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('gitlab_commits_export.log')
        ]
    )


def main():
    """Main execution function."""
    print("🚀 GitLab Commits Extractor with DevSecOps Analytics")
    print("=" * 60)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize GitLab client
        logger.info("Initializing GitLab client...")
        gitlab_client_wrapper = create_gitlab_client()
        gitlab_client = gitlab_client_wrapper.get_client()
        
        # Initialize commits extractor with batch processing
        logger.info("Initializing commits extractor with batch processing...")
        batch_size = int(os.getenv('BATCH_SIZE', '10'))  # Configurable batch size
        extractor = CommitsExtractor(gitlab_client, batch_size=batch_size)
        
        # Extract commits data with batch processing
        print(f"\n📊 Extracting commits with batch processing (batch_size: {batch_size})...")
        print("🎯 Optimized for 200+ projects with:")
        print("  • Git author/committer information")
        print("  • GitLab user mapping via email")
        print("  • Change statistics (additions, deletions, files)")
        print("  • File type analysis (code, config, docs, tests)")
        print("  • Commit pattern detection (hotfix, feature, refactor)")
        print("  • Change magnitude and complexity scoring")
        print("  • Memory-efficient batch processing")
        print("  • Progress tracking and error resilience")
        
        # Configure extraction parameters
        commits_df = extractor.extract_commits(
            max_commits=1000,  # Increased limit with batch processing
            use_batch_processing=True  # Enable batch processing
            # project_ids=[123, 456],  # Uncomment to filter specific projects
            # branch_name='main',  # Uncomment to filter by branch
            # since='2024-01-01T00:00:00Z',  # Uncomment to filter by date
        )
        
        if commits_df.empty:
            print("❌ No commits data found")
            return
        
        # Display extraction statistics
        print(f"\n✅ Successfully extracted {len(commits_df)} commits")
        print(f"📈 Data includes {len(commits_df.columns)} fields per commit")
        
        # Show some interesting statistics
        print("\n📊 Quick Statistics:")
        if not commits_df.empty:
            total_additions = commits_df['stats_additions'].sum()
            total_deletions = commits_df['stats_deletions'].sum()
            merge_commits = commits_df['is_merge_commit'].sum()
            hotfixes = commits_df['is_hotfix'].sum()
            features = commits_df['is_feature'].sum()
            
            print(f"  • Total lines added: {total_additions:,}")
            print(f"  • Total lines deleted: {total_deletions:,}")
            print(f"  • Merge commits: {merge_commits}")
            print(f"  • Hotfixes detected: {hotfixes}")
            print(f"  • Features detected: {features}")
            
            # Show change magnitude distribution
            magnitude_dist = commits_df['change_magnitude'].value_counts()
            print("  • Change magnitude distribution:")
            for magnitude, count in magnitude_dist.items():
                print(f"    - {magnitude}: {count} commits")
        
        # Export to Excel
        print("\n📁 Exporting to Excel...")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"gitlab_commits_export_{timestamp}.xlsx"
        
        export_to_excel(
            df=commits_df,
            filename=excel_filename,
            sheet_name="GitLab Commits Analytics"
        )
        
        print("✅ Export completed successfully!")
        print(f"📄 File saved: {excel_filename}")
        print(f"📊 Contains: {len(commits_df)} commits with {len(commits_df.columns)} fields each")
        
        # Show sample of extracted data
        print("\n🔍 Sample of extracted fields:")
        sample_fields = ['short_id', 'author_name', 'authored_date', 'stats_total', 
                        'change_magnitude', 'is_merge_commit', 'gitlab_username']
        if all(field in commits_df.columns for field in sample_fields):
            sample_df = commits_df[sample_fields].head(3)
            for _, row in sample_df.iterrows():
                print(f"  • {row['short_id']}: {row['author_name']} - {row['stats_total']} changes ({row['change_magnitude']})")
        
        print("\n🎯 DevSecOps Insights Available:")
        print("  • Developer productivity analysis")
        print("  • Code review complexity scoring") 
        print("  • Security hotfix tracking")
        print("  • Refactoring vs feature development balance")
        print("  • File type change patterns")
        
        logger.info(f"Commits extraction completed successfully: {len(commits_df)} records")
        
    except Exception as e:
        logger.error(f"Error during commits extraction: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
