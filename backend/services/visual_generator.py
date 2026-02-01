"""Visual content generation service using OpenAI DALL-E and Gemini Imagen"""
import logging
from typing import List, Optional, Dict
import os
import uuid
import httpx
from pathlib import Path
import openai
import google.generativeai as genai
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure AI services
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key

if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


class VisualGenerationError(Exception):
    """Exception raised for visual generation errors"""
    pass


class VisualGenerator:
    """Generate images for short-form videos using AI"""
    
    def __init__(self):
        self.openai_available = bool(settings.openai_api_key)
        self.gemini_available = bool(settings.gemini_api_key)
        
        if not self.openai_available and not self.gemini_available:
            logger.warning("No AI API keys configured. Visual generation will fail.")
    
    def _create_image_prompt(self, script_data: Dict, niche: str, style: str = "realistic") -> str:
        """Create a prompt for image generation based on script"""
        
        hook = script_data.get('hook', '')
        body = script_data.get('body', '')
        
        style_descriptions = {
            "realistic": "photorealistic, high quality, detailed",
            "animated": "digital illustration, vibrant colors, cartoon style",
            "minimalist": "minimalist design, clean, simple, modern",
            "cinematic": "cinematic lighting, dramatic, movie-like quality"
        }
        
        style_desc = style_descriptions.get(style, "high quality")
        
        prompt = f"""
Create a visually striking image for a {niche} short-form video.

Script context: {hook} {body}

Style: {style_desc}

Requirements:
- Vertical format suitable for mobile (9:16 aspect ratio)
- Eye-catching and suitable for short-form content
- No text overlays
- Professional quality
- Engaging and attention-grabbing
"""
        return prompt.strip()
    
    async def generate_image_with_dalle(self, prompt: str) -> str:
        """Generate image using OpenAI DALL-E"""
        try:
            logger.info("Generating image with DALL-E...")
            
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",  # Closest to 9:16 aspect ratio
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download and save the image
            image_filename = f"visual_{uuid.uuid4()}.png"
            image_path = os.path.join(settings.image_storage_path, image_filename)
            
            # Ensure directory exists
            Path(settings.image_storage_path).mkdir(parents=True, exist_ok=True)
            
            # Download image
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url)
                img_response.raise_for_status()
                
                with open(image_path, "wb") as f:
                    f.write(img_response.content)
            
            logger.info(f"Image generated successfully with DALL-E: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"DALL-E image generation failed: {str(e)}")
            raise VisualGenerationError(f"DALL-E generation failed: {str(e)}")
    
    async def generate_image_with_gemini(self, prompt: str) -> str:
        """Generate image using Gemini Imagen (placeholder - requires Vertex AI setup)"""
        # Note: Gemini image generation requires Google Cloud Vertex AI setup
        # This is a placeholder for future implementation
        raise VisualGenerationError("Gemini image generation not yet implemented. Please use DALL-E.")
    
    async def generate_visuals(self, script_data: Dict, niche: str, count: int = 3, style: str = "realistic") -> List[str]:
        """Generate multiple images for a video
        
        Args:
            script_data: Dictionary containing script (hook, body, ending)
            niche: Content niche
            count: Number of images to generate
            style: Visual style (realistic, animated, minimalist, cinematic)
        
        Returns:
            List[str]: List of file paths to generated images
        """
        
        if count < 1 or count > 5:
            raise VisualGenerationError("Count must be between 1 and 5")
        
        image_paths = []
        
        # Generate base prompt
        base_prompt = self._create_image_prompt(script_data, niche, style)
        
        # Generate images (currently one at a time with DALL-E)
        try:
            if self.openai_available:
                # For multiple images, we'll generate them sequentially
                for i in range(count):
                    # Add variation to each prompt
                    variation_prompt = f"{base_prompt}\n\nImage {i+1} of {count}: Focus on a different aspect or angle."
                    image_path = await self.generate_image_with_dalle(variation_prompt)
                    image_paths.append(image_path)
            else:
                raise VisualGenerationError("No AI service available for image generation")
            
            logger.info(f"Generated {len(image_paths)} images successfully")
            return image_paths
            
        except Exception as e:
            logger.error(f"Visual generation failed: {str(e)}")
            # If some images were generated, return those
            if image_paths:
                logger.warning(f"Partial success: {len(image_paths)} images generated")
                return image_paths
            raise VisualGenerationError(f"Visual generation failed: {str(e)}")
    
    async def generate_single_visual(self, script_data: Dict, niche: str, style: str = "realistic") -> str:
        """Generate a single image for quick testing
        
        Args:
            script_data: Dictionary containing script
            niche: Content niche
            style: Visual style
        
        Returns:
            str: File path to generated image
        """
        images = await self.generate_visuals(script_data, niche, count=1, style=style)
        return images[0] if images else None


# Singleton instance
_visual_generator: Optional[VisualGenerator] = None

def get_visual_generator() -> VisualGenerator:
    """Get VisualGenerator singleton instance"""
    global _visual_generator
    if _visual_generator is None:
        _visual_generator = VisualGenerator()
    return _visual_generator
