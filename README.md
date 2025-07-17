# Smart Split PWA

A simple Progressive Web App (PWA) template built with Flask. This template provides all the essential PWA features including offline functionality, installability, and responsive design.

## Features

- 📱 **Installable**: Can be installed on devices like a native app
- 🔄 **Offline Support**: Works even when offline using service workers
- ⚡ **Fast Loading**: Quick loading with efficient caching
- 📲 **Responsive**: Works great on all devices and screen sizes
- 🎨 **Modern UI**: Beautiful and modern user interface
- 🔔 **Push Notifications**: Ready for push notification implementation
- 🔄 **Background Sync**: Prepared for background synchronization

## Project Structure

```
smart-split/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html         # Base template with PWA features
│   ├── index.html        # Main page
│   └── offline.html      # Offline fallback page
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── js/
│   │   └── app.js       # PWA JavaScript functionality
│   ├── icons/           # PWA icons (various sizes)
│   ├── manifest.json    # PWA manifest file
│   └── sw.js           # Service worker
└── README.md           # This file
```

## Installation & Setup

### Option 1: Local Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:3000
   ```

### Option 2: Docker Installation

#### Development with Docker
1. **Clone the repository**

2. **Run with Docker Compose (Development):**
   ```bash
   docker-compose up --build
   ```
   This will start the app in development mode with hot reloading.

3. **Open your browser and navigate to:**
   ```
   http://localhost:3000
   ```

#### Production with Docker
1. **Run with production configuration:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

2. **Or build and run manually:**
   ```bash
   # Build the image
   docker build -t smart-split .
   
   # Run the container
   docker run -d \
     --name smart-split-app \
     -p 3000:3000 \
     -v $(pwd)/data:/app/data \
     -e SECRET_KEY=your-production-secret-key \
     smart-split
   ```

#### Docker Commands
- **Stop containers:** `docker-compose down`
- **View logs:** `docker-compose logs -f`
- **Rebuild:** `docker-compose up --build`
- **Production logs:** `docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f`

#### Environment Variables
Set these environment variables for production:
- `SECRET_KEY`: Your Flask secret key (required for production)
- `DATABASE`: Database file path (default: `/app/data/splitwise.db`)
- `FLASK_ENV`: Set to `production` for production deployment

## PWA Features

### Service Worker
- Caches static assets for offline use
- Provides offline fallback pages
- Implements cache-first strategy for better performance

### Web App Manifest
- Defines app metadata (name, icons, theme colors)
- Enables "Add to Home Screen" functionality
- Configures standalone display mode

### Responsive Design
- Mobile-first approach
- Flexible grid layout
- Touch-friendly interface

### Install Prompt
- Custom install button when PWA is installable
- Handles browser install events
- Cross-platform compatibility

## API Endpoints

- `GET /` - Main application page
- `GET /offline` - Offline fallback page
- `GET /manifest.json` - PWA manifest file
- `GET /sw.js` - Service worker script
- `GET /api/data` - Sample API endpoint

## Customization

### Changing App Details
1. Update `manifest.json` with your app's name, description, and theme colors
2. Replace icons in `static/icons/` with your own (maintain same sizes)
3. Update the title and content in templates
4. Modify CSS variables in `style.css` for custom theming

### Adding New Features
1. Add new routes in `app.py`
2. Create corresponding templates in `templates/`
3. Update the service worker cache list if needed
4. Add new API endpoints as required

### Deployment
For production deployment:

#### Traditional Deployment
1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:3000 app:app
   ```

#### Docker Deployment (Recommended)
1. Use the production Docker configuration:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```
2. Set the `SECRET_KEY` environment variable:
   ```bash
   export SECRET_KEY=your-secure-production-key
   ```

#### General Requirements
1. Configure HTTPS (required for PWA features)
2. Update manifest start_url for your domain
3. Ensure database persistence (Docker volumes handle this automatically)

## Browser Support

This PWA works on all modern browsers that support:
- Service Workers
- Web App Manifest
- Cache API
- Fetch API

### Supported Browsers:
- Chrome 40+
- Firefox 44+
- Safari 11.1+
- Edge 17+

## Testing PWA Features

1. **Install Prompt**: Visit the site on a supported mobile browser
2. **Offline Functionality**: Turn off network connection and reload
3. **Service Worker**: Check browser developer tools → Application → Service Workers
4. **Manifest**: Check browser developer tools → Application → Manifest

## Development

### Running in Development
```bash
python app.py
```

### Testing Service Worker
1. Open Chrome DevTools
2. Go to Application tab
3. Check Service Workers section
4. Use "Offline" checkbox to test offline functionality

### Lighthouse Audit
Run a Lighthouse audit to check PWA compliance:
1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run "Progressive Web App" audit

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the browser console for error messages
2. Verify HTTPS is enabled (required for PWA features)
3. Test in multiple browsers
4. Check service worker registration status