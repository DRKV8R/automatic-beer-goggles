#!/usr/bin/env python3
"""
Example script: Batch processing multiple audio files
"""

import sys
from pathlib import Path

# Add the project root to Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from automatic_beer_goggles.orchestration.workflow import WorkflowConfig, create_workflow_orchestrator
from automatic_beer_goggles.audio.mastering import AudioMasteringConfig
from automatic_beer_goggles.video.generation import VideoGenerationConfig
from loguru import logger


def main():
    """Example of batch processing workflow."""
    
    # Setup logging
    logger.add(sys.stderr, level="INFO")
    logger.add("batch_processing.log", rotation="10 MB")
    
    # Configuration
    audio_directory = Path("input/audio_files")
    brand_image = Path("input/brand_image.png")
    output_directory = Path("output/batch_process")
    
    # Target platforms
    target_platforms = ["youtube", "instagram", "tiktok", "twitter"]
    
    # Check if input paths exist
    if not audio_directory.exists():
        logger.error(f"Audio directory not found: {audio_directory}")
        return 1
    
    if not brand_image.exists():
        logger.error(f"Brand image not found: {brand_image}")
        return 1
    
    # Create output directory
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # Configure the workflow
    workflow_config = WorkflowConfig(
        max_concurrent_jobs=4,  # Adjust based on your system
        audio_mastering=AudioMasteringConfig(
            target_lufs=-14.0,
            normalize_loudness=True
        ),
        video_generation=VideoGenerationConfig(
            fps=30,
            audio_bitrate="128k",
            use_gpu_acceleration=True
        ),
        output_base_dir=str(output_directory),
        resume_on_failure=True,
        log_file="workflow.log"
    )
    
    # Create orchestrator
    orchestrator = create_workflow_orchestrator(workflow_config)
    
    # Add batch jobs
    logger.info(f"Adding batch jobs for audio files in {audio_directory}")
    jobs = orchestrator.add_batch_jobs(
        audio_dir=audio_directory,
        image_file=brand_image,
        platforms=target_platforms,
        audio_pattern="*.wav"
    )
    
    if not jobs:
        logger.error("No jobs were added. Check your audio directory and file patterns.")
        return 1
    
    logger.info(f"Added {len(jobs)} jobs for processing")
    
    # Process all jobs
    logger.info("Starting batch processing...")
    status_counts = orchestrator.process_all_jobs()
    
    # Report results
    logger.info("Batch processing completed!")
    logger.info(f"Results: {status_counts}")
    
    # Show failed jobs if any
    failed_jobs = orchestrator.get_failed_jobs()
    if failed_jobs:
        logger.warning(f"Failed jobs ({len(failed_jobs)}):")
        for job in failed_jobs:
            logger.warning(f"  - {job.job_id}: {job.error_message}")
        
        # Optionally retry failed jobs
        retry_choice = input("Retry failed jobs? (y/n): ").lower().strip()
        if retry_choice == 'y':
            logger.info("Retrying failed jobs...")
            retry_results = orchestrator.retry_failed_jobs()
            logger.info(f"Retry results: {retry_results}")
    
    # Export processing report
    report_file = output_directory / "processing_report.json"
    orchestrator.export_job_report(report_file)
    logger.info(f"Processing report saved to: {report_file}")
    
    # Return exit code based on results
    if status_counts.get("failed", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())