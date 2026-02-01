"""Content generation service using OpenAI and Gemini AI via Emergent Integration"""
import logging
from typing import Dict, Optional
import uuid
from emergentintegrations.llm.chat import LlmChat, UserMessage
from config.settings import get_settings
from config.constants import NICHES

logger = logging.getLogger(__name__)
settings = get_settings()


class ContentGenerationError(Exception):
    """Exception raised for content generation errors"""
    pass


class ContentGenerator:
    """Generate viral short-form video scripts using AI"""
    
    def __init__(self):
        self.emergent_key = settings.emergent_llm_key if hasattr(settings, 'emergent_llm_key') else None
        self.openai_available = bool(self.emergent_key)
        
        if not self.openai_available:
            logger.warning("No Emergent LLM key configured. Content generation will fail.")
    
    def _create_prompt(self, platform: str, niche: str, language: str, duration: int) -> str:
        """Create a detailed prompt for script generation"""
        
        niche_prompts = {
            "motivation": "Create an inspiring and motivational message that energizes viewers",
            "facts": "Share a surprising and interesting fact that makes viewers think 'wow'",
            "stories": "Tell a captivating micro-story with a twist or emotional impact",
            "cute_animals": "Describe adorable animal moments that make people smile",
            "tech_tips": "Share a useful tech tip or hack that solves a common problem",
            "fitness": "Give a quick fitness tip or workout motivation",
            "cooking": "Share a quick cooking tip or recipe idea",
            "travel": "Describe an amazing travel destination or travel tip",
            "business": "Share actionable business advice or success insight",
            "finance": "Give practical financial advice or money-saving tip",
            "gaming": "Share gaming tips, tricks, or interesting gaming facts",
            "education": "Teach something interesting and valuable in simple terms",
            "entertainment": "Share entertaining content that makes people laugh or amazed",
            "health": "Give practical health advice or wellness tip",
            "fashion": "Share fashion tips or style advice",
            "lifestyle": "Share lifestyle tips that improve daily life"
        }
        
        niche_description = niche_prompts.get(niche, "Create engaging content")
        
        prompt = f"""
You are an expert viral short-form video script writer for {platform}. 

Create a {duration}-second video script in {language} for the niche: {niche}.

{niche_description}.

IMPORTANT REQUIREMENTS:
1. HOOK (0-2 seconds): Start with a powerful, curiosity-inducing hook that stops scrolling
2. BODY (middle section): Deliver the main content clearly and engagingly
3. LOOP ENDING: End with a statement that makes viewers want to watch again or check comments
4. Keep it conversational and natural
5. Use simple, punchy language
6. Make it suitable for voiceover (no complex words)

Provide the output in this EXACT JSON format:
{{
    "hook": "The opening hook line (1-2 sentences)",
    "body": "The main content (2-4 sentences)",
    "ending": "The loop ending that encourages rewatching (1 sentence)",
    "title": "Catchy video title (5-8 words)",
    "description": "Engaging video description (1-2 sentences)",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"]
}}

Generate the script now:
"""
        return prompt
    
    async def generate_script_with_emergent(self, platform: str, niche: str, language: str, duration: int) -> Dict:
        """Generate script using Emergent LLM integration"""
        try:
            prompt = self._create_prompt(platform, niche, language, duration)
            
            # Initialize LLM chat with Emergent key
            chat = LlmChat(
                api_key=self.emergent_key,
                session_id=f"script_gen_{uuid.uuid4()}",
                system_message="You are an expert viral short-form video script writer. Always respond with valid JSON only, no additional text."
            ).with_model("openai", "gpt-5.2")
            
            # Create user message
            user_message = UserMessage(text=prompt)
            
            # Get response
            response = await chat.send_message(user_message)
            content = response.strip()
            
            # Extract JSON from response
            import json
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            script_data = json.loads(content)
            
            logger.info(f"Successfully generated script with Emergent LLM for niche: {niche}")
            return script_data
            
        except Exception as e:
            logger.error(f"Emergent LLM script generation failed: {str(e)}")
            raise ContentGenerationError(f"Script generation failed: {str(e)}")
    
    async def generate_script(self, platform: str, niche: str, language: str = "English", duration: int = 30) -> Dict:
        """Generate script using Emergent LLM"""
        
        # Validate inputs
        if niche not in NICHES:
            raise ContentGenerationError(f"Invalid niche: {niche}. Must be one of {NICHES}")
        
        if duration < 10 or duration > 60:
            raise ContentGenerationError("Duration must be between 10 and 60 seconds")
        
        if not self.openai_available:
            raise ContentGenerationError("No Emergent LLM key configured")
        
        return await self.generate_script_with_emergent(platform, niche, language, duration)


# Singleton instance
_content_generator: Optional[ContentGenerator] = None

def get_content_generator() -> ContentGenerator:
    """Get ContentGenerator singleton instance"""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator
