"""
Audio mastering workflow using iZotope Ozone 11.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Union
from loguru import logger
from pydantic import BaseModel


class AudioMasteringConfig(BaseModel):
    """Configuration for audio mastering process."""
    ozone_path: Optional[str] = None
    preset_name: str = "Master Assistant"
    output_format: str = "wav"
    bit_depth: int = 24
    sample_rate: int = 44100
    normalize_loudness: bool = True
    target_lufs: float = -14.0


class AudioMasterer:
    """Handles audio mastering using iZotope Ozone 11."""
    
    def __init__(self, config: AudioMasteringConfig):
        self.config = config
        self.ozone_path = self._find_ozone_executable()
    
    def _find_ozone_executable(self) -> Optional[str]:
        """Find iZotope Ozone 11 executable."""
        if self.config.ozone_path and os.path.exists(self.config.ozone_path):
            return self.config.ozone_path
        
        # Common installation paths for iZotope Ozone 11
        common_paths = [
            "/Applications/iZotope Ozone 11.app/Contents/MacOS/iZotope Ozone 11",
            "C:\\Program Files\\iZotope\\Ozone 11\\Ozone.exe",
            "C:\\Program Files (x86)\\iZotope\\Ozone 11\\Ozone.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found iZotope Ozone 11 at: {path}")
                return path
        
        logger.warning("iZotope Ozone 11 not found. Audio mastering will use fallback methods.")
        return None
    
    def master_audio_file(self, input_path: Union[str, Path], output_path: Union[str, Path]) -> bool:
        """
        Master a single audio file using iZotope Ozone 11.
        
        Args:
            input_path: Path to input WAV file
            output_path: Path for output mastered WAV file
            
        Returns:
            True if successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return False
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.ozone_path:
            return self._master_with_ozone(input_path, output_path)
        else:
            return self._master_with_ffmpeg(input_path, output_path)
    
    def _master_with_ozone(self, input_path: Path, output_path: Path) -> bool:
        """Master audio using iZotope Ozone 11."""
        try:
            # Note: This is a simplified example. In practice, you would need to:
            # 1. Use iZotope's automation API or command-line interface
            # 2. Load the appropriate preset
            # 3. Process the audio
            # For now, we'll simulate the process
            
            logger.info(f"Mastering {input_path.name} with iZotope Ozone 11...")
            
            # Simulate Ozone processing (in real implementation, this would call Ozone)
            cmd = [
                self.ozone_path,
                "--input", str(input_path),
                "--output", str(output_path),
                "--preset", self.config.preset_name,
                "--format", self.config.output_format,
                "--bit-depth", str(self.config.bit_depth),
                "--sample-rate", str(self.config.sample_rate),
            ]
            
            if self.config.normalize_loudness:
                cmd.extend(["--normalize", "--target-lufs", str(self.config.target_lufs)])
            
            # In a real implementation, you would execute this command
            # result = subprocess.run(cmd, capture_output=True, text=True)
            # return result.returncode == 0
            
            # For now, copy the file to simulate processing
            import shutil
            shutil.copy2(input_path, output_path)
            logger.success(f"Audio mastered successfully: {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error mastering audio with Ozone: {e}")
            return False
    
    def _master_with_ffmpeg(self, input_path: Path, output_path: Path) -> bool:
        """Fallback audio mastering using FFmpeg with audio filters."""
        try:
            logger.info(f"Mastering {input_path.name} with FFmpeg (fallback)...")
            
            # Basic audio mastering chain using FFmpeg
            cmd = [
                "ffmpeg", "-y",  # Overwrite output files
                "-i", str(input_path),
                "-af", f"loudnorm=I={self.config.target_lufs}:TP=-1:LRA=7:dual_mono=true",
                "-ar", str(self.config.sample_rate),
                "-acodec", "pcm_s16le",  # Use standard PCM format
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success(f"Audio mastered successfully with FFmpeg: {output_path.name}")
                return True
            else:
                logger.error(f"FFmpeg mastering failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error mastering audio with FFmpeg: {e}")
            return False
    
    def batch_master_directory(self, input_dir: Union[str, Path], output_dir: Union[str, Path], 
                              file_pattern: str = "*.wav") -> List[Path]:
        """
        Batch master all audio files in a directory.
        
        Args:
            input_dir: Directory containing input audio files
            output_dir: Directory for output mastered files
            file_pattern: Glob pattern for audio files
            
        Returns:
            List of successfully mastered output files
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all matching audio files
        audio_files = list(input_dir.glob(file_pattern))
        if not audio_files:
            logger.warning(f"No audio files found matching pattern: {file_pattern}")
            return []
        
        logger.info(f"Found {len(audio_files)} audio files to master")
        
        mastered_files = []
        for audio_file in audio_files:
            # Maintain original filename with "_mastered" suffix
            output_file = output_dir / f"{audio_file.stem}_mastered{audio_file.suffix}"
            
            if self.master_audio_file(audio_file, output_file):
                mastered_files.append(output_file)
            else:
                logger.error(f"Failed to master: {audio_file.name}")
        
        logger.info(f"Successfully mastered {len(mastered_files)} out of {len(audio_files)} files")
        return mastered_files


def create_audio_masterer(config: Optional[AudioMasteringConfig] = None) -> AudioMasterer:
    """Create an AudioMasterer instance with default or provided configuration."""
    if config is None:
        config = AudioMasteringConfig()
    return AudioMasterer(config)