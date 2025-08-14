"""
AI Image Generation Module for Blog Posts
Generates relevant images based on article titles and descriptions
"""

import os
import hashlib
import logging
import requests
from io import BytesIO
import random
import math
from typing import Optional, Dict, Any
import json

# Try to import PIL, fall back gracefully if not available
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL (Pillow) not available. Image generation will use placeholder images only.")

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.api_key = self.config.get('api_key', '')
        self.api_endpoint = self.config.get('api_endpoint', '')
        self.image_dir = self.config.get('image_dir', 'app/static/images/generated')
        self.placeholder_dir = self.config.get('placeholder_dir', 'app/static/images/placeholders')
        self.cache_file = self.config.get('cache_file', 'data/image_cache.json')
        self.image_width = self.config.get('image_width', 800)
        self.image_height = self.config.get('image_height', 400)
        self.image_quality = self.config.get('image_quality', 90)
        
        # Ensure directories exist
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.placeholder_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        # Load cache
        self.cache = self._load_cache()
        
        # Create default placeholder if it doesn't exist
        self._create_default_placeholder()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load image generation cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading image cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save image generation cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving image cache: {e}")
    
    def _create_default_placeholder(self):
        """Create a default placeholder image"""
        placeholder_path = os.path.join(self.placeholder_dir, 'default.jpg')
        
        if not os.path.exists(placeholder_path):
            if not PIL_AVAILABLE:
                # Create a simple text file as placeholder if PIL is not available
                try:
                    with open(placeholder_path.replace('.jpg', '.txt'), 'w') as f:
                        f.write("TestGuild Blog Post - Image placeholder")
                    logger.info(f"Created text placeholder at {placeholder_path.replace('.jpg', '.txt')}")
                except Exception as e:
                    logger.error(f"Error creating text placeholder: {e}")
                return
            
            try:
                # Create a simple gradient placeholder
                width, height = 800, 400
                image = Image.new('RGB', (width, height), color='#f0f0f0')
                draw = ImageDraw.Draw(image)
                
                # Create gradient background
                for y in range(height):
                    color_value = int(240 - (y / height) * 40)  # Gradient from light to darker gray
                    color = (color_value, color_value, color_value)
                    draw.line([(0, y), (width, y)], fill=color)
                
                # Add TestGuild branding
                try:
                    # Try to use a nice font
                    font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
                    font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                except:
                    # Fallback to default font
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                
                # Draw text
                text1 = "TestGuild"
                text2 = "Blog Post"
                
                # Calculate text positions for centering
                bbox1 = draw.textbbox((0, 0), text1, font=font_large)
                bbox2 = draw.textbbox((0, 0), text2, font=font_small)
                
                text1_width = bbox1[2] - bbox1[0]
                text1_height = bbox1[3] - bbox1[1]
                text2_width = bbox2[2] - bbox2[0]
                
                x1 = (width - text1_width) // 2
                y1 = (height - text1_height) // 2 - 20
                x2 = (width - text2_width) // 2
                y2 = y1 + text1_height + 10
                
                draw.text((x1, y1), text1, fill='#4A90E2', font=font_large)
                draw.text((x2, y2), text2, fill='#666666', font=font_small)
                
                # Save placeholder
                image.save(placeholder_path, 'JPEG', quality=85)
                logger.info(f"Created default placeholder image at {placeholder_path}")
                
            except Exception as e:
                logger.error(f"Error creating default placeholder: {e}")
    
    def _generate_cache_key(self, title: str, description: str) -> str:
        """Generate a cache key for the image"""
        content = f"{title}|{description}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _create_text_based_image(self, title: str, description: str) -> str:
        """Create a highly realistic and professional image based on article content"""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, using placeholder image")
            return self._get_placeholder_filename()
        
        try:
            # Create image dimensions
            width, height = self.image_width, self.image_height
            
            # Analyze content to determine theme and style
            content_theme = self._analyze_content_theme(title, description)
            colors = self._get_thematic_colors(content_theme)
            
            # Create sophisticated background
            image = self._create_realistic_background(width, height, content_theme, colors)
            draw = ImageDraw.Draw(image)
            
            # Add thematic visual elements first (behind text)
            self._add_thematic_elements(draw, width, height, content_theme, colors)
            
            # Load high-quality fonts with fallbacks
            fonts = self._load_professional_fonts()
            
            # Create a clean content area
            self._create_content_overlay(draw, width, height, colors)
            
            # Prepare and style the title
            title_styled = self._prepare_title_text(title)
            
            # Draw title with professional typography
            title_y = self._draw_professional_title(draw, title_styled, width, height, fonts, colors)
            
            # Draw description with enhanced readability
            if description:
                desc_y = title_y + 40
                self._draw_professional_description(draw, description, width, height, desc_y, fonts, colors)
            
            # Add theme indicator and branding
            self._add_professional_branding(draw, width, height, content_theme, fonts, colors)
            
            # Add subtle visual enhancements
            self._add_visual_polish(draw, width, height, colors)
            
            # Generate filename
            filename = f"generated_{self._generate_cache_key(title, description)}.jpg"
            filepath = os.path.join(self.image_dir, filename)
            
            # Save with high quality
            image.save(filepath, 'JPEG', quality=95, optimize=True)
            logger.info(f"Created realistic contextual image for theme '{content_theme}': {filepath}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error creating realistic image: {e}")
            return self._get_placeholder_filename()
    
    def _analyze_content_theme(self, title: str, description: str) -> str:
        """Analyze content to determine the theme for visual representation with improved accuracy"""
        content = f"{title} {description}".lower()
        
        # Enhanced theme keywords with weighted scoring
        theme_keywords = {
            'testing': {
                'primary': ['testing', 'test automation', 'qa', 'quality assurance', 'unit test', 'integration test'],
                'secondary': ['selenium', 'cypress', 'junit', 'pytest', 'testng', 'mock', 'stub', 'verify', 'assert'],
                'tools': ['postman', 'jmeter', 'cucumber', 'behave', 'robot framework', 'playwright']
            },
            'development': {
                'primary': ['programming', 'development', 'coding', 'software engineering', 'algorithm'],
                'secondary': ['api', 'framework', 'library', 'sdk', 'architecture', 'design pattern', 'refactor'],
                'tools': ['git', 'github', 'ide', 'compiler', 'debugger', 'profiler', 'lint']
            },
            'data': {
                'primary': ['data science', 'machine learning', 'artificial intelligence', 'big data', 'analytics'],
                'secondary': ['dataset', 'model', 'neural network', 'deep learning', 'statistics', 'visualization'],
                'tools': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'jupyter', 'tableau', 'powerbi']
            },
            'security': {
                'primary': ['cybersecurity', 'security', 'vulnerability', 'penetration testing', 'encryption'],
                'secondary': ['authentication', 'authorization', 'firewall', 'malware', 'phishing', 'breach'],
                'tools': ['owasp', 'burp suite', 'metasploit', 'nmap', 'wireshark', 'ssl', 'https']
            },
            'web': {
                'primary': ['web development', 'frontend', 'backend', 'full stack', 'responsive design'],
                'secondary': ['html', 'css', 'javascript', 'dom', 'ajax', 'rest api', 'graphql'],
                'tools': ['react', 'angular', 'vue', 'nodejs', 'express', 'webpack', 'babel']
            },
            'mobile': {
                'primary': ['mobile development', 'android', 'ios', 'mobile app', 'native app'],
                'secondary': ['swift', 'kotlin', 'java', 'objective-c', 'cross platform', 'hybrid app'],
                'tools': ['flutter', 'react native', 'xamarin', 'ionic', 'android studio', 'xcode']
            },
            'cloud': {
                'primary': ['cloud computing', 'aws', 'azure', 'google cloud', 'serverless', 'microservices'],
                'secondary': ['docker', 'kubernetes', 'container', 'devops', 'ci/cd', 'infrastructure'],
                'tools': ['terraform', 'ansible', 'jenkins', 'lambda', 'ec2', 's3', 'rds']
            },
            'performance': {
                'primary': ['performance optimization', 'load testing', 'stress testing', 'benchmarking'],
                'secondary': ['scalability', 'throughput', 'latency', 'bottleneck', 'profiling', 'monitoring'],
                'tools': ['jmeter', 'loadrunner', 'gatling', 'new relic', 'datadog', 'prometheus']
            },
            'tutorial': {
                'primary': ['tutorial', 'guide', 'how to', 'step by step', 'beginner', 'introduction'],
                'secondary': ['learn', 'course', 'lesson', 'example', 'walkthrough', 'getting started'],
                'tools': ['documentation', 'cookbook', 'cheat sheet', 'reference', 'best practices']
            },
            'devops': {
                'primary': ['devops', 'ci/cd', 'continuous integration', 'deployment', 'infrastructure'],
                'secondary': ['pipeline', 'automation', 'monitoring', 'logging', 'configuration'],
                'tools': ['jenkins', 'gitlab', 'travis', 'circleci', 'docker', 'kubernetes']
            },
            'ai_ml': {
                'primary': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
                'secondary': ['algorithm', 'model training', 'prediction', 'classification', 'regression'],
                'tools': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'opencv', 'nlp']
            }
        }
        
        # Calculate weighted scores
        theme_scores = {}
        for theme, categories in theme_keywords.items():
            score = 0
            # Primary keywords get highest weight
            for keyword in categories['primary']:
                if keyword in content:
                    score += 3
            # Secondary keywords get medium weight
            for keyword in categories['secondary']:
                if keyword in content:
                    score += 2
            # Tool keywords get lower weight
            for keyword in categories['tools']:
                if keyword in content:
                    score += 1
            
            if score > 0:
                theme_scores[theme] = score
        
        # Return the theme with highest score, with minimum threshold
        if theme_scores:
            best_theme = max(theme_scores.keys(), key=theme_scores.get)
            best_score = theme_scores[best_theme]
            
            # Require minimum score of 2 for confident theme detection
            if best_score >= 2:
                return best_theme
        
        return 'general'
    
    def _get_thematic_colors(self, theme: str) -> dict:
        """Get vibrant, comic-book style color schemes inspired by the sample"""
        color_schemes = {
            'testing': {
                'bg': '#FF8C00',  # Vibrant orange like sample
                'text': '#FFD700',  # Bright gold for text
                'accent': '#FF6347',  # Tomato red
                'secondary': '#32CD32',  # Lime green for success
                'gradient': ['#FF8C00', '#FF4500'],
                'icon': '#00FF7F'  # Spring green
            },
            'development': {
                'bg': '#4169E1',  # Royal Blue
                'text': '#FFD700',  # Gold text like sample
                'accent': '#00BFFF',  # Deep sky blue
                'secondary': '#87CEEB',
                'gradient': ['#4169E1', '#0000CD'],
                'icon': '#ADD8E6'
            },
            'data': {
                'bg': '#9932CC',  # Dark Orchid
                'text': '#FFD700',  # Gold text
                'accent': '#DA70D6',  # Orchid
                'secondary': '#DDA0DD',
                'gradient': ['#9932CC', '#8B008B'],
                'icon': '#E6E6FA'
            },
            'ai_ml': {
                'bg': '#FF6347',  # Tomato - vibrant like sample
                'text': '#FFD700',  # Gold text
                'accent': '#FF4500',  # Orange red
                'secondary': '#FFA500',  # Orange
                'gradient': ['#FF6347', '#DC143C'],
                'icon': '#FFE4B5'
            },
            'security': {
                'bg': '#DC143C',  # Crimson
                'text': '#FFD700',  # Gold text
                'accent': '#FF0000',  # Pure red
                'secondary': '#FFB6C1',
                'gradient': ['#DC143C', '#8B0000'],
                'icon': '#FFA07A'
            },
            'web': {
                'bg': '#FF8C00',  # Orange like sample
                'text': '#FFD700',  # Gold text
                'accent': '#FF6347',  # Tomato
                'secondary': '#FFE4B5',
                'gradient': ['#FF8C00', '#FF4500'],
                'icon': '#FFEFD5'
            },
            'mobile': {
                'bg': '#20B2AA',  # Light Sea Green
                'text': '#FFD700',  # Gold text
                'accent': '#00CED1',  # Dark Turquoise
                'secondary': '#AFEEEE',
                'gradient': ['#20B2AA', '#008B8B'],
                'icon': '#E0FFFF'
            },
            'cloud': {
                'bg': '#4682B4',  # Steel Blue
                'text': '#FFD700',  # Gold text
                'accent': '#5F9EA0',  # Cadet Blue
                'secondary': '#B0E0E6',
                'gradient': ['#4682B4', '#2F4F4F'],
                'icon': '#F0F8FF'
            },
            'performance': {
                'bg': '#FF4500',  # Orange Red - energetic
                'text': '#FFD700',  # Gold text
                'accent': '#FF6600',
                'secondary': '#FFCC99',
                'gradient': ['#FF4500', '#DC143C'],
                'icon': '#FFFF99'
            },
            'tutorial': {
                'bg': '#32CD32',  # Lime Green
                'text': '#FFD700',  # Gold text
                'accent': '#228B22',
                'secondary': '#90EE90',
                'gradient': ['#32CD32', '#006400'],
                'icon': '#F0FFF0'
            },
            'devops': {
                'bg': '#708090',  # Slate Gray
                'text': '#FFD700',  # Gold text
                'accent': '#2F4F4F',  # Dark Slate Gray
                'secondary': '#D3D3D3',
                'gradient': ['#708090', '#483D8B'],
                'icon': '#F5F5F5'
            },
            'tools': {
                'bg': '#696969',  # Dim Gray
                'text': '#FFD700',  # Gold text
                'accent': '#2F4F4F',
                'secondary': '#D3D3D3',
                'gradient': ['#696969', '#2F4F4F'],
                'icon': '#DCDCDC'
            },
            'general': {
                'bg': '#FF8C00',  # Default to orange like sample
                'text': '#FFD700',  # Gold text
                'accent': '#FF6347',
                'secondary': '#B0C4DE',
                'gradient': ['#FF8C00', '#FF4500'],
                'icon': '#E6F3FF'
            }
        }
        
        return color_schemes.get(theme, color_schemes['general'])
    
    def _load_professional_fonts(self) -> dict:
        """Load high-quality fonts with fallbacks"""
        fonts = {}
        
        # Try to load system fonts with various fallbacks
        font_paths = [
            # macOS fonts
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf", 
            "/System/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Times.ttc",
            # Linux fonts
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            # Windows fonts
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        ]
        
        try:
            # Title font - large and bold
            for path in font_paths:
                if os.path.exists(path):
                    if "Bold" in path or "arialbd" in path:
                        fonts['title'] = ImageFont.truetype(path, 42)
                        break
            else:
                fonts['title'] = ImageFont.load_default()
            
            # Subtitle font - medium
            for path in font_paths:
                if os.path.exists(path) and "Bold" not in path:
                    fonts['subtitle'] = ImageFont.truetype(path, 24)
                    break
            else:
                fonts['subtitle'] = ImageFont.load_default()
            
            # Description font - readable
            for path in font_paths:
                if os.path.exists(path) and "Bold" not in path:
                    fonts['description'] = ImageFont.truetype(path, 18)
                    break
            else:
                fonts['description'] = ImageFont.load_default()
            
            # Small font for labels
            for path in font_paths:
                if os.path.exists(path) and "Bold" not in path:
                    fonts['small'] = ImageFont.truetype(path, 14)
                    break
            else:
                fonts['small'] = ImageFont.load_default()
                
        except Exception as e:
            logger.warning(f"Error loading fonts: {e}, using defaults")
            fonts = {
                'title': ImageFont.load_default(),
                'subtitle': ImageFont.load_default(),
                'description': ImageFont.load_default(),
                'small': ImageFont.load_default()
            }
        
        return fonts
    
    def _create_realistic_background(self, width: int, height: int, theme: str, colors: dict):
        """Create a vibrant, comic-book style background inspired by professional designs"""
        # Create base with vibrant gradient
        image = Image.new('RGB', (width, height), color=colors['bg'])
        
        # Create dynamic multi-color gradient
        for y in range(height):
            ratio = y / height
            # Create more vibrant gradient
            r1, g1, b1 = ImageColor.getrgb(colors['gradient'][0])
            r2, g2, b2 = ImageColor.getrgb(colors['gradient'][1])
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            # Add vibrant color boost
            r = min(255, int(r * 1.1))
            g = min(255, int(g * 1.1)) 
            b = min(255, int(b * 1.1))
            
            color = (r, g, b)
            draw = ImageDraw.Draw(image)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add comic-book style halftone pattern
        self._add_halftone_pattern(image, width, height, colors)
        
        # Add dynamic geometric shapes
        self._add_dynamic_shapes(image, width, height, colors, theme)
        
        return image
    
    def _add_halftone_pattern(self, image, width: int, height: int, colors: dict):
        """Add comic-book style halftone dot pattern"""
        try:
            draw = ImageDraw.Draw(image)
            dot_color = ImageColor.getrgb(colors['accent'])
            # Make dots semi-transparent by adjusting color
            dot_color = (
                min(255, dot_color[0] + 40),
                min(255, dot_color[1] + 40),
                min(255, dot_color[2] + 40)
            )
            
            # Create halftone pattern
            for x in range(0, width, 20):
                for y in range(0, height, 20):
                    # Vary dot size based on position
                    dot_size = 2 + (x + y) % 4
                    draw.ellipse([x, y, x + dot_size, y + dot_size], fill=dot_color)
                    
        except Exception as e:
            logger.warning(f"Error adding halftone pattern: {e}")
    
    def _add_dynamic_shapes(self, image, width: int, height: int, colors: dict, theme: str):
        """Add dynamic geometric shapes for visual appeal"""
        try:
            draw = ImageDraw.Draw(image)
            
            # Add diagonal stripes in corners
            stripe_color = ImageColor.getrgb(colors['secondary'])
            for i in range(5):
                # Top-left stripes
                start_x = i * 15
                draw.line([(start_x, 0), (0, start_x)], fill=stripe_color, width=3)
                
                # Bottom-right stripes  
                end_x = width - i * 15
                end_y = height - i * 15
                draw.line([(end_x, height), (width, end_y)], fill=stripe_color, width=3)
            
            # Add theme-specific accent shapes
            accent_color = colors['icon']
            if theme in ['testing', 'ai_ml']:
                # Tech circuits pattern
                self._draw_circuit_pattern(draw, width, height, accent_color)
            elif theme in ['web', 'mobile']:
                # Digital grid pattern
                self._draw_grid_pattern(draw, width, height, accent_color)
            elif theme in ['security', 'performance']:
                # Shield/speed lines
                self._draw_action_lines(draw, width, height, accent_color)
            
        except Exception as e:
            logger.warning(f"Error adding dynamic shapes: {e}")
    
    def _draw_circuit_pattern(self, draw, width: int, height: int, color):
        """Draw tech circuit pattern"""
        # Simple circuit-like lines in corners
        lines = [
            [(width-80, 20), (width-60, 20), (width-60, 40), (width-40, 40)],
            [(20, height-40), (40, height-40), (40, height-60), (60, height-60)]
        ]
        for line in lines:
            for i in range(len(line)-1):
                draw.line([line[i], line[i+1]], fill=color, width=2)
                # Add connection dots
                draw.ellipse([line[i][0]-2, line[i][1]-2, line[i][0]+2, line[i][1]+2], fill=color)
    
    def _draw_grid_pattern(self, draw, width: int, height: int, color):
        """Draw digital grid pattern"""
        # Subtle grid in background
        for x in range(50, width-50, 40):
            draw.line([(x, 20), (x, 80)], fill=color, width=1)
        for y in range(50, height-50, 40):
            draw.line([(width-80, y), (width-20, y)], fill=color, width=1)
    
    def _draw_action_lines(self, draw, width: int, height: int, color):
        """Draw dynamic action/speed lines"""
        # Speed lines radiating from corner
        center_x, center_y = width - 50, height - 50
        for i in range(8):
            angle = i * 45
            import math
            end_x = center_x + 30 * math.cos(math.radians(angle))
            end_y = center_y + 30 * math.sin(math.radians(angle))
            draw.line([(center_x, center_y), (end_x, end_y)], fill=color, width=2)
    
    def _create_content_overlay(self, draw, width: int, height: int, colors: dict):
        """Create a clean content area for text"""
        try:
            # Create a semi-transparent overlay for better text readability
            overlay_color = ImageColor.getrgb(colors['bg'])
            overlay_alpha = 180  # Semi-transparent
            
            # Main content area
            content_margin = 40
            content_width = width - (content_margin * 2)
            content_height = height - (content_margin * 2)
            
            # Draw rounded rectangle for content area
            self._draw_rounded_rectangle(
                draw, 
                content_margin, content_margin, 
                content_width, content_height, 
                radius=15, 
                fill=(overlay_alpha, overlay_alpha, overlay_alpha), 
                outline=colors['accent']
            )
            
        except Exception as e:
            logger.warning(f"Error creating content overlay: {e}")
    
    def _draw_rounded_rectangle(self, draw, x, y, width, height, radius=10, fill=None, outline=None):
        """Draw a rounded rectangle"""
        try:
            # Simple rounded rectangle using arcs and lines
            draw.rectangle([x + radius, y, x + width - radius, y + height], fill=fill, outline=outline)
            draw.rectangle([x, y + radius, x + width, y + height - radius], fill=fill, outline=outline)
            
            # Corner arcs (simplified)
            draw.ellipse([x, y, x + radius*2, y + radius*2], fill=fill, outline=outline)
            draw.ellipse([x + width - radius*2, y, x + width, y + radius*2], fill=fill, outline=outline)
            draw.ellipse([x, y + height - radius*2, x + radius*2, y + height], fill=fill, outline=outline)
            draw.ellipse([x + width - radius*2, y + height - radius*2, x + width, y + height], fill=fill, outline=outline)
            
        except Exception as e:
            logger.warning(f"Error drawing rounded rectangle: {e}")
    
    def _prepare_title_text(self, title: str) -> str:
        """Prepare title text with smart truncation"""
        # Smart truncation that preserves meaning
        words = title.split()
        if len(words) <= 8:
            return title
        
        # Keep the most important words (usually at the beginning)
        important_words = words[:6]
        
        # Add the last word if it's important (like "Guide", "Tutorial", etc.)
        if words[-1].lower() in ['guide', 'tutorial', 'tips', 'methods', 'strategies', 'techniques']:
            important_words.append(words[-1])
        
        return ' '.join(important_words) + ('...' if len(words) > len(important_words) else '')
    
    def _draw_professional_title(self, draw, title: str, width: int, height: int, fonts: dict, colors: dict) -> int:
        """Draw title with bold comic-book style typography like the sample"""
        try:
            # Wrap text intelligently
            title_lines = self._wrap_text_smart(title, fonts['title'], width - 120)
            
            # Calculate starting position
            line_height = 55
            total_text_height = len(title_lines) * line_height
            start_y = 60  # Top margin
            
            current_y = start_y
            
            for i, line in enumerate(title_lines):
                # Get text dimensions
                bbox = draw.textbbox((0, 0), line, font=fonts['title'])
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center horizontally
                x = (width - text_width) // 2
                
                # Comic-book style text with bold outline (like the sample)
                outline_width = 4
                
                # Draw black outline (multiple passes for thickness)
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx*dx + dy*dy <= outline_width*outline_width:
                            draw.text((x + dx, current_y + dy), line, fill='#000000', font=fonts['title'])
                
                # Draw main text in bright color (yellow/orange like sample)
                main_color = '#FFD700'  # Bright gold/yellow
                if colors['text'] != '#FFFFFF':
                    main_color = colors['text']
                draw.text((x, current_y), line, fill=main_color, font=fonts['title'])
                
                # Add highlight/shine effect on top
                highlight_color = '#FFFFFF'
                draw.text((x - 1, current_y - 2), line, fill=highlight_color, font=fonts['title'])
                draw.text((x, current_y), line, fill=main_color, font=fonts['title'])
                
                current_y += line_height
            
            return current_y
            
        except Exception as e:
            logger.error(f"Error drawing comic-style title: {e}")
            return 150
    
    def _draw_professional_description(self, draw, description: str, width: int, height: int, start_y: int, fonts: dict, colors: dict):
        """Draw description with enhanced readability"""
        try:
            # Prepare description text
            desc_text = self._prepare_description_text(description)
            desc_lines = self._wrap_text_smart(desc_text, fonts['description'], width - 160)
            
            # Limit to 3 lines for clean layout
            desc_lines = desc_lines[:3]
            
            current_y = start_y
            line_height = 25
            
            for line in desc_lines:
                bbox = draw.textbbox((0, 0), line, font=fonts['description'])
                text_width = bbox[2] - bbox[0]
                
                # Center horizontally
                x = (width - text_width) // 2
                
                # Draw subtle text shadow
                draw.text((x + 1, current_y + 1), line, fill='#000000', font=fonts['description'])
                
                # Draw main text
                text_color = colors['text'] if colors['text'] != '#FFFFFF' else '#F0F0F0'
                draw.text((x, current_y), line, fill=text_color, font=fonts['description'])
                
                current_y += line_height
                
        except Exception as e:
            logger.error(f"Error drawing professional description: {e}")
    
    def _prepare_description_text(self, description: str) -> str:
        """Prepare description text for optimal display"""
        # Clean up description
        desc = description.strip()
        
        # Remove redundant phrases
        redundant_phrases = [
            "In this article,", "This article", "In this post,", "This post",
            "Learn about", "Discover", "Find out"
        ]
        
        for phrase in redundant_phrases:
            if desc.startswith(phrase):
                desc = desc[len(phrase):].strip()
        
        # Ensure proper length
        if len(desc) > 150:
            # Find last complete sentence within limit
            sentences = desc.split('.')
            result = ""
            for sentence in sentences:
                if len(result + sentence + '.') <= 150:
                    result += sentence + '.'
                else:
                    break
            desc = result if result else desc[:147] + '...'
        
        return desc
    
    def _wrap_text_smart(self, text: str, font, max_width: int) -> list:
        """Smart text wrapping that preserves word integrity"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, force break
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _add_professional_branding(self, draw, width: int, height: int, theme: str, fonts: dict, colors: dict):
        """Add professional branding and theme indicator"""
        try:
            # Theme badge in top-right
            badge_text = theme.replace('_', '/').title()
            badge_x = width - 120
            badge_y = 20
            
            # Badge background
            bbox = draw.textbbox((0, 0), badge_text, font=fonts['small'])
            badge_width = bbox[2] - bbox[0] + 20
            badge_height = bbox[3] - bbox[1] + 10
            
            self._draw_rounded_rectangle(draw, badge_x, badge_y, badge_width, badge_height, 
                                       radius=8, fill=colors['accent'], outline=colors['secondary'])
            
            # Badge text
            draw.text((badge_x + 10, badge_y + 5), badge_text, fill='#FFFFFF', font=fonts['small'])
            
            # TestGuild branding (bottom-right)
            brand_text = "TestGuild"
            brand_x = width - 100
            brand_y = height - 30
            
            # Brand background
            draw.rectangle([brand_x - 10, brand_y - 5, brand_x + 80, brand_y + 20], 
                          fill=colors['bg'], outline=colors['accent'], width=2)
            
            # Brand text
            draw.text((brand_x, brand_y), brand_text, fill=colors['text'], font=fonts['small'])
            
        except Exception as e:
            logger.error(f"Error adding professional branding: {e}")
    
    def _add_visual_polish(self, draw, width: int, height: int, colors: dict):
        """Add subtle visual enhancements for polish"""
        try:
            # Add corner accents
            accent_size = 20
            accent_color = colors['secondary']
            
            # Top-left accent
            draw.polygon([(0, 0), (accent_size, 0), (0, accent_size)], fill=accent_color)
            
            # Bottom-right accent
            draw.polygon([(width, height), (width - accent_size, height), (width, height - accent_size)], 
                        fill=accent_color)
            
            # Add subtle border
            border_color = colors['accent']
            draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=2)
            
        except Exception as e:
            logger.error(f"Error adding visual polish: {e}")
    
    def _create_thematic_background(self, width: int, height: int, theme: str, colors: dict):
        """Create a thematic background based on content theme"""
        # Create gradient background
        image = Image.new('RGB', (width, height), color=colors['bg'])
        
        # Add gradient effect
        for y in range(height):
            # Create gradient from top to bottom
            ratio = y / height
            r1, g1, b1 = ImageColor.getrgb(colors['gradient'][0])
            r2, g2, b2 = ImageColor.getrgb(colors['gradient'][1])
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = (r, g, b)
            draw = ImageDraw.Draw(image)
            draw.line([(0, y), (width, y)], fill=color)
        
        return image
    
    def _add_thematic_elements(self, draw, width: int, height: int, theme: str, colors: dict):
        """Add enhanced visual elements specific to the content theme"""
        try:
            if theme == 'testing':
                self._draw_testing_elements(draw, width, height, colors)
            elif theme == 'development':
                self._draw_development_elements(draw, width, height, colors)
            elif theme == 'data':
                self._draw_data_elements(draw, width, height, colors)
            elif theme == 'security':
                self._draw_security_elements(draw, width, height, colors)
            elif theme == 'web':
                self._draw_web_elements(draw, width, height, colors)
            elif theme == 'mobile':
                self._draw_mobile_elements(draw, width, height, colors)
            elif theme == 'cloud':
                self._draw_cloud_elements(draw, width, height, colors)
            elif theme == 'performance':
                self._draw_performance_elements(draw, width, height, colors)
            elif theme == 'tutorial':
                self._draw_tutorial_elements(draw, width, height, colors)
            elif theme == 'devops':
                self._draw_devops_elements(draw, width, height, colors)
            elif theme == 'ai_ml':
                self._draw_ai_ml_elements(draw, width, height, colors)
            elif theme == 'tools':
                self._draw_tool_elements(draw, width, height, colors)
            else:
                self._add_decorative_elements(draw, width, height, colors['accent'])
                
        except Exception as e:
            logger.error(f"Error adding thematic elements: {e}")
    
    def _draw_text_background(self, draw, x: int, y: int, width: int, height: int, colors: dict, alpha: float = 0.8):
        """Draw a semi-transparent background for text"""
        try:
            # Create overlay for text readability
            overlay_color = ImageColor.getrgb(colors['accent'])
            # Simple rectangle for text background
            draw.rectangle([x, y, x + width, y + height], fill=overlay_color, outline=colors['secondary'])
        except Exception as e:
            logger.error(f"Error drawing text background: {e}")
    
    def _add_branding(self, draw, width: int, height: int, font, colors: dict):
        """Add TestGuild branding to the image"""
        try:
            brand_text = "TestGuild"
            bbox = draw.textbbox((0, 0), brand_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = width - text_width - 20
            y = height - 30
            
            # Add background for branding
            draw.rectangle([x - 5, y - 5, x + text_width + 5, y + 20], fill=colors['accent'])
            draw.text((x, y), brand_text, fill=colors['text'], font=font)
        except Exception as e:
            logger.error(f"Error adding branding: {e}")
    
    def _add_content_icons(self, draw, width: int, height: int, theme: str, colors: dict):
        """Add simple iconic representations based on content"""
        try:
            icon_size = 40
            x = 30
            y = 30
            
            if theme == 'testing':
                # Draw a simple checkmark
                draw.line([(x, y + icon_size//2), (x + icon_size//3, y + 2*icon_size//3), 
                          (x + icon_size, y + icon_size//4)], fill=colors['secondary'], width=4)
            elif theme == 'development':
                # Draw angle brackets < >
                draw.line([(x + icon_size//3, y), (x, y + icon_size//2), (x + icon_size//3, y + icon_size)], 
                         fill=colors['secondary'], width=3)
                draw.line([(x + 2*icon_size//3, y), (x + icon_size, y + icon_size//2), (x + 2*icon_size//3, y + icon_size)], 
                         fill=colors['secondary'], width=3)
            elif theme == 'data':
                # Draw simple bar chart
                bars = [icon_size//4, icon_size//2, 3*icon_size//4, icon_size//3]
                for i, bar_height in enumerate(bars):
                    bar_x = x + i * (icon_size//4)
                    draw.rectangle([bar_x, y + icon_size - bar_height, bar_x + icon_size//6, y + icon_size], 
                                 fill=colors['secondary'])
            # Add more icon types as needed...
                
        except Exception as e:
            logger.error(f"Error adding content icons: {e}")
    
    # Enhanced thematic element drawing methods
    def _draw_testing_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive testing-themed elements with character illustrations"""
        try:
            # Draw a robot character (inspired by the sample)
            robot_x, robot_y = width - 150, height - 180
            self._draw_testing_robot(draw, robot_x, robot_y, colors)
            
            # Multiple checkmarks in different sizes
            check_positions = [(80, 50), (120, 90), (60, 130)]
            for x, y in check_positions:
                # Large checkmark with comic-book style
                self._draw_comic_checkmark(draw, x, y, colors['icon'], size=20)
            
            # Test results dashboard
            dashboard_x, dashboard_y = 30, height - 120
            self._draw_test_dashboard(draw, dashboard_x, dashboard_y, colors)
            
            # Add "TESTING" badge
            self._draw_theme_badge(draw, 30, 30, "TESTING", colors)
            
        except Exception as e:
            logger.error(f"Error drawing testing elements: {e}")
    
    def _draw_testing_robot(self, draw, x, y, colors):
        """Draw a cute testing robot character"""
        try:
            # Robot head (rectangular with rounded corners)
            head_width, head_height = 40, 35
            self._draw_rounded_rect(draw, x, y, head_width, head_height, 8, colors['icon'], colors['accent'])
            
            # Robot eyes (like the sample)
            eye_color = '#FFFFFF'
            draw.ellipse([x + 8, y + 8, x + 16, y + 16], fill=eye_color, outline=colors['accent'], width=2)
            draw.ellipse([x + 24, y + 8, x + 32, y + 16], fill=eye_color, outline=colors['accent'], width=2)
            
            # Eye pupils
            draw.ellipse([x + 10, y + 10, x + 14, y + 14], fill='#000000')
            draw.ellipse([x + 26, y + 10, x + 30, y + 14], fill='#000000')
            
            # Robot mouth (digital display)
            draw.rectangle([x + 12, y + 20, x + 28, y + 26], fill='#000000', outline=colors['accent'], width=1)
            # Smile pixels
            pixels = [(x + 14, y + 22), (x + 16, y + 24), (x + 20, y + 24), (x + 22, y + 24), (x + 24, y + 22)]
            for px, py in pixels:
                draw.rectangle([px, py, px + 1, py + 1], fill='#00FF00')
            
            # Robot body
            body_y = y + head_height + 5
            self._draw_rounded_rect(draw, x - 5, body_y, 50, 60, 10, colors['secondary'], colors['accent'])
            
            # TestGuild logo on chest
            logo_x, logo_y = x + 15, body_y + 20
            draw.polygon([(logo_x, logo_y), (logo_x + 10, logo_y), (logo_x + 5, logo_y + 8)], fill=colors['accent'])
            draw.text((logo_x + 2, logo_y + 10), "T", fill=colors['text'], font=None)
            
            # Robot arms
            arm_y = body_y + 15
            # Left arm
            draw.rectangle([x - 15, arm_y, x - 5, arm_y + 25], fill=colors['icon'], outline=colors['accent'], width=2)
            # Right arm  
            draw.rectangle([x + 45, arm_y, x + 55, arm_y + 25], fill=colors['icon'], outline=colors['accent'], width=2)
            
            # Robot hands holding test tools
            # Left hand with test report
            hand_x = x - 15
            draw.rectangle([hand_x - 8, arm_y + 20, hand_x, arm_y + 35], fill='#FFFFFF', outline='#000000', width=1)
            draw.line([(hand_x - 6, arm_y + 25), (hand_x - 2, arm_y + 25)], fill='#000000', width=1)
            
        except Exception as e:
            logger.error(f"Error drawing testing robot: {e}")
    
    def _draw_comic_checkmark(self, draw, x, y, color, size=15):
        """Draw a comic-book style checkmark with outline"""
        # Black outline
        outline_width = 2
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx*dx + dy*dy <= outline_width*outline_width:
                    draw.line([(x + dx, y + size//2 + dy), (x + size//3 + dx, y + 2*size//3 + dy), 
                              (x + size + dx, y + size//4 + dy)], fill='#000000', width=3)
        
        # Main checkmark
        draw.line([(x, y + size//2), (x + size//3, y + 2*size//3), (x + size, y + size//4)], 
                 fill=color, width=4)
    
    def _draw_test_dashboard(self, draw, x, y, colors):
        """Draw a testing dashboard display"""
        # Dashboard background
        self._draw_rounded_rect(draw, x, y, 120, 80, 8, colors['bg'], colors['accent'])
        
        # Title
        draw.text((x + 10, y + 5), "TEST RESULTS", fill=colors['text'])
        
        # Progress bars
        bars = [(70, '#00FF00'), (85, '#FFFF00'), (95, '#00FF00')]
        for i, (percentage, bar_color) in enumerate(bars):
            bar_y = y + 25 + i * 15
            # Background bar
            draw.rectangle([x + 10, bar_y, x + 100, bar_y + 8], fill='#333333')
            # Progress bar
            progress_width = int((percentage / 100) * 90)
            draw.rectangle([x + 10, bar_y, x + 10 + progress_width, bar_y + 8], fill=bar_color)
            # Percentage text
            draw.text((x + 105, bar_y - 2), f"{percentage}%", fill=colors['text'])
    
    def _draw_theme_badge(self, draw, x, y, text, colors):
        """Draw a comic-book style theme badge"""
        # Badge background with outline
        badge_width = len(text) * 8 + 20
        badge_height = 25
        
        # Black outline
        self._draw_rounded_rect(draw, x - 2, y - 2, badge_width + 4, badge_height + 4, 8, '#000000', '#000000')
        # Main badge
        self._draw_rounded_rect(draw, x, y, badge_width, badge_height, 6, colors['accent'], colors['secondary'])
        
        # Badge text
        text_x = x + 10
        text_y = y + 8
        draw.text((text_x, text_y), text, fill='#FFFFFF')
    
    def _draw_rounded_rect(self, draw, x, y, width, height, radius, fill_color, outline_color):
        """Draw a rounded rectangle"""
        # Main rectangle
        draw.rectangle([x + radius, y, x + width - radius, y + height], fill=fill_color, outline=outline_color)
        draw.rectangle([x, y + radius, x + width, y + height - radius], fill=fill_color, outline=outline_color)
        
        # Corners
        draw.ellipse([x, y, x + radius*2, y + radius*2], fill=fill_color, outline=outline_color)
        draw.ellipse([x + width - radius*2, y, x + width, y + radius*2], fill=fill_color, outline=outline_color)
        draw.ellipse([x, y + height - radius*2, x + radius*2, y + height], fill=fill_color, outline=outline_color)
        draw.ellipse([x + width - radius*2, y + height - radius*2, x + width, y + height], fill=fill_color, outline=outline_color)
    
    def _draw_development_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive development-themed elements"""
        try:
            # Code brackets and syntax
            bracket_pairs = [
                (30, 50, 70), (width-70, 50, 70), 
                (50, 100, 50), (width-100, 100, 50)
            ]
            for x, y, size in bracket_pairs:
                # Opening bracket
                draw.line([(x, y), (x-10, y+size//2), (x, y+size)], fill=colors['icon'], width=3)
                # Closing bracket
                draw.line([(x+size, y), (x+size+10, y+size//2), (x+size, y+size)], fill=colors['icon'], width=3)
            
            # Code lines representation
            code_lines = [(60, 60, 120), (60, 70, 90), (60, 80, 110), (60, 90, 80)]
            for x, y, length in code_lines:
                draw.line([(x, y), (x + length, y)], fill=colors['secondary'], width=2)
                # Indentation dots
                for dot in range(3):
                    draw.ellipse([x - 15 + dot*3, y-1, x - 13 + dot*3, y+1], fill=colors['accent'])
            
            # Git branch visualization
            branch_x = width - 100
            draw.line([(branch_x, 30), (branch_x, 80)], fill=colors['icon'], width=3)
            draw.line([(branch_x, 50), (branch_x + 30, 40)], fill=colors['secondary'], width=2)
            draw.line([(branch_x + 30, 40), (branch_x + 30, 70)], fill=colors['secondary'], width=2)
            
        except Exception as e:
            logger.error(f"Error drawing development elements: {e}")
    
    def _draw_data_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive data science themed elements"""
        try:
            # Enhanced bar chart
            chart_x = width - 120
            bar_heights = [30, 50, 25, 40, 35]
            bar_width = 12
            for i, height_val in enumerate(bar_heights):
                x = chart_x + i * (bar_width + 3)
                y = height - 80
                draw.rectangle([x, y - height_val, x + bar_width, y], fill=colors['icon'])
                # Value labels
                draw.ellipse([x + bar_width//2 - 2, y - height_val - 8, 
                             x + bar_width//2 + 2, y - height_val - 4], fill=colors['secondary'])
            
            # Neural network nodes
            nodes = [(50, 60), (80, 40), (80, 80), (110, 60)]
            for node in nodes:
                draw.ellipse([node[0]-8, node[1]-8, node[0]+8, node[1]+8], 
                            outline=colors['accent'], fill=colors['icon'], width=2)
            
            # Connections between nodes
            connections = [(nodes[0], nodes[1]), (nodes[0], nodes[2]), 
                          (nodes[1], nodes[3]), (nodes[2], nodes[3])]
            for start, end in connections:
                draw.line([start, end], fill=colors['secondary'], width=2)
            
            # Data flow arrows
            arrow_y = height - 40
            for x in range(30, width-30, 40):
                draw.polygon([(x, arrow_y), (x+15, arrow_y-5), (x+15, arrow_y+5)], fill=colors['accent'])
            
        except Exception as e:
            logger.error(f"Error drawing data elements: {e}")
    
    def _draw_security_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive security-themed elements"""
        try:
            # Enhanced shield
            shield_x, shield_y = 50, 50
            shield_points = [
                (shield_x, shield_y), (shield_x-15, shield_y+20), (shield_x-15, shield_y+40),
                (shield_x, shield_y+55), (shield_x+15, shield_y+40), (shield_x+15, shield_y+20)
            ]
            draw.polygon(shield_points, outline=colors['accent'], fill=colors['icon'], width=3)
            
            # Lock icon
            lock_x, lock_y = shield_x-5, shield_y+15
            draw.rectangle([lock_x, lock_y+8, lock_x+10, lock_y+20], outline=colors['text'], width=2)
            draw.arc([lock_x+2, lock_y, lock_x+8, lock_y+8], start=0, end=180, fill=colors['text'], width=2)
            
            # Security patterns
            pattern_positions = [(width-80, 60), (width-60, 100), (width-100, 140)]
            for x, y in pattern_positions:
                # Warning triangles
                triangle_points = [(x, y), (x-10, y+15), (x+10, y+15)]
                draw.polygon(triangle_points, outline=colors['secondary'], width=2)
                draw.text((x-3, y+5), "!", fill=colors['accent'])
            
            # Firewall representation
            firewall_x = width - 120
            for i in range(5):
                y_pos = 40 + i * 15
                draw.line([(firewall_x, y_pos), (firewall_x+30, y_pos)], fill=colors['secondary'], width=2)
                draw.ellipse([firewall_x+35, y_pos-2, firewall_x+39, y_pos+2], fill=colors['accent'])
            
        except Exception as e:
            logger.error(f"Error drawing security elements: {e}")
    
    def _draw_web_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive web development themed elements"""
        try:
            # Enhanced browser window
            browser_x, browser_y = 30, 40
            window_width, window_height = 100, 80
            
            # Browser frame
            draw.rectangle([browser_x, browser_y, browser_x + window_width, browser_y + window_height], 
                          outline=colors['accent'], width=3)
            
            # Title bar
            draw.rectangle([browser_x, browser_y, browser_x + window_width, browser_y + 15], 
                          fill=colors['icon'])
            
            # Window controls
            for i in range(3):
                control_colors = [colors['secondary'], colors['accent'], colors['text']]
                draw.ellipse([browser_x + 5 + i*12, browser_y + 4, 
                             browser_x + 12 + i*12, browser_y + 11], fill=control_colors[i])
            
            # Address bar
            draw.rectangle([browser_x + 5, browser_y + 20, browser_x + window_width - 5, browser_y + 35], 
                          outline=colors['secondary'], width=1)
            
            # HTML tags representation
            tag_y = browser_y + 45
            tag_text = ["<html>", "<body>", "<div>"]
            for i, tag in enumerate(tag_text):
                y_pos = tag_y + i * 12
                draw.text((browser_x + 10, y_pos), tag, fill=colors['text'])
            
            # Responsive design indicators
            device_sizes = [(width-80, 50, 30, 20), (width-80, 80, 20, 15), (width-80, 105, 15, 10)]
            for x, y, w, h in device_sizes:
                draw.rectangle([x, y, x+w, y+h], outline=colors['secondary'], width=2)
                # Screen content
                draw.rectangle([x+2, y+2, x+w-2, y+h-2], fill=colors['icon'])
            
        except Exception as e:
            logger.error(f"Error drawing web elements: {e}")
    
    def _draw_mobile_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive mobile development themed elements"""
        try:
            # Multiple device outlines
            devices = [
                (50, 40, 25, 45),  # Phone
                (90, 35, 35, 50),  # Tablet
                (140, 50, 20, 35)  # Small phone
            ]
            
            for x, y, w, h in devices:
                # Device frame
                draw.rounded_rectangle([x, y, x+w, y+h], radius=3, outline=colors['accent'], width=2)
                
                # Screen
                screen_margin = 3
                draw.rectangle([x+screen_margin, y+screen_margin+5, 
                               x+w-screen_margin, y+h-screen_margin-5], fill=colors['icon'])
                
                # Home button
                button_x = x + w//2 - 2
                button_y = y + h - 3
                draw.ellipse([button_x, button_y, button_x+4, button_y+2], fill=colors['secondary'])
                
                # App icons on screen
                for row in range(2):
                    for col in range(2):
                        icon_x = x + screen_margin + 2 + col * 6
                        icon_y = y + screen_margin + 8 + row * 6
                        draw.rectangle([icon_x, icon_y, icon_x+4, icon_y+4], fill=colors['secondary'])
            
            # Signal bars
            signal_x = width - 80
            for i in range(4):
                bar_height = 5 + i * 3
                draw.rectangle([signal_x + i*4, 50 - bar_height, 
                               signal_x + i*4 + 2, 50], fill=colors['accent'])
            
            # App development workflow
            workflow_y = height - 60
            steps = ["Code", "Build", "Test", "Deploy"]
            for i, step in enumerate(steps):
                x_pos = 30 + i * 50
                draw.ellipse([x_pos, workflow_y, x_pos+20, workflow_y+20], 
                            outline=colors['secondary'], fill=colors['icon'], width=2)
                if i < len(steps) - 1:
                    draw.line([(x_pos+20, workflow_y+10), (x_pos+30, workflow_y+10)], 
                             fill=colors['accent'], width=2)
            
        except Exception as e:
            logger.error(f"Error drawing mobile elements: {e}")
    
    def _draw_cloud_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive cloud computing themed elements"""
        try:
            # Enhanced cloud shapes
            cloud_positions = [(60, 50), (width-120, 60), (100, height-80)]
            
            for x, y in cloud_positions:
                # Main cloud body
                draw.ellipse([x, y+10, x+40, y+25], fill=colors['icon'], outline=colors['accent'], width=2)
                # Cloud bumps
                draw.ellipse([x+8, y, x+25, y+15], fill=colors['icon'], outline=colors['accent'], width=2)
                draw.ellipse([x+20, y+5, x+35, y+20], fill=colors['icon'], outline=colors['accent'], width=2)
                
                # Data flow arrows
                for i in range(3):
                    arrow_y = y + 30 + i * 8
                    draw.polygon([(x+15, arrow_y), (x+25, arrow_y), (x+22, arrow_y+3), 
                                 (x+25, arrow_y+6), (x+15, arrow_y+6), (x+18, arrow_y+3)], 
                                fill=colors['secondary'])
            
            # Server racks
            rack_x = width - 100
            for i in range(3):
                rack_y = 40 + i * 25
                draw.rectangle([rack_x, rack_y, rack_x+30, rack_y+20], 
                              outline=colors['accent'], width=2)
                # Server indicators
                for j in range(4):
                    draw.ellipse([rack_x+5+j*5, rack_y+5, rack_x+7+j*5, rack_y+7], 
                                fill=colors['secondary'])
                    draw.ellipse([rack_x+5+j*5, rack_y+12, rack_x+7+j*5, rack_y+14], 
                                fill=colors['icon'])
            
            # Network connections
            connection_points = [(30, height//2), (width//2, 30), (width-30, height//2)]
            for i in range(len(connection_points)-1):
                start = connection_points[i]
                end = connection_points[i+1]
                draw.line([start, end], fill=colors['secondary'], width=2)
                # Data packets
                mid_x = (start[0] + end[0]) // 2
                mid_y = (start[1] + end[1]) // 2
                draw.rectangle([mid_x-3, mid_y-3, mid_x+3, mid_y+3], fill=colors['accent'])
            
        except Exception as e:
            logger.error(f"Error drawing cloud elements: {e}")
    
    def _draw_performance_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive performance optimization themed elements"""
        try:
            # Speed indicators / tachometer
            center_x, center_y = 80, 80
            radius = 30
            
            # Tachometer arc
            draw.arc([center_x-radius, center_y-radius, center_x+radius, center_y+radius], 
                    start=225, end=315, fill=colors['accent'], width=4)
            
            # Speed marks
            for i in range(5):
                angle = 225 + i * 22.5
                import math
                x1 = center_x + (radius-10) * math.cos(math.radians(angle))
                y1 = center_y + (radius-10) * math.sin(math.radians(angle))
                x2 = center_x + radius * math.cos(math.radians(angle))
                y2 = center_y + radius * math.sin(math.radians(angle))
                draw.line([(x1, y1), (x2, y2)], fill=colors['secondary'], width=2)
            
            # Needle pointing to high performance
            needle_angle = 280
            import math
            needle_x = center_x + (radius-5) * math.cos(math.radians(needle_angle))
            needle_y = center_y + (radius-5) * math.sin(math.radians(needle_angle))
            draw.line([(center_x, center_y), (needle_x, needle_y)], fill=colors['text'], width=3)
            
            # Performance graphs
            graph_x = width - 120
            graph_points = [(graph_x, 100), (graph_x+20, 80), (graph_x+40, 60), 
                           (graph_x+60, 45), (graph_x+80, 30)]
            
            for i in range(len(graph_points)-1):
                draw.line([graph_points[i], graph_points[i+1]], fill=colors['icon'], width=3)
            
            for point in graph_points:
                draw.ellipse([point[0]-3, point[1]-3, point[0]+3, point[1]+3], fill=colors['secondary'])
            
            # Optimization arrows
            for i in range(3):
                arrow_x = 40 + i * 60
                arrow_y = height - 40
                # Arrow shaft
                draw.line([(arrow_x, arrow_y), (arrow_x+20, arrow_y)], fill=colors['accent'], width=4)
                # Arrow head
                draw.polygon([(arrow_x+20, arrow_y), (arrow_x+25, arrow_y-5), (arrow_x+25, arrow_y+5)], 
                            fill=colors['accent'])
            
        except Exception as e:
            logger.error(f"Error drawing performance elements: {e}")
    
    def _draw_tutorial_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive tutorial/learning themed elements"""
        try:
            # Book icon
            book_x, book_y = 50, 50
            book_width, book_height = 30, 40
            
            # Book cover
            draw.rectangle([book_x, book_y, book_x+book_width, book_y+book_height], 
                          fill=colors['icon'], outline=colors['accent'], width=2)
            
            # Book spine
            draw.line([(book_x+5, book_y), (book_x+5, book_y+book_height)], fill=colors['secondary'], width=2)
            
            # Pages
            for i in range(3):
                page_x = book_x + 10 + i * 2
                draw.rectangle([page_x, book_y+5, page_x+15, book_y+book_height-5], 
                              outline=colors['secondary'], width=1)
            
            # Learning path / steps
            steps = [(120, 60), (160, 60), (200, 60), (240, 60)]
            for i, (x, y) in enumerate(steps):
                # Step circle
                draw.ellipse([x-8, y-8, x+8, y+8], fill=colors['icon'], outline=colors['accent'], width=2)
                draw.text((x-3, y-5), str(i+1), fill=colors['text'])
                
                # Connection line to next step
                if i < len(steps) - 1:
                    next_x = steps[i+1][0]
                    draw.line([(x+8, y), (next_x-8, y)], fill=colors['secondary'], width=2)
            
            # Lightbulb (idea/learning)
            bulb_x, bulb_y = width-80, 50
            # Bulb shape
            draw.ellipse([bulb_x, bulb_y, bulb_x+20, bulb_y+25], outline=colors['accent'], width=2)
            # Bulb base
            draw.rectangle([bulb_x+5, bulb_y+25, bulb_x+15, bulb_y+30], fill=colors['secondary'])
            # Light rays
            rays = [(-10, -10), (0, -15), (10, -10), (-15, 0), (25, 0)]
            for dx, dy in rays:
                ray_x, ray_y = bulb_x+10+dx, bulb_y+12+dy
                draw.line([(bulb_x+10, bulb_y+12), (ray_x, ray_y)], fill=colors['icon'], width=2)
            
            # Progress indicators
            progress_y = height - 40
            for i in range(6):
                x_pos = 40 + i * 30
                if i < 4:  # Completed
                    draw.ellipse([x_pos, progress_y, x_pos+8, progress_y+8], fill=colors['icon'])
                else:  # In progress
                    draw.ellipse([x_pos, progress_y, x_pos+8, progress_y+8], outline=colors['secondary'], width=2)
            
        except Exception as e:
            logger.error(f"Error drawing tutorial elements: {e}")
    
    def _draw_devops_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive DevOps themed elements"""
        try:
            # CI/CD Pipeline
            pipeline_stages = ["Code", "Build", "Test", "Deploy"]
            stage_width = 60
            stage_height = 25
            start_x = 30
            pipeline_y = 50
            
            for i, stage in enumerate(pipeline_stages):
                x = start_x + i * (stage_width + 10)
                
                # Stage box
                draw.rectangle([x, pipeline_y, x+stage_width, pipeline_y+stage_height], 
                              fill=colors['icon'], outline=colors['accent'], width=2)
                
                # Pipeline connector
                if i < len(pipeline_stages) - 1:
                    connector_x = x + stage_width
                    draw.polygon([(connector_x, pipeline_y+5), (connector_x+10, pipeline_y+stage_height//2), 
                                 (connector_x, pipeline_y+stage_height-5)], fill=colors['secondary'])
                
                # Status indicator
                status_colors = [colors['icon'], colors['secondary'], colors['accent'], colors['text']]
                draw.ellipse([x+stage_width-10, pipeline_y+3, x+stage_width-3, pipeline_y+10], 
                            fill=status_colors[i])
            
            # Infrastructure elements
            # Docker containers
            container_y = 120
            for i in range(3):
                cont_x = 50 + i * 40
                draw.rectangle([cont_x, container_y, cont_x+30, container_y+20], 
                              outline=colors['accent'], width=2)
                # Container layers
                for j in range(2):
                    draw.line([(cont_x+5, container_y+5+j*5), (cont_x+25, container_y+5+j*5)], 
                             fill=colors['secondary'], width=1)
            
            # Monitoring graphs
            monitor_x = width - 100
            monitor_y = 100
            
            # CPU usage
            cpu_points = [(monitor_x, monitor_y), (monitor_x+15, monitor_y-10), 
                         (monitor_x+30, monitor_y-5), (monitor_x+45, monitor_y-15)]
            for i in range(len(cpu_points)-1):
                draw.line([cpu_points[i], cpu_points[i+1]], fill=colors['icon'], width=2)
            
            # Memory usage
            mem_y = monitor_y + 20
            mem_points = [(monitor_x, mem_y), (monitor_x+15, mem_y-8), 
                         (monitor_x+30, mem_y-12), (monitor_x+45, mem_y-6)]
            for i in range(len(mem_points)-1):
                draw.line([mem_points[i], mem_points[i+1]], fill=colors['secondary'], width=2)
            
            # Automation gears
            gear_centers = [(width-50, 50), (width-30, 70)]
            for center in gear_centers:
                # Gear outline
                draw.ellipse([center[0]-12, center[1]-12, center[0]+12, center[1]+12], 
                            outline=colors['accent'], width=2)
                # Gear teeth (simplified)
                for angle in range(0, 360, 45):
                    import math
                    x = center[0] + 15 * math.cos(math.radians(angle))
                    y = center[1] + 15 * math.sin(math.radians(angle))
                    draw.ellipse([x-2, y-2, x+2, y+2], fill=colors['secondary'])
            
        except Exception as e:
            logger.error(f"Error drawing devops elements: {e}")
    
    def _draw_ai_ml_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive AI/ML themed elements"""
        try:
            # Neural network with multiple layers
            layer_positions = [
                [(60, 60), (60, 100), (60, 140)],  # Input layer
                [(120, 50), (120, 80), (120, 110), (120, 140)],  # Hidden layer 1
                [(180, 60), (180, 100), (180, 140)],  # Hidden layer 2
                [(240, 80), (240, 120)]  # Output layer
            ]
            
            # Draw connections
            for layer_idx in range(len(layer_positions)-1):
                current_layer = layer_positions[layer_idx]
                next_layer = layer_positions[layer_idx+1]
                for node1 in current_layer:
                    for node2 in next_layer:
                        # Varying line thickness for weight representation
                        thickness = random.choice([1, 2, 3])
                        draw.line([node1, node2], fill=colors['secondary'], width=thickness)
            
            # Draw nodes
            for layer in layer_positions:
                for node in layer:
                    draw.ellipse([node[0]-6, node[1]-6, node[0]+6, node[1]+6], 
                                fill=colors['icon'], outline=colors['accent'], width=2)
            
            # Brain representation
            brain_x, brain_y = width-100, 50
            # Brain outline (simplified)
            brain_points = [
                (brain_x, brain_y+20), (brain_x-10, brain_y+10), (brain_x-15, brain_y),
                (brain_x-10, brain_y-10), (brain_x+10, brain_y-15), (brain_x+25, brain_y-10),
                (brain_x+30, brain_y), (brain_x+25, brain_y+10), (brain_x+15, brain_y+25),
                (brain_x, brain_y+20)
            ]
            draw.polygon(brain_points, outline=colors['accent'], width=2)
            
            # Brain folds
            fold_lines = [
                [(brain_x-5, brain_y), (brain_x+5, brain_y+5)],
                [(brain_x, brain_y-5), (brain_x+10, brain_y)],
                [(brain_x+5, brain_y+10), (brain_x+15, brain_y+15)]
            ]
            for line in fold_lines:
                draw.line(line, fill=colors['secondary'], width=2)
            
            # Data processing flow
            data_y = height - 60
            process_steps = ["Data", "Train", "Model", "Predict"]
            for i, step in enumerate(process_steps):
                x_pos = 40 + i * 60
                
                # Process box
                draw.rectangle([x_pos, data_y, x_pos+40, data_y+20], 
                              fill=colors['icon'], outline=colors['accent'], width=2)
                
                # Data flow arrow
                if i < len(process_steps) - 1:
                    arrow_start = x_pos + 40
                    arrow_end = x_pos + 60
                    draw.line([(arrow_start, data_y+10), (arrow_end-5, data_y+10)], 
                             fill=colors['secondary'], width=2)
                    draw.polygon([(arrow_end-5, data_y+7), (arrow_end, data_y+10), (arrow_end-5, data_y+13)], 
                                fill=colors['secondary'])
            
            # Algorithm visualization (decision tree)
            tree_x, tree_y = 50, height - 120
            # Root node
            draw.ellipse([tree_x-8, tree_y-8, tree_x+8, tree_y+8], 
                        fill=colors['icon'], outline=colors['accent'], width=2)
            
            # Branches
            branches = [
                (tree_x, tree_y, tree_x-30, tree_y+30),
                (tree_x, tree_y, tree_x+30, tree_y+30),
                (tree_x-30, tree_y+30, tree_x-45, tree_y+60),
                (tree_x-30, tree_y+30, tree_x-15, tree_y+60),
                (tree_x+30, tree_y+30, tree_x+15, tree_y+60),
                (tree_x+30, tree_y+30, tree_x+45, tree_y+60)
            ]
            
            for x1, y1, x2, y2 in branches:
                draw.line([(x1, y1), (x2, y2)], fill=colors['secondary'], width=2)
                # Leaf nodes
                if y2 == tree_y + 60:  # Leaf level
                    draw.rectangle([x2-6, y2-6, x2+6, y2+6], 
                                  fill=colors['icon'], outline=colors['accent'], width=1)
                elif y2 == tree_y + 30:  # Intermediate level
                    draw.ellipse([x2-6, y2-6, x2+6, y2+6], 
                                fill=colors['icon'], outline=colors['accent'], width=1)
            
        except Exception as e:
            logger.error(f"Error drawing AI/ML elements: {e}")
    
    def _draw_tool_elements(self, draw, width: int, height: int, colors: dict):
        """Draw comprehensive tools/utilities themed elements"""
        try:
            # Toolbox
            toolbox_x, toolbox_y = 50, 60
            toolbox_width, toolbox_height = 50, 30
            
            # Toolbox body
            draw.rectangle([toolbox_x, toolbox_y, toolbox_x+toolbox_width, toolbox_y+toolbox_height], 
                          fill=colors['icon'], outline=colors['accent'], width=2)
            
            # Toolbox handle
            handle_y = toolbox_y - 8
            draw.arc([toolbox_x+10, handle_y, toolbox_x+40, toolbox_y+5], 
                    start=0, end=180, fill=colors['secondary'], width=3)
            
            # Tools sticking out
            tools = [
                (toolbox_x+10, toolbox_y-15, toolbox_x+10, toolbox_y-5),  # Screwdriver
                (toolbox_x+20, toolbox_y-12, toolbox_x+20, toolbox_y-2),  # Another tool
                (toolbox_x+30, toolbox_y-18, toolbox_x+30, toolbox_y-8)   # Wrench handle
            ]
            
            for x1, y1, x2, y2 in tools:
                draw.line([(x1, y1), (x2, y2)], fill=colors['secondary'], width=3)
            
            # Gear/settings icons
            gear_positions = [(width-80, 60), (width-50, 90), (width-110, 120)]
            for gear_x, gear_y in gear_positions:
                # Main gear circle
                draw.ellipse([gear_x-15, gear_y-15, gear_x+15, gear_y+15], 
                            outline=colors['accent'], width=2)
                
                # Gear teeth
                teeth_angles = [0, 45, 90, 135, 180, 225, 270, 315]
                for angle in teeth_angles:
                    import math
                    tooth_x = gear_x + 18 * math.cos(math.radians(angle))
                    tooth_y = gear_y + 18 * math.sin(math.radians(angle))
                    draw.rectangle([tooth_x-2, tooth_y-2, tooth_x+2, tooth_y+2], fill=colors['secondary'])
                
                # Center hole
                draw.ellipse([gear_x-4, gear_y-4, gear_x+4, gear_y+4], fill=colors['icon'])
            
            # Plugin/extension representation
            plugin_y = height - 80
            plugin_elements = [
                (60, plugin_y, 20, 15),   # Main plugin
                (90, plugin_y+5, 15, 10), # Connected module
                (115, plugin_y+2, 18, 12) # Another module
            ]
            
            for x, y, w, h in plugin_elements:
                # Plugin block
                draw.rectangle([x, y, x+w, y+h], fill=colors['icon'], outline=colors['accent'], width=2)
                
                # Connection ports
                for port in range(3):
                    port_x = x + 3 + port * 5
                    draw.ellipse([port_x, y+h-3, port_x+2, y+h-1], fill=colors['secondary'])
            
            # Connection lines between plugins
            draw.line([(80, plugin_y+7), (90, plugin_y+10)], fill=colors['secondary'], width=2)
            draw.line([(105, plugin_y+10), (115, plugin_y+8)], fill=colors['secondary'], width=2)
            
            # Utility icons
            utility_positions = [(150, 80), (180, 100), (210, 85)]
            utility_icons = ['⚙', '🔧', '⚡']  # Simplified representations
            
            for i, (x, y) in enumerate(utility_positions):
                # Icon background
                draw.ellipse([x-10, y-10, x+10, y+10], fill=colors['icon'], outline=colors['secondary'], width=2)
                
                # Simple geometric representation instead of emoji
                if i == 0:  # Settings
                    draw.rectangle([x-4, y-4, x+4, y+4], outline=colors['accent'], width=2)
                elif i == 1:  # Tool
                    draw.line([(x-6, y-6), (x+6, y+6)], fill=colors['accent'], width=3)
                    draw.ellipse([x+4, y+4, x+8, y+8], outline=colors['accent'], width=2)
                else:  # Power/Speed
                    draw.polygon([(x-6, y), (x, y-8), (x+6, y), (x, y+8)], fill=colors['accent'])
            
        except Exception as e:
            logger.error(f"Error drawing tool elements: {e}")
    
    # Helper methods for different thematic elements (keeping existing ones)
    
    def _draw_mobile_elements(self, draw, width: int, height: int, color: str):
        """Draw mobile device outlines"""
        try:
            # Phone outline
            draw.rounded_rectangle([width-80, 40, width-40, 120], radius=10, outline=color, width=2)
            # Screen
            draw.rectangle([width-75, 50, width-45, 100], outline=color, width=1)
            # Home button
            draw.ellipse([width-65, 105, width-55, 115], outline=color)
        except Exception as e:
            logger.error(f"Error drawing mobile elements: {e}")
    
    def _draw_cloud_shapes(self, draw, width: int, height: int, color: str):
        """Draw cloud shapes for cloud theme"""
        try:
            # Simple cloud outline using arcs
            draw.arc([30, 50, 70, 80], 0, 180, fill=color, width=2)
            draw.arc([50, 45, 90, 75], 0, 180, fill=color, width=2)
            draw.arc([70, 50, 110, 80], 0, 180, fill=color, width=2)
        except Exception as e:
            logger.error(f"Error drawing cloud shapes: {e}")
    
    def _draw_performance_arrows(self, draw, width: int, height: int, color: str):
        """Draw speed/performance arrows"""
        try:
            # Right-pointing arrows
            for i in range(3):
                y_pos = 60 + i * 15
                draw.polygon([(width-100, y_pos), (width-80, y_pos-5), (width-80, y_pos-2), 
                             (width-60, y_pos-2), (width-60, y_pos+2), (width-80, y_pos+2), 
                             (width-80, y_pos+5)], fill=color)
        except Exception as e:
            logger.error(f"Error drawing performance arrows: {e}")
    
    def _draw_learning_elements(self, draw, width: int, height: int, color: str):
        """Draw learning/education elements"""
        try:
            # Book outline
            draw.rectangle([40, 50, 80, 90], outline=color, width=2)
            # Book pages
            draw.line([(45, 55), (45, 85)], fill=color, width=1)
            draw.line([(50, 55), (50, 85)], fill=color, width=1)
            # Bookmark
            draw.polygon([(75, 50), (85, 50), (85, 70), (80, 65), (75, 70)], fill=color)
        except Exception as e:
            logger.error(f"Error drawing learning elements: {e}")
    
    def _draw_tool_elements(self, draw, width: int, height: int, color: str):
        """Draw tool/gear elements"""
        try:
            # Simple gear outline
            center = (60, 70)
            radius = 15
            # Outer gear teeth
            for i in range(8):
                angle = i * 45
                import math
                x1 = center[0] + radius * math.cos(math.radians(angle))
                y1 = center[1] + radius * math.sin(math.radians(angle))
                x2 = center[0] + (radius + 5) * math.cos(math.radians(angle))
                y2 = center[1] + (radius + 5) * math.sin(math.radians(angle))
                draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
            # Center circle
            draw.ellipse([center[0]-8, center[1]-8, center[0]+8, center[1]+8], outline=color, width=2)
        except Exception as e:
            logger.error(f"Error drawing tool elements: {e}")

    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Create a temporary image to measure text
            if PIL_AVAILABLE:
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                # Rough estimation if PIL is not available
                text_width = len(test_line) * 8  # Approximate character width
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _add_decorative_elements(self, draw, width: int, height: int, accent_color: str):
        """Add decorative elements to the image"""
        try:
            # Add corner decorations
            corner_size = 60
            
            # Top-left corner
            draw.arc([10, 10, corner_size, corner_size], 180, 270, fill=accent_color, width=3)
            
            # Top-right corner
            draw.arc([width-corner_size, 10, width-10, corner_size], 270, 360, fill=accent_color, width=3)
            
            # Bottom-left corner
            draw.arc([10, height-corner_size, corner_size, height-10], 90, 180, fill=accent_color, width=3)
            
            # Bottom-right corner
            draw.arc([width-corner_size, height-corner_size, width-10, height-10], 0, 90, fill=accent_color, width=3)
            
        except Exception as e:
            logger.error(f"Error adding decorative elements: {e}")
    
    def _get_placeholder_filename(self) -> str:
        """Get the default placeholder filename"""
        # Check if we have a JPG placeholder, if not use a generic one
        jpg_path = os.path.join(self.placeholder_dir, 'default.jpg')
        if os.path.exists(jpg_path):
            return 'images/placeholders/default.jpg'
        else:
            # Return a CSS-generated placeholder or generic image
            return 'images/placeholders/default.jpg'  # We'll handle missing files in the template
    
    def generate_image(self, title: str, description: str = "", post_url: str = "") -> str:
        """
        Generate an image for a blog post
        Returns the relative path to the generated image
        """
        if not self.enabled:
            logger.info("Image generation is disabled")
            return self._get_placeholder_filename()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(title, description)
            if cache_key in self.cache:
                cached_file = self.cache[cache_key]
                cached_path = os.path.join('app/static/images', cached_file)
                if os.path.exists(cached_path):
                    logger.info(f"Using cached image for: {title}")
                    return f"images/{cached_file}"
            
            logger.info(f"Generating image for: {title}")
            
            # For now, create a text-based image if PIL is available, otherwise use placeholder
            if PIL_AVAILABLE:
                filename = self._create_text_based_image(title, description)
                # Update cache
                self.cache[cache_key] = filename
                self._save_cache()
                return f"images/generated/{filename}"
            else:
                # Use placeholder when PIL is not available
                logger.info(f"PIL not available, using placeholder for: {title}")
                return self._get_placeholder_filename()
            
        except Exception as e:
            logger.error(f"Error generating image for '{title}': {e}")
            return self._get_placeholder_filename()
    
    def cleanup_old_images(self, days_old: int = 30):
        """Clean up old generated images"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            for filename in os.listdir(self.image_dir):
                filepath = os.path.join(self.image_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old image: {filename}")
                        
                        # Remove from cache
                        for key, cached_file in list(self.cache.items()):
                            if cached_file == filename:
                                del self.cache[key]
                                break
            
            self._save_cache()
            
        except Exception as e:
            logger.error(f"Error cleaning up old images: {e}")

# Configuration for image generation
def get_image_config():
    """Get image configuration from environment or defaults"""
    try:
        from config import config
        app_config = config.get('development')()  # Instantiate the config class
        return {
            'enabled': app_config.IMAGE_GENERATION_ENABLED,
            'image_dir': app_config.GENERATED_IMAGES_DIR,
            'placeholder_dir': app_config.PLACEHOLDER_IMAGES_DIR,
            'cache_file': app_config.IMAGE_CACHE_FILE,
            'image_width': app_config.DEFAULT_IMAGE_WIDTH,
            'image_height': app_config.DEFAULT_IMAGE_HEIGHT,
            'image_quality': app_config.IMAGE_QUALITY,
            'api_key': app_config.OPENAI_API_KEY,
            'api_endpoint': '',
        }
    except (ImportError, Exception) as e:
        # Fallback configuration if config module is not available
        print(f"Using fallback image configuration: {e}")
        return {
            'enabled': True,
            'image_dir': 'app/static/images/generated',
            'placeholder_dir': 'app/static/images/placeholders',
            'cache_file': 'data/image_cache.json',
            'image_width': 800,
            'image_height': 400,
            'image_quality': 90,
            'api_key': '',
            'api_endpoint': '',
        }

IMAGE_CONFIG = get_image_config()

# Create global instance
image_generator = ImageGenerator(IMAGE_CONFIG)
