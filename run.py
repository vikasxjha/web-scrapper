#!/usr/bin/env python3
"""
TestGuild Blog Scraper
Main entry point for the Flask application
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
