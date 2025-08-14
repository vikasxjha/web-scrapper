"""
Configuration settings for the Blog Scraper application
"""

import os

class Config:
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'data/blog_posts.db')
    
    # Image generation settings
    IMAGE_GENERATION_ENABLED = os.environ.get('IMAGE_GENERATION_ENABLED', 'true').lower() == 'true'
    IMAGE_GENERATION_ON_SCRAPE = os.environ.get('IMAGE_GENERATION_ON_SCRAPE', 'false').lower() == 'true'  # Manual by default
    IMAGE_CACHE_ENABLED = os.environ.get('IMAGE_CACHE_ENABLED', 'true').lower() == 'true'
    IMAGE_CACHE_TTL_HOURS = int(os.environ.get('IMAGE_CACHE_TTL_HOURS', '24'))
    
    # Image directories
    GENERATED_IMAGES_DIR = os.environ.get('GENERATED_IMAGES_DIR', 'app/static/images/generated')
    PLACEHOLDER_IMAGES_DIR = os.environ.get('PLACEHOLDER_IMAGES_DIR', 'app/static/images/placeholders')
    IMAGE_CACHE_FILE = os.environ.get('IMAGE_CACHE_FILE', 'data/image_cache.json')
    
    # External API settings (for future use with real AI image generation services)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    STABILITY_AI_API_KEY = os.environ.get('STABILITY_AI_API_KEY', '')
    MIDJOURNEY_API_KEY = os.environ.get('MIDJOURNEY_API_KEY', '')
    
    # Image generation parameters
    DEFAULT_IMAGE_WIDTH = int(os.environ.get('DEFAULT_IMAGE_WIDTH', '800'))
    DEFAULT_IMAGE_HEIGHT = int(os.environ.get('DEFAULT_IMAGE_HEIGHT', '400'))
    IMAGE_QUALITY = int(os.environ.get('IMAGE_QUALITY', '90'))
    
    # Scraping settings
    SCRAPING_DELAY = float(os.environ.get('SCRAPING_DELAY', '1.0'))  # Delay between requests in seconds
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '30'))
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', '8000'))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True
    IMAGE_GENERATION_ENABLED = True

# Production configuration  
class ProductionConfig(Config):
    DEBUG = False
    
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable must be set for production")
        return key

# Testing configuration
class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests
    IMAGE_GENERATION_ENABLED = False  # Disable image generation in tests

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
