"""
Command-line interface for Automatic Beer Goggles.
"""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from loguru import logger

from automatic_beer_goggles.config.platforms import list_supported_platforms, get_platform_config
from automatic_beer_goggles.audio.mastering import AudioMasteringConfig, create_audio_masterer
from automatic_beer_goggles.video.generation import VideoGenerationConfig, create_video_generator
from automatic_beer_goggles.orchestration.workflow import WorkflowConfig, create_workflow_orchestrator
from automatic_beer_goggles.utils.file_utils import (
    validate_audio_file, validate_image_file, find_audio_files,
    check_dependencies, get_system_info, format_file_size
)

console = Console()


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    
    # Console logging
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                                             "<level>{level: <8}</level> | "
                                             "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                                             "<level>{message}</level>")
    
    # File logging
    if log_file:
        logger.add(log_file, level="DEBUG", rotation="10 MB", retention="30 days")


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', type=str, help='Log file path')
@click.pass_context
def main(ctx, verbose: bool, log_file: Optional[str]):
    """Automatic Beer Goggles - Automated mastered audio-image video creation for social media platforms."""
    ctx.ensure_object(dict)
    setup_logging(verbose, log_file)
    ctx.obj['verbose'] = verbose
    ctx.obj['log_file'] = log_file


@main.command()
def info():
    """Display system information and check dependencies."""
    console.print(Panel.fit("🍺 Automatic Beer Goggles - System Information", style="bold green"))
    
    # System info
    system_info = get_system_info()
    
    system_table = Table(title="System Information")
    system_table.add_column("Property", style="cyan")
    system_table.add_column("Value", style="white")
    
    for key, value in system_info.items():
        system_table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(system_table)
    console.print()
    
    # Dependencies
    deps = check_dependencies()
    
    deps_table = Table(title="Dependencies")
    deps_table.add_column("Dependency", style="cyan")
    deps_table.add_column("Status", style="white")
    
    for dep, available in deps.items():
        status = "✅ Available" if available else "❌ Missing"
        style = "green" if available else "red"
        deps_table.add_row(dep, f"[{style}]{status}[/{style}]")
    
    console.print(deps_table)
    console.print()
    
    # Supported platforms
    platforms = list_supported_platforms()
    
    platforms_table = Table(title="Supported Platforms")
    platforms_table.add_column("Platform", style="cyan")
    platforms_table.add_column("Aspect Ratios", style="white")
    platforms_table.add_column("Max Duration", style="white")
    platforms_table.add_column("Max File Size", style="white")
    
    for platform in platforms:
        config = get_platform_config(platform)
        ratios = ", ".join([ar.value for ar in config.aspect_ratios])
        duration = f"{config.max_duration_seconds // 60}m {config.max_duration_seconds % 60}s"
        file_size = format_file_size(config.max_file_size_mb * 1024 * 1024)
        platforms_table.add_row(config.name, ratios, duration, file_size)
    
    console.print(platforms_table)


@main.command()
@click.argument('audio_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--preset', default='Master Assistant', help='iZotope Ozone preset name')
@click.option('--target-lufs', default=-14.0, type=float, help='Target LUFS for normalization')
@click.option('--ozone-path', type=str, help='Path to iZotope Ozone executable')
def master_audio(audio_file: Path, output_file: Path, preset: str, 
                target_lufs: float, ozone_path: Optional[str]):
    """Master a single audio file using iZotope Ozone 11."""
    
    if not validate_audio_file(audio_file):
        console.print(f"[red]Error: Invalid audio file: {audio_file}[/red]")
        sys.exit(1)
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup mastering configuration
    config = AudioMasteringConfig(
        preset_name=preset,
        target_lufs=target_lufs,
        ozone_path=ozone_path
    )
    
    masterer = create_audio_masterer(config)
    
    with console.status(f"[bold green]Mastering {audio_file.name}..."):
        success = masterer.master_audio_file(audio_file, output_file)
    
    if success:
        file_size = format_file_size(output_file.stat().st_size)
        console.print(f"[green]✅ Audio mastered successfully: {output_file} ({file_size})[/green]")
    else:
        console.print(f"[red]❌ Audio mastering failed[/red]")
        sys.exit(1)


@main.command()
@click.argument('image_file', type=click.Path(exists=True, path_type=Path))
@click.argument('audio_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--platform', required=True, type=click.Choice(list_supported_platforms()), 
              help='Target social media platform')
@click.option('--aspect-ratio', type=str, help='Aspect ratio (e.g., 16:9, 1:1, 9:16)')
@click.option('--video-bitrate', type=str, help='Video bitrate (e.g., 2M)')
@click.option('--audio-bitrate', default='128k', help='Audio bitrate')
@click.option('--fps', default=30, type=int, help='Frames per second')
def create_video(image_file: Path, audio_file: Path, output_file: Path,
                platform: str, aspect_ratio: Optional[str], video_bitrate: Optional[str],
                audio_bitrate: str, fps: int):
    """Create a video from image and audio for a specific platform."""
    
    if not validate_image_file(image_file):
        console.print(f"[red]Error: Invalid image file: {image_file}[/red]")
        sys.exit(1)
    
    if not validate_audio_file(audio_file):
        console.print(f"[red]Error: Invalid audio file: {audio_file}[/red]")
        sys.exit(1)
    
    # Get platform configuration
    platform_config = get_platform_config(platform)
    
    # Validate aspect ratio
    if aspect_ratio:
        from automatic_beer_goggles.config.platforms import AspectRatio
        try:
            aspect_ratio_enum = AspectRatio(aspect_ratio)
            if aspect_ratio_enum not in platform_config.aspect_ratios:
                console.print(f"[red]Error: Aspect ratio {aspect_ratio} not supported by {platform}[/red]")
                sys.exit(1)
        except ValueError:
            console.print(f"[red]Error: Invalid aspect ratio format: {aspect_ratio}[/red]")
            sys.exit(1)
    else:
        aspect_ratio_enum = platform_config.aspect_ratios[0]  # Use first supported ratio
    
    # Create output directory
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Setup video generation configuration
    config = VideoGenerationConfig(
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        fps=fps
    )
    
    generator = create_video_generator(config)
    
    with console.status(f"[bold green]Creating {platform} video..."):
        success = generator.create_video(
            image_path=image_file,
            audio_path=audio_file,
            output_path=output_file,
            platform_config=platform_config,
            aspect_ratio=aspect_ratio_enum
        )
    
    if success:
        file_size = format_file_size(output_file.stat().st_size)
        console.print(f"[green]✅ Video created successfully: {output_file} ({file_size})[/green]")
    else:
        console.print(f"[red]❌ Video creation failed[/red]")
        sys.exit(1)


