"""Video rendering service using FFmpeg"""
import logging
import os
import uuid
from typing import Dict, List, Optional
import ffmpeg
import asyncio
from pathlib import Path
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VideoRenderError(Exception):
    """Exception raised for video rendering errors"""
    pass


class VideoRenderer:
    """Render short-form videos using FFmpeg"""
    
    def __init__(self):
        self.video_storage_path = settings.video_storage_path
        self.temp_storage_path = settings.temp_storage_path
        Path(self.video_storage_path).mkdir(parents=True, exist_ok=True)
        Path(self.temp_storage_path).mkdir(parents=True, exist_ok=True)
    
    async def render_video(
        self,
        audio_path: str,
        image_paths: List[str],
        duration: int = 30,
        output_filename: Optional[str] = None,
        add_captions: bool = False,
        background_music_path: Optional[str] = None
    ) -> str:
        """Render video from audio and images
        
        Args:
            audio_path: Path to audio file
            image_paths: List of paths to images
            duration: Total video duration in seconds
            output_filename: Optional output filename
            add_captions: Whether to add captions
            background_music_path: Optional background music
            
        Returns:
            str: Path to rendered video file
        """
        try:
            if not output_filename:
                output_filename = f"video_{uuid.uuid4()}.mp4"
            
            output_path = os.path.join(self.video_storage_path, output_filename)
            
            # Calculate duration per image
            num_images = len(image_paths)
            if num_images == 0:
                raise VideoRenderError("No images provided for video rendering")
            
            duration_per_image = duration / num_images
            
            logger.info(f"Rendering video with {num_images} images, {duration}s duration")
            
            # Create video from images (slideshow)
            # For shorts: 1080x1920 (9:16)
            width, height = 1080, 1920
            
            # Create input list for FFmpeg
            inputs = []
            for img_path in image_paths:
                # Add each image with duration
                inputs.append(
                    ffmpeg.input(img_path, loop=1, t=duration_per_image)
                    .filter('scale', width, height, force_original_aspect_ratio='decrease')
                    .filter('pad', width, height, '(ow-iw)/2', '(oh-ih)/2')
                )
            
            # Concatenate all images
            video_stream = ffmpeg.concat(*inputs, v=1, a=0)
            
            # Add audio
            audio_stream = ffmpeg.input(audio_path)
            
            # Combine video and audio
            output = ffmpeg.output(
                video_stream,
                audio_stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                audio_bitrate='192k',
                video_bitrate='5000k',
                format='mp4',
                shortest=None,
                pix_fmt='yuv420p'
            ).overwrite_output()
            
            # Run FFmpeg command
            await asyncio.to_thread(output.run, quiet=False)
            
            logger.info(f"Video rendered successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Video rendering failed: {str(e)}")
            raise VideoRenderError(f"Video rendering failed: {str(e)}")
    
    async def add_captions_to_video(self, video_path: str, subtitles_path: str) -> str:
        """Add captions/subtitles to video
        
        Args:
            video_path: Path to video file
            subtitles_path: Path to subtitles file (SRT format)
            
        Returns:
            str: Path to video with captions
        """
        try:
            output_filename = f"video_captioned_{uuid.uuid4()}.mp4"
            output_path = os.path.join(self.video_storage_path, output_filename)
            
            # Add subtitles using FFmpeg
            video = ffmpeg.input(video_path)
            output = ffmpeg.output(
                video,
                output_path,
                vf=f"subtitles={subtitles_path}"
            ).overwrite_output()
            
            await asyncio.to_thread(output.run, quiet=False)
            
            logger.info(f"Captions added successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to add captions: {str(e)}")
            raise VideoRenderError(f"Failed to add captions: {str(e)}")
    
    def get_video_duration(self, video_path: str) -> float:
        """Get duration of video file in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            float: Duration in seconds
        """
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception as e:
            logger.error(f"Failed to get video duration: {str(e)}")
            return 0.0


# Singleton instance
_video_renderer: Optional[VideoRenderer] = None

def get_video_renderer() -> VideoRenderer:
    """Get VideoRenderer singleton instance"""
    global _video_renderer
    if _video_renderer is None:
        _video_renderer = VideoRenderer()
    return _video_renderer
