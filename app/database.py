"""
Database operations for blog posts
Handles SQLite database operations including storage and retrieval of blog posts
"""

import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BlogDatabase:
    def __init__(self, db_path: str = "data/blog_posts.db"):
        self.db_path = db_path
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create necessary database tables"""
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS blog_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    description TEXT,
                    full_content TEXT,
                    published_date TEXT,
                    thumbnail TEXT,
                    scraped_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster URL lookups
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_blog_posts_url 
                ON blog_posts(url)
            ''')
            
            conn.commit()
            logger.info("Database tables created/verified")
    
    def insert_post(self, post: Dict) -> bool:
        """Insert a single blog post, avoiding duplicates"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO blog_posts 
                    (title, url, description, full_content, published_date, thumbnail, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post['title'],
                    post['url'],
                    post['description'],
                    post.get('full_content'),
                    post.get('published_date'),
                    post.get('thumbnail'),
                    post['scraped_at']
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting post: {e}")
            return False
    
    def insert_posts_batch(self, posts: List[Dict]) -> int:
        """Insert multiple blog posts, return count of inserted posts"""
        inserted_count = 0
        for post in posts:
            if self.insert_post(post):
                inserted_count += 1
        
        logger.info(f"Inserted {inserted_count} out of {len(posts)} posts")
        return inserted_count
    
    def get_post_by_id(self, post_id: int) -> Optional[Dict]:
        """Get a single post by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM blog_posts WHERE id = ?', 
                    (post_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error fetching post by ID: {e}")
            return None
    
    def get_all_posts(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """Get all posts with optional pagination"""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT * FROM blog_posts 
                    ORDER BY created_at DESC
                '''
                params = []
                
                if limit:
                    query += ' LIMIT ? OFFSET ?'
                    params.extend([limit, offset])
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error fetching posts: {e}")
            return []
    
    def search_posts(self, keyword: str) -> List[Dict]:
        """Search posts by keyword in title or description"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT * FROM blog_posts 
                    WHERE title LIKE ? OR description LIKE ? OR full_content LIKE ?
                    ORDER BY created_at DESC
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error searching posts: {e}")
            return []
    
    def get_total_posts_count(self) -> int:
        """Get total number of posts in database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM blog_posts')
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Error counting posts: {e}")
            return 0
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post by ID"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM blog_posts WHERE id = ?', (post_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting post: {e}")
            return False
    
    def clear_all_posts(self) -> bool:
        """Clear all posts from database"""
        try:
            with self.get_connection() as conn:
                conn.execute('DELETE FROM blog_posts')
                conn.commit()
                logger.info("All posts cleared from database")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error clearing posts: {e}")
            return False
    
    def get_latest_scrape_time(self) -> Optional[str]:
        """Get the timestamp of the most recent scrape"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    'SELECT MAX(scraped_at) FROM blog_posts'
                )
                result = cursor.fetchone()[0]
                return result
        except sqlite3.Error as e:
            logger.error(f"Error fetching latest scrape time: {e}")
            return None

if __name__ == "__main__":
    # Test the database
    db = BlogDatabase()
    
    # Test post
    test_post = {
        'title': 'Test Blog Post',
        'url': 'https://testguild.com/test-post',
        'description': 'This is a test blog post description.',
        'published_date': '2024-01-15',
        'thumbnail': 'https://testguild.com/test-image.jpg',
        'scraped_at': datetime.now().isoformat()
    }
    
    # Insert test post
    if db.insert_post(test_post):
        print("Test post inserted successfully")
    
    # Fetch all posts
    posts = db.get_all_posts()
    print(f"Total posts in database: {len(posts)}")
    
    for post in posts:
        print(f"- {post['title']}")
