"""
Batch Processing Utilities for GitLab Extractors

Optimizes memory usage and API calls for large projects collections.
"""

import logging
from typing import Iterator, List, TypeVar, Generic, Callable, Any, Optional
from pathlib import Path
import pandas as pd
from tqdm import tqdm

T = TypeVar('T')


class BatchProcessor(Generic[T]):
    """
    Process large collections in manageable batches.
    
    Optimized for GitLab API calls and memory management.
    """
    
    def __init__(self, batch_size: int = 10, temp_dir: Optional[Path] = None):
        """
        Initialize batch processor.
        
        Args:
            batch_size: Number of items per batch (10 optimal for GitLab)
            temp_dir: Directory for temporary batch files
        """
        self.batch_size = batch_size
        self.temp_dir = temp_dir or Path("temp_batches")
        self.temp_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def create_batches(self, items: List[T]) -> Iterator[List[T]]:
        """
        Split items into batches.
        
        Args:
            items: List of items to batch
            
        Yields:
            Batches of items
        """
        for i in range(0, len(items), self.batch_size):
            yield items[i:i + self.batch_size]
    
    def process_with_progress(
        self, 
        items: List[T], 
        processor_func: Callable[[List[T]], pd.DataFrame],
        description: str = "Processing"
    ) -> pd.DataFrame:
        """
        Process items in batches with progress tracking.
        
        Args:
            items: Items to process
            processor_func: Function that processes a batch
            description: Progress bar description
            
        Returns:
            Combined DataFrame from all batches
        """
        all_dataframes = []
        failed_batches = []
        
        batches = list(self.create_batches(items))
        
        with tqdm(total=len(batches), desc=description, unit="batch") as pbar:
            for batch_idx, batch in enumerate(batches):
                try:
                    self.logger.info(f"Processing batch {batch_idx + 1}/{len(batches)}")
                    
                    # Process batch
                    batch_df = processor_func(batch)
                    
                    if not batch_df.empty:
                        all_dataframes.append(batch_df)
                        
                        # Save intermediate result (safety)
                        temp_file = self.temp_dir / f"batch_{batch_idx:03d}.xlsx"
                        batch_df.to_excel(temp_file, index=False)
                    
                    pbar.update(1)
                    pbar.set_postfix({
                        'Success': len(all_dataframes),
                        'Failed': len(failed_batches)
                    })
                    
                except Exception as e:
                    self.logger.error(f"Batch {batch_idx} failed: {e}")
                    failed_batches.append(batch_idx)
                    pbar.update(1)
                    continue
        
        # Log results
        success_rate = (len(batches) - len(failed_batches)) / len(batches) * 100
        self.logger.info(f"Batch processing completed: {success_rate:.1f}% success rate")
        
        if failed_batches:
            self.logger.warning(f"Failed batches: {failed_batches}")
        
        # Combine all successful batches
        if all_dataframes:
            result = pd.concat(all_dataframes, ignore_index=True)
            self.logger.info(f"Combined {len(all_dataframes)} batches into {len(result)} records")
            return result
        else:
            self.logger.warning("No successful batches to combine")
            return pd.DataFrame()
    
    def cleanup_temp_files(self):
        """Remove temporary batch files."""
        if self.temp_dir.exists():
            for temp_file in self.temp_dir.glob("batch_*.xlsx"):
                temp_file.unlink()
            self.logger.info("Cleaned up temporary batch files")


class GitLabBatchProcessor(BatchProcessor):
    """Specialized batch processor for GitLab API operations."""
    
    def __init__(self, batch_size: int = 10):
        """
        Initialize GitLab batch processor.
        
        Args:
            batch_size: Optimal for GitLab API (10 projects per batch)
        """
        super().__init__(batch_size=batch_size)
    
    def process_projects_batch(
        self, 
        project_ids: List[int],
        extractor_func: Callable[[List[int]], pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Process GitLab projects in optimized batches.
        
        Args:
            project_ids: List of GitLab project IDs
            extractor_func: Function that extracts data from projects
            
        Returns:
            Combined extraction results
        """
        def batch_processor(batch_project_ids: List[int]) -> pd.DataFrame:
            """Process a single batch of project IDs."""
            return extractor_func(batch_project_ids)
        
        return self.process_with_progress(
            items=project_ids,
            processor_func=batch_processor,
            description=f"🔄 GitLab Projects ({len(project_ids)} total)"
        )
