# RegexFlow
[![Watch the demo](https://github.com/CarlosFuSiCong/RegexFlow/raw/main/assets/RegexFlow.jpg)](https://github.com/CarlosFuSiCong/RegexFlow/raw/main/RegexFlow.mp4)
RegexFlow is a web application that helps users work with regular expressions, providing a modern and intuitive interface for testing, validating, and experimenting with regex patterns.

## Features

- Real-time regex pattern testing
- Visual pattern explanation
- Multiple test string support
- Pattern library and examples
- Cross-platform compatibility

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v18.0.0 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)
- Git

## Project Structure

```
RegexFlow/
├── frontend/         # Next.js frontend application
├── backend/         # Django backend application
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
   The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

## Development

To work on the project:

1. Frontend development:
   - The frontend uses Next.js with TypeScript
   - Styling is handled with Tailwind CSS
   - Run `npm run lint` to check for code style issues
   - Run `npm run build` to create a production build

2. Backend development:
   - The backend uses Django
   - API endpoints are documented at `/api/docs/` when the server is running
   - Run `python manage.py test` to run the test suite

## Production Deployment

For production deployment:

1. Frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Backend:
   - Set up appropriate environment variables
   - Configure a production-grade server (e.g., Gunicorn)
   - Use a reverse proxy (e.g., Nginx)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 