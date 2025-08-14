"""
Flask Web Application for Blog Post Viewer
Main application with routes and web interface
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import logging
import os
from typing import Optional

from app.scraper import BlogScraper
from app.database import BlogDatabase
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app_config = config.get(config_name, config['default'])
    app.config.from_object(app_config)
    
    # Set secret key
    app.secret_key = app_config.SECRET_KEY
    
    # Initialize components with configuration
    scraper = BlogScraper()
    db = BlogDatabase(app_config.DATABASE_PATH)
    
    return app, scraper, db

# Create app instance
app, scraper, db = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.route('/')
def index():
    """Home page showing one blog post at a time"""
    # Get current post index from query parameter
    current_index = request.args.get('index', 0, type=int)
    
    # Get all posts
    posts = db.get_all_posts()
    total_posts = len(posts)
    
    if total_posts == 0:
        return render_template('index.html', 
                             post=None, 
                             current_index=0, 
                             total_posts=0,
                             message="No blog posts found. Click 'Refresh Data' to scrape posts.")
    
    # Handle index bounds
    if current_index < 0:
        current_index = 0
    elif current_index >= total_posts:
        current_index = total_posts - 1
    
    current_post = posts[current_index]
    
    return render_template('index.html',
                         post=current_post,
                         current_index=current_index,
                         total_posts=total_posts,
                         has_previous=current_index > 0,
                         has_next=current_index < total_posts - 1)

@app.route('/refresh')
def refresh_data():
    """Refresh blog posts by scraping the website"""
    try:
        logger.info("Starting manual refresh of blog posts")
        
        # Scrape new posts
        posts = scraper.scrape_all_posts()
        
        if not posts:
            flash("No posts found during scraping. The website might be unavailable.", "warning")
            return redirect(url_for('index'))
        
        # Insert into database
        inserted_count = db.insert_posts_batch(posts)
        
        if inserted_count > 0:
            flash(f"Successfully refreshed! Added/updated {inserted_count} blog posts.", "success")
        else:
            flash("Refresh completed, but no new posts were found.", "info")
            
    except Exception as e:
        logger.error(f"Error during refresh: {e}")
        flash(f"Error during refresh: {str(e)}", "error")
    
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """Search blog posts by keyword"""
    keyword = request.args.get('q', '').strip()
    
    if not keyword:
        flash("Please enter a search keyword.", "warning")
        return redirect(url_for('index'))
    
    # Search posts
    posts = db.search_posts(keyword)
    
    return render_template('search_results.html',
                         posts=posts,
                         keyword=keyword,
                         total_results=len(posts))

@app.route('/all')
def view_all():
    """View all blog posts in a list"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    posts = db.get_all_posts(limit=per_page, offset=offset)
    total_posts = db.get_total_posts_count()
    total_pages = (total_posts + per_page - 1) // per_page
    
    return render_template('all_posts.html',
                         posts=posts,
                         current_page=page,
                         total_pages=total_pages,
                         has_previous=page > 1,
                         has_next=page < total_pages)

@app.route('/api/posts')
def api_posts():
    """API endpoint to get posts (for infinite scroll)"""
    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page
    
    posts = db.get_all_posts(limit=per_page, offset=offset)
    total_posts = db.get_total_posts_count()
    
    return jsonify({
        'posts': posts,
        'current_page': page,
        'total_posts': total_posts,
        'has_more': offset + len(posts) < total_posts
    })

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """API endpoint to refresh blog posts"""
    try:
        posts = scraper.scrape_all_posts()
        inserted_count = db.insert_posts_batch(posts)
        
        return jsonify({
            'success': True,
            'message': f'Refreshed! Added/updated {inserted_count} posts.',
            'inserted_count': inserted_count
        })
        
    except Exception as e:
        logger.error(f"API refresh error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error during refresh: {str(e)}'
        }), 500

@app.route('/stats')
def stats():
    """Show statistics about scraped posts"""
    total_posts = db.get_total_posts_count()
    latest_scrape = db.get_latest_scrape_time()
    
    return render_template('stats.html', stats=stats)

@app.route('/api/generate-image/<int:post_id>', methods=['POST'])
def generate_image_for_post(post_id):
    """Generate image for a specific post on demand"""
    try:
        # Get the post from database
        post = db.get_post_by_id(post_id)
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Generate image
        from app.image_generator import image_generator
        image_path = image_generator.generate_image(
            title=post['title'],
            description=post.get('description', ''),
            post_url=post['url']
        )
        
        # Update database with new image path
        success = db.update_post_image(post_id, image_path)
        
        if success:
            logger.info(f"Generated image for post {post_id}: {image_path}")
            return jsonify({
                'success': True, 
                'image_path': image_path,
                'message': 'Image generated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update database'}), 500
            
    except Exception as e:
        logger.error(f"Error generating image for post {post_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/regenerate-image/<int:post_id>', methods=['POST'])
def regenerate_image_for_post(post_id):
    """Regenerate image for a specific post (bypass cache)"""
    try:
        # Get the post from database
        post = db.get_post_by_id(post_id)
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        # Clear cache for this post to force regeneration
        from app.image_generator import image_generator
        cache_key = image_generator._generate_cache_key(post['title'], post.get('description', ''))
        if cache_key in image_generator.cache:
            del image_generator.cache[cache_key]
            image_generator._save_cache()
        
        # Generate new image
        image_path = image_generator.generate_image(
            title=post['title'],
            description=post.get('description', ''),
            post_url=post['url']
        )
        
        # Update database with new image path
        success = db.update_post_image(post_id, image_path)
        
        if success:
            logger.info(f"Regenerated image for post {post_id}: {image_path}")
            return jsonify({
                'success': True, 
                'image_path': image_path,
                'message': 'Image regenerated successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to update database'}), 500
            
    except Exception as e:
        logger.error(f"Error regenerating image for post {post_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500

# Template filters
@app.template_filter('datetime')
def datetime_filter(date_string):
    """Format datetime string for display"""
    if not date_string:
        return "Unknown date"
    
    try:
        # Parse ISO format
        if 'T' in date_string:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        else:
            return date_string
    except:
        return date_string

@app.template_filter('truncate_words')
def truncate_words_filter(text, length=20):
    """Truncate text to specified number of words"""
    if not text:
        return ""
    
    words = text.split()
    if len(words) <= length:
        return text
    
    return ' '.join(words[:length]) + '...'

if __name__ == '__main__':
    # Initialize with some data if database is empty
    if db.get_total_posts_count() == 0:
        logger.info("Database is empty, performing initial scrape...")
        try:
            posts = scraper.scrape_all_posts()
            if posts:
                db.insert_posts_batch(posts)
                logger.info(f"Initial scrape completed with {len(posts)} posts")
        except Exception as e:
            logger.error(f"Initial scrape failed: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
