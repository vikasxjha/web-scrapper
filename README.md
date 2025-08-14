# TestGuild Blog Scraper

A modern Python web application that scrapes blog posts from TestGuild and displays them with a clean, responsive interface.

## Features

- **Web Scraping**: Extracts blog posts from https://testguild.com/blog/ using BeautifulSoup
- **Full Content Extraction**: Fetches complete article content from individual pages
- **Data Storage**: Stores posts in SQLite database with duplicate prevention
- **Modern UI**: Clean, responsive design using TailwindCSS
- **Multiple Views**:
  - Single post view with Previous/Next navigation and Summary/Full Content toggle
  - All posts list view with pagination and content toggles
  - Search functionality (searches titles, descriptions, and full content)
- **Caching**: 30-minute cache to reduce server load
- **Error Handling**: Graceful error handling with user-friendly messages
- **Keyboard Navigation**: Use arrow keys to navigate between posts## Project Structure

```
├── app/
│   ├── main.py           # Flask application and routes
│   ├── scraper.py        # Web scraping logic
│   ├── database.py       # Database operations
│   ├── templates/        # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── all_posts.html
│   │   ├── search_results.html
│   │   ├── stats.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── static/           # Static files (if needed)
├── data/                 # SQLite database storage
├── requirements.txt      # Python dependencies
├── run.py               # Application entry point
└── README.md           # This file
```

## Installation & Setup

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd testguild-blog-scraper

# Or download and extract the files
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using Flask directly
python -m flask --app app.main run --debug

# Option 3: Using the main module
python app/main.py
```

The application will start on `http://localhost:5000`

## Usage

### First Run

1. **Start the application** using one of the methods above
2. **Open your browser** and go to `http://localhost:5000`
3. **Click "Refresh Data"** to scrape blog posts from TestGuild
4. **Browse posts** using the navigation or explore different views

### Navigation

- **Home Page**: View one post at a time with Previous/Next buttons
- **All Posts**: Browse all posts in a paginated list
- **Search**: Search posts by keyword in title or description
- **Stats**: View scraping statistics and database information

### Keyboard Shortcuts

- **Left Arrow (←)**: Previous post (in single view)
- **Right Arrow (→)**: Next post (in single view)

## API Endpoints

The application also provides API endpoints for programmatic access:

- `GET /api/posts?page=1` - Get paginated posts
- `POST /api/refresh` - Trigger data refresh

## Configuration

### Environment Variables

You can customize the application using environment variables:

```bash
# Set Flask environment
export FLASK_ENV=development  # or production

# Set custom port
export FLASK_RUN_PORT=8000

# Set custom host
export FLASK_RUN_HOST=0.0.0.0
```

### Database Location

The SQLite database is stored in `data/blog_posts.db` by default. You can modify this in `app/database.py`.

## Features in Detail

### Web Scraping

- **Smart Extraction**: Uses CSS selectors and fallback patterns to extract post data
- **Full Content Fetching**: Visits individual article pages to extract complete content
- **Caching**: 30-minute TTL cache to avoid excessive requests
- **Error Handling**: Graceful handling of network errors and parsing issues
- **Rate Limiting**: Respectful scraping with proper delays

### Data Management

- **SQLite Database**: Lightweight, file-based storage
- **Duplicate Prevention**: URL-based uniqueness constraint
- **Efficient Queries**: Indexed database with optimized queries
- **Data Integrity**: Proper transaction handling

### User Interface

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Styling**: Clean interface using TailwindCSS
- **Content Toggle**: Switch between summary and full article content
- **Interactive Elements**: Hover effects, transitions, and animations
- **Accessibility**: Semantic HTML and keyboard navigation

## Troubleshooting

### Common Issues

1. **"No posts found"**

   - Click "Refresh Data" to scrape posts
   - Check internet connection
   - TestGuild website might be temporarily unavailable

2. **"Import errors"**

   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Activate virtual environment if using one

3. **"Permission denied" on database**

   - Ensure the `data/` directory is writable
   - Check file permissions

4. **"Port already in use"**
   - Use a different port: `python run.py` or set `FLASK_RUN_PORT`
   - Kill existing processes using the port

### Development Mode

For development with auto-reload:

```bash
export FLASK_ENV=development
python run.py
```

## Dependencies

- **Flask 2.3.3**: Web framework
- **requests 2.31.0**: HTTP library for scraping
- **beautifulsoup4 4.12.2**: HTML parsing
- **lxml 4.9.3**: XML/HTML parser
- **cachetools 5.3.1**: Caching utilities
- **python-dateutil 2.8.2**: Date parsing
- **Werkzeug 2.3.7**: WSGI utilities

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- **Fast Loading**: Optimized database queries and caching
- **Minimal Bandwidth**: TailwindCSS CDN and efficient asset loading
- **Responsive**: Smooth navigation and interactions

## Security Considerations

- Input validation for search queries
- SQL injection prevention with parameterized queries
- XSS protection with proper template escaping
- CSRF protection (built into Flask)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect TestGuild's robots.txt and terms of service when scraping their content.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Check the Flask and BeautifulSoup documentation

---

**Note**: This scraper is designed specifically for TestGuild's blog structure. If the website structure changes, the scraping selectors may need updates.