@main.command()
@click.argument('audio_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('image_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_dir', type=click.Path(path_type=Path))
@click.option('--platforms', '-p', multiple=True, required=True,
              type=click.Choice(list_supported_platforms()), 
              help='Target platforms (can be specified multiple times)')
@click.option('--audio-pattern', default='*.wav', help='Audio file pattern')
@click.option('--max-jobs', default=4, type=int, help='Maximum concurrent jobs')
@click.option('--resume', is_flag=True, help='Resume from previous run')
@click.option('--report-file', type=str, help='Export job report to file')
def batch_process(audio_dir: Path, image_file: Path, output_dir: Path,
                 platforms: List[str], audio_pattern: str, max_jobs: int,
                 resume: bool, report_file: Optional[str]):
    """Batch process multiple audio files into videos for multiple platforms."""
    
    if not validate_image_file(image_file):
        console.print(f"[red]Error: Invalid image file: {image_file}[/red]")
        sys.exit(1)
    
    # Find audio files
    audio_files = find_audio_files(audio_dir, [audio_pattern])
    if not audio_files:
        console.print(f"[red]Error: No audio files found in {audio_dir} matching {audio_pattern}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Found {len(audio_files)} audio files to process[/cyan]")
    
    # Setup workflow configuration
    config = WorkflowConfig(
        max_concurrent_jobs=max_jobs,
        output_base_dir=str(output_dir),
        resume_on_failure=resume
    )
    
    orchestrator = create_workflow_orchestrator(config)
    
    # Add batch jobs
    jobs = orchestrator.add_batch_jobs(audio_dir, image_file, list(platforms), audio_pattern)
    
    console.print(f"[cyan]Added {len(jobs)} processing jobs for platforms: {', '.join(platforms)}[/cyan]")
    
    # Process all jobs
    with Progress() as progress:
        task = progress.add_task("[green]Processing jobs...", total=len(jobs))
        
        # Run the batch processing
        status_counts = orchestrator.process_all_jobs()
        progress.update(task, completed=len(jobs))
    
    # Display results
    results_table = Table(title="Processing Results")
    results_table.add_column("Status", style="cyan")
    results_table.add_column("Count", style="white")
    
    for status, count in status_counts.items():
        if count > 0:
            style = "green" if status == "completed" else "red" if status == "failed" else "yellow"
            results_table.add_row(status.title(), f"[{style}]{count}[/{style}]")
    
    console.print(results_table)
    
    # Show failed jobs if any
    failed_jobs = orchestrator.get_failed_jobs()
    if failed_jobs:
        console.print(f"\n[red]Failed jobs ({len(failed_jobs)}):[/red]")
        for job in failed_jobs:
            console.print(f"  • {job.job_id}: {job.error_message}")
    
    # Export report if requested
    if report_file:
        orchestrator.export_job_report(report_file)
        console.print(f"[cyan]Report exported to: {report_file}[/cyan]")
    
    # Exit with error code if there were failures
    if status_counts.get("failed", 0) > 0:
        sys.exit(1)


@main.command()
@click.argument('audio_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument('output_dir', type=click.Path(path_type=Path))
@click.option('--audio-pattern', default='*.wav', help='Audio file pattern')
@click.option('--preset', default='Master Assistant', help='iZotope Ozone preset name')
@click.option('--target-lufs', default=-14.0, type=float, help='Target LUFS for normalization')
@click.option('--ozone-path', type=str, help='Path to iZotope Ozone executable')
def batch_master(audio_dir: Path, output_dir: Path, audio_pattern: str,
                preset: str, target_lufs: float, ozone_path: Optional[str]):
    """Batch master multiple audio files."""
    
    # Find audio files
    audio_files = find_audio_files(audio_dir, [audio_pattern])
    if not audio_files:
        console.print(f"[red]Error: No audio files found in {audio_dir} matching {audio_pattern}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Found {len(audio_files)} audio files to master[/cyan]")
    
    # Setup mastering configuration
    config = AudioMasteringConfig(
        preset_name=preset,
        target_lufs=target_lufs,
        ozone_path=ozone_path
    )
    
    masterer = create_audio_masterer(config)
    
    # Process files
    with Progress() as progress:
        task = progress.add_task("[green]Mastering audio files...", total=len(audio_files))
        
        mastered_files = masterer.batch_master_directory(audio_dir, output_dir, audio_pattern)
        progress.update(task, completed=len(audio_files))
    
    console.print(f"[green]✅ Successfully mastered {len(mastered_files)} out of {len(audio_files)} files[/green]")
    
    if len(mastered_files) < len(audio_files):
        console.print(f"[yellow]⚠️  {len(audio_files) - len(mastered_files)} files failed to process[/yellow]")
        sys.exit(1)


if __name__ == '__main__':
    main()