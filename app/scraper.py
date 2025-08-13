"""
Blog Post Scraper for TestGuild
Extracts blog posts from https://testguild.com/blog/
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Optional
from cachetools import TTLCache
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for 30 minutes
cache = TTLCache(maxsize=100, ttl=1800)

class BlogScraper:
    def __init__(self, base_url: str = "https://testguild.com/blog/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page with caching"""
        if url in cache:
            logger.info(f"Using cached version of {url}")
            return cache[url]
        
        try:
            logger.info(f"Fetching {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cache[url] = soup
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_blog_posts(self) -> List[Dict]:
        """Extract blog posts from the main blog page"""
        soup = self.fetch_page(self.base_url)
        if not soup:
            return []
        
        posts = []
        
        # Look for blog post containers - adjust selectors based on actual site structure
        post_containers = soup.find_all(['article', 'div'], class_=re.compile(r'post|article|blog', re.I))
        
        if not post_containers:
            # Fallback: look for common blog post patterns
            post_containers = soup.find_all('div', class_=re.compile(r'entry|item|card', re.I))
        
        for container in post_containers:
            post_data = self.extract_post_data(container)
            if post_data:
                posts.append(post_data)
        
        return posts
    
    def extract_post_data(self, container) -> Optional[Dict]:
        """Extract individual post data from a container element"""
        try:
            # Extract title and URL
            title_elem = container.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|heading', re.I))
            if not title_elem:
                title_elem = container.find(['h1', 'h2', 'h3', 'h4'])
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # Find the link
            link_elem = title_elem.find('a') or container.find('a')
            if not link_elem:
                return None
            
            url = link_elem.get('href', '')
            if url.startswith('/'):
                url = 'https://testguild.com' + url
            elif not url.startswith('http'):
                url = 'https://testguild.com/blog/' + url
            
            # Extract description
            description = self.extract_description(container)
            
            # Extract date
            pub_date = self.extract_date(container)
            
            # Extract thumbnail
            thumbnail = self.extract_thumbnail(container)
            
            return {
                'title': title,
                'url': url,
                'description': description,
                'published_date': pub_date,
                'thumbnail': thumbnail,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None
    
    def extract_description(self, container) -> str:
        """Extract post description or excerpt"""
        # Look for description/excerpt elements
        desc_selectors = [
            'div.excerpt', 'div.description', 'p.excerpt',
            'div.summary', 'div.content', 'div.entry-content'
        ]
        
        for selector in desc_selectors:
            elem = container.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                return text[:300] + '...' if len(text) > 300 else text
        
        # Fallback: get first paragraph
        p_elem = container.find('p')
        if p_elem:
            text = p_elem.get_text(strip=True)
            return text[:300] + '...' if len(text) > 300 else text
        
        return "No description available"
    
    def extract_date(self, container) -> Optional[str]:
        """Extract publication date"""
        date_selectors = [
            'time', 'span.date', 'div.date', 'span.published',
            'div.published', 'span.post-date', 'div.post-date'
        ]
        
        for selector in date_selectors:
            elem = container.select_one(selector)
            if elem:
                # Try datetime attribute first
                date_str = elem.get('datetime') or elem.get_text(strip=True)
                return self.parse_date(date_str)
        
        return None
    
    def extract_thumbnail(self, container) -> Optional[str]:
        """Extract thumbnail image URL"""
        img_elem = container.find('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src')
            if src:
                if src.startswith('/'):
                    return 'https://testguild.com' + src
                elif src.startswith('http'):
                    return src
        
        return None
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats"""
        if not date_str:
            return None
        
        # Common date patterns
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # 2024-01-15
            r'\d{1,2}/\d{1,2}/\d{4}',  # 1/15/2024
            r'\d{1,2}-\d{1,2}-\d{4}',  # 1-15-2024
            r'[A-Za-z]+ \d{1,2}, \d{4}',  # January 15, 2024
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_str)
            if match:
                return match.group()
        
        return date_str[:20]  # Truncate if no pattern matches
    
    def scrape_all_posts(self) -> List[Dict]:
        """Main method to scrape all blog posts"""
        logger.info("Starting blog post scraping...")
        posts = self.extract_blog_posts()
        logger.info(f"Scraped {len(posts)} blog posts")
        return posts

if __name__ == "__main__":
    scraper = BlogScraper()
    posts = scraper.scrape_all_posts()
    for post in posts[:3]:  # Print first 3 posts
        print(f"Title: {post['title']}")
        print(f"URL: {post['url']}")
        print(f"Description: {post['description'][:100]}...")
        print("-" * 50)
