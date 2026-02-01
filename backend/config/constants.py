# Available niches for content generation
NICHES = [
    "motivation",
    "facts",
    "stories",
    "cute_animals",
    "tech_tips",
    "fitness",
    "cooking",
    "travel",
    "business",
    "finance",
    "gaming",
    "education",
    "entertainment",
    "health",
    "fashion",
    "lifestyle"
]

# Supported languages
LANGUAGES = [
    {"code": "en", "name": "English"},
    {"code": "hi", "name": "Hindi"},
    {"code": "es", "name": "Spanish"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"},
    {"code": "pt", "name": "Portuguese"},
    {"code": "it", "name": "Italian"},
    {"code": "ja", "name": "Japanese"},
    {"code": "ko", "name": "Korean"},
    {"code": "zh", "name": "Chinese"}
]

# Video duration options (in seconds)
DURATION_OPTIONS = [
    {"label": "10 seconds", "value": 10},
    {"label": "15 seconds", "value": 15},
    {"label": "20 seconds", "value": 20},
    {"label": "30 seconds", "value": 30},
    {"label": "45 seconds", "value": 45},
    {"label": "60 seconds", "value": 60}
]

# Supported platforms
PLATFORMS = [
    "youtube",
    "instagram",
    "facebook"
]

# Voice IDs for ElevenLabs (examples)
VOICE_IDS = {
    "male_1": "21m00Tcm4TlvDq8ikWAM",  # Example voice ID
    "female_1": "EXAVITQu4vr4xnSDxMaL",  # Example voice ID
    "male_2": "ErXwobaYiN019PkySvjV",
    "female_2": "MF3mGyEYCl7XYWbV9V6O"
}

# Video aspect ratios
ASPECT_RATIOS = {
    "shorts": {"width": 1080, "height": 1920},  # 9:16
    "landscape": {"width": 1920, "height": 1080},  # 16:9
    "square": {"width": 1080, "height": 1080}  # 1:1
}

# Default aspect ratio for shorts
DEFAULT_ASPECT_RATIO = "shorts"