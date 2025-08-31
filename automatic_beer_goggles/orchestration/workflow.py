"""
Orchestration system for batch processing audio-video workflows.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from loguru import logger
from pydantic import BaseModel

from automatic_beer_goggles.config.platforms import get_platform_config, list_supported_platforms, PlatformConfig
from automatic_beer_goggles.audio.mastering import AudioMasterer, AudioMasteringConfig
from automatic_beer_goggles.video.generation import VideoGenerator, VideoGenerationConfig


@dataclass
class ProcessingJob:
    """Represents a single processing job."""
    job_id: str
    audio_file: Path
    image_file: Path
    platforms: List[str]
    status: str = "pending"  # pending, processing, completed, failed
    output_files: Dict[str, Optional[Path]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = {}


class WorkflowConfig(BaseModel):
    """Configuration for the orchestration workflow."""
    max_concurrent_jobs: int = 4
    audio_mastering: AudioMasteringConfig = AudioMasteringConfig()
    video_generation: VideoGenerationConfig = VideoGenerationConfig()
    output_base_dir: str = "./output"
    log_file: Optional[str] = None
    resume_on_failure: bool = True


class WorkflowOrchestrator:
    """Orchestrates the complete audio mastering and video generation workflow."""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.jobs: List[ProcessingJob] = []
        self.audio_masterer = AudioMasterer(config.audio_mastering)
        self.video_generator = VideoGenerator(config.video_generation)
        
        # Setup directories
        self.output_dir = Path(config.output_base_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.mastered_audio_dir = self.output_dir / "mastered_audio"
        self.mastered_audio_dir.mkdir(parents=True, exist_ok=True)
        
        self.videos_dir = self.output_dir / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        if config.log_file:
            logger.add(config.log_file, rotation="10 MB", retention="30 days")
    
    def add_job(self, audio_file: Union[str, Path], image_file: Union[str, Path], 
                platforms: List[str], job_id: Optional[str] = None) -> ProcessingJob:
        """
        Add a new processing job to the queue.
        
        Args:
            audio_file: Path to source audio file
            image_file: Path to source PNG image
            platforms: List of target platforms
            job_id: Optional custom job ID
            
        Returns:
            Created ProcessingJob instance
        """
        audio_path = Path(audio_file)
        image_path = Path(image_file)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Validate platforms
        supported_platforms = list_supported_platforms()
        invalid_platforms = [p for p in platforms if p.lower() not in supported_platforms]
        if invalid_platforms:
            raise ValueError(f"Unsupported platforms: {invalid_platforms}")
        
        if job_id is None:
            job_id = f"{audio_path.stem}_{len(self.jobs)}"
        
        job = ProcessingJob(
            job_id=job_id,
            audio_file=audio_path,
            image_file=image_path,
            platforms=[p.lower() for p in platforms]
        )
        
        self.jobs.append(job)
        logger.info(f"Added job {job_id}: {audio_path.name} -> {platforms}")
        return job
    
    def add_batch_jobs(self, audio_dir: Union[str, Path], image_file: Union[str, Path],
                      platforms: List[str], audio_pattern: str = "*.wav") -> List[ProcessingJob]:
        """
        Add multiple jobs from a directory of audio files.
        
        Args:
            audio_dir: Directory containing audio files
            image_file: Single image file to use for all videos
            platforms: List of target platforms
            audio_pattern: Glob pattern for audio files
            
        Returns:
            List of created ProcessingJob instances
        """
        audio_dir = Path(audio_dir)
        image_path = Path(image_file)
        
        if not audio_dir.exists():
            raise FileNotFoundError(f"Audio directory not found: {audio_dir}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        audio_files = list(audio_dir.glob(audio_pattern))
        if not audio_files:
            logger.warning(f"No audio files found in {audio_dir} matching {audio_pattern}")
            return []
        
        jobs = []
        for audio_file in audio_files:
            job = self.add_job(audio_file, image_path, platforms)
            jobs.append(job)
        
        logger.info(f"Added {len(jobs)} batch jobs from {audio_dir}")
        return jobs
    
    def _process_single_job(self, job: ProcessingJob) -> ProcessingJob:
        """Process a single job through the complete workflow."""
        try:
            logger.info(f"Processing job {job.job_id}")
            job.status = "processing"
            
            # Step 1: Master the audio
            mastered_audio_path = self.mastered_audio_dir / f"{job.audio_file.stem}_mastered.wav"
            
            if not mastered_audio_path.exists() or not self.config.resume_on_failure:
                success = self.audio_masterer.master_audio_file(job.audio_file, mastered_audio_path)
                if not success:
                    job.status = "failed"
                    job.error_message = "Audio mastering failed"
                    return job
            
            # Step 2: Generate videos for each platform
            platform_configs = [get_platform_config(platform) for platform in job.platforms]
            
            video_results = self.video_generator.create_multi_platform_videos(
                image_path=job.image_file,
                audio_path=mastered_audio_path,
                output_dir=self.videos_dir / job.job_id,
                platforms=platform_configs,
                base_filename=job.job_id
            )
            
            # Update job with results
            job.output_files = {k: str(v) if v else None for k, v in video_results.items()}
            
            # Check if all videos were created successfully
            failed_videos = [k for k, v in video_results.items() if v is None]
            if failed_videos:
                job.status = "failed"
                job.error_message = f"Failed to create videos: {failed_videos}"
            else:
                job.status = "completed"
                logger.success(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            logger.error(f"Job {job.job_id} failed: {e}")
        
        return job
    
    def process_all_jobs(self) -> Dict[str, int]:
        """
        Process all jobs in the queue using parallel execution.
        
        Returns:
            Dictionary with job status counts
        """
        if not self.jobs:
            logger.warning("No jobs to process")
            return {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
        
        logger.info(f"Processing {len(self.jobs)} jobs with max {self.config.max_concurrent_jobs} concurrent workers")
        
        # Filter jobs that need processing
        jobs_to_process = [job for job in self.jobs if job.status == "pending"]
        
        if not jobs_to_process:
            logger.info("No pending jobs to process")
        else:
            # Process jobs concurrently
            with ThreadPoolExecutor(max_workers=self.config.max_concurrent_jobs) as executor:
                # Submit all jobs
                future_to_job = {executor.submit(self._process_single_job, job): job 
                               for job in jobs_to_process}
                
                # Collect results as they complete
                for future in as_completed(future_to_job):
                    job = future_to_job[future]
                    try:
                        updated_job = future.result()
                        # Update the job in our list
                        job_index = self.jobs.index(job)
                        self.jobs[job_index] = updated_job
                    except Exception as e:
                        logger.error(f"Unexpected error processing job {job.job_id}: {e}")
                        job.status = "failed"
                        job.error_message = f"Unexpected error: {e}"
        
        # Generate status summary
        status_counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
        for job in self.jobs:
            status_counts[job.status] += 1
        
        logger.info(f"Processing summary: {status_counts}")
        return status_counts
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get status of a specific job."""
        for job in self.jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_failed_jobs(self) -> List[ProcessingJob]:
        """Get list of failed jobs."""
        return [job for job in self.jobs if job.status == "failed"]
    
    def retry_failed_jobs(self) -> Dict[str, int]:
        """Retry all failed jobs."""
        failed_jobs = self.get_failed_jobs()
        for job in failed_jobs:
            job.status = "pending"
            job.error_message = None
        
        logger.info(f"Retrying {len(failed_jobs)} failed jobs")
        return self.process_all_jobs()
    
    def export_job_report(self, output_file: Union[str, Path]) -> None:
        """Export job processing report to JSON file."""
        output_path = Path(output_file)
        
        report = {
            "workflow_config": {
                "max_concurrent_jobs": self.config.max_concurrent_jobs,
                "output_base_dir": self.config.output_base_dir,
                "audio_mastering": self.config.audio_mastering.dict(),
                "video_generation": self.config.video_generation.dict(),
            },
            "jobs": [asdict(job) for job in self.jobs],
            "summary": {
                "total_jobs": len(self.jobs),
                "completed": len([j for j in self.jobs if j.status == "completed"]),
                "failed": len([j for j in self.jobs if j.status == "failed"]),
                "pending": len([j for j in self.jobs if j.status == "pending"]),
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Job report exported to: {output_path}")
    
    def clear_jobs(self) -> None:
        """Clear all jobs from the queue."""
        self.jobs.clear()
        logger.info("All jobs cleared from queue")


def create_workflow_orchestrator(config: Optional[WorkflowConfig] = None) -> WorkflowOrchestrator:
    """Create a WorkflowOrchestrator instance with default or provided configuration."""
    if config is None:
        config = WorkflowConfig()
    return WorkflowOrchestrator(config)