"""Visual content generation service using OpenAI DALL-E and Gemini Nano Banana"""
import logging
from typing import List, Optional, Dict
import os
import uuid
import httpx
import base64
from pathlib import Path
import openai
from emergentintegrations.llm.chat import LlmChat, UserMessage
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Configure OpenAI
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key


class VisualGenerationError(Exception):
    """Exception raised for visual generation errors"""
    pass


class VisualGenerator:
    """Generate images for short-form videos using AI"""
    
    def __init__(self):
        self.openai_available = bool(settings.openai_api_key)
        self.emergent_key = settings.emergent_llm_key if hasattr(settings, 'emergent_llm_key') else None
        self.gemini_available = bool(self.emergent_key) or bool(settings.gemini_api_key)
        
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
        """Generate image using Gemini Nano Banana"""
        try:
            logger.info("Generating image with Gemini Nano Banana...")
            
            # Use Emergent LLM key for Gemini Nano Banana
            api_key = self.emergent_key or settings.gemini_api_key
            
            # Initialize chat with Gemini Nano Banana model
            chat = LlmChat(
                api_key=api_key,
                session_id=f"visual_gen_{uuid.uuid4()}",
                system_message="You are an expert image generator creating high-quality visuals for short-form video content."
            ).with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
            
            # Create user message with prompt
            msg = UserMessage(text=prompt)
            
            # Generate image and get response
            text, images = await chat.send_message_multimodal_response(msg)
            
            if not images or len(images) == 0:
                raise VisualGenerationError("Gemini did not return any images")
            
            # Get the first generated image
            image_data = images[0]
            
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data['data'])
            
            # Generate filename and save
            image_filename = f"visual_{uuid.uuid4()}.png"
            image_path = os.path.join(settings.image_storage_path, image_filename)
            
            # Ensure directory exists
            Path(settings.image_storage_path).mkdir(parents=True, exist_ok=True)
            
            # Save image
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"Image generated successfully with Gemini Nano Banana: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Gemini Nano Banana image generation failed: {str(e)}")
            raise VisualGenerationError(f"Gemini generation failed: {str(e)}")
    
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
        
        # Try Gemini Nano Banana first (if available), then OpenAI DALL-E
        try:
            if self.gemini_available:
                logger.info("Using Gemini Nano Banana for image generation")
                # For multiple images, generate them sequentially
                for i in range(count):
                    # Add variation to each prompt
                    variation_prompt = f"{base_prompt}\n\nImage {i+1} of {count}: Focus on a different aspect or angle of the scene."
                    try:
                        image_path = await self.generate_image_with_gemini(variation_prompt)
                        image_paths.append(image_path)
                    except Exception as e:
                        logger.warning(f"Gemini generation failed for image {i+1}: {str(e)}")
                        # If Gemini fails, try DALL-E as fallback
                        if self.openai_available:
                            logger.info("Falling back to DALL-E for remaining images")
                            image_path = await self.generate_image_with_dalle(variation_prompt)
                            image_paths.append(image_path)
                        else:
                            raise
            
            elif self.openai_available:
                logger.info("Using OpenAI DALL-E for image generation")
                # For multiple images, generate them sequentially with DALL-E
                for i in range(count):
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