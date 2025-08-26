# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Using Docker Compose (Recommended)
- **Start development environment**: `docker compose -f docker-compose.local.yml up --build`
- **Run Django management commands**: `docker compose -f docker-compose.local.yml run --rm django python manage.py <command>`
- **Run tests**: `docker compose -f docker-compose.local.yml run --rm django python manage.py test`
- **Create migrations**: `docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations`
- **Apply migrations**: `docker compose -f docker-compose.local.yml run --rm django python manage.py migrate`
- **Code linting**: `docker compose -f docker-compose.local.yml run --rm django ruff check .`
- **Code formatting**: `docker compose -f docker-compose.local.yml run --rm django ruff format .`

### Using Just Commands (Alternative)
- **Build containers**: `just build`
- **Start containers**: `just up`
- **Stop containers**: `just down`
- **Django commands**: `just django <command>`
- **Management commands**: `just manage <command>`

### Testing Framework
- **Test runner**: Django's built-in test framework with pytest configuration
- **Test settings**: Uses `config.settings.test` module
- **Run specific test**: `docker compose -f docker-compose.local.yml run --rm django python manage.py test <app.tests.test_module>`
- **Coverage**: pytest-cov is available for coverage reports

## Project Architecture

### Django Apps Structure
- **authentication/**: JWT-based auth with Firebase integration, custom User model extending AbstractUser
- **blogs/**: Blog posts with categories, pagination, and status management
- **coach/**: Core coach profiles with categories, reviews, media, and claim functionality
- **core/**: Contains base User model and shared utilities
- **events/**: Event management with participants and tickets
- **inquiries/**: General contact/inquiry system
- **notifications/**: User notification system
- **products/**: Product catalog with categories and media
- **quizzes/**: Quiz system with feedback and field management

### Key Models
- **User** (`core.users.models.User`): Custom user extending AbstractUser with phone number
- **Coach** (`coach.models.Coach`): Main coach profile with categories, reviews, and media
- **Category/Subcategory** (`coach.models`): Hierarchical categorization system
- **Profile** (`core.users.models.Profile`): Extended user profile information

### API Structure
- **REST Framework**: Uses DRF with JWT authentication
- **API Documentation**: Available at `/api/docs/` (Swagger/OpenAPI)
- **Authentication**: JWT tokens via rest_framework_simplejwt
- **Permissions**: Most endpoints require authentication
- **CORS**: Configured for frontend domains including localhost:3000

### Database & Storage
- **Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Media Files**: Stored in `core/media/` with organized subdirectories
- **Static Files**: Django's collectstatic with WhiteNoise for serving
- **File Uploads**: UUID-based filenames for security

### Background Tasks
- **Celery**: Configured with Redis broker for async tasks
- **Celery Beat**: Database scheduler for periodic tasks
- **Flower**: Task monitoring available in development

### Settings Configuration
- **Base settings**: `config/settings/base.py`
- **Local development**: `config/settings/local.py`
- **Production**: `config/settings/production.py`
- **Test**: `config/settings/test.py`
- **Environment variables**: Uses django-environ for configuration

### Code Quality Tools
- **Linter**: Ruff with extensive rule set (see pyproject.toml)
- **Type checking**: MyPy configured for Django projects
- **Template linting**: djLint for Django templates
- **Test framework**: pytest with Django plugin

## Important Conventions

### File Organization
- Apps follow standard Django structure with separate serializers/ directory for complex apps
- Media files use UUID-based naming for security
- Migrations are tracked and should be committed
- Factory Boy is used for test data generation

### Authentication
- JWT tokens with 1-hour access token lifetime, 30-day refresh
- Firebase integration available for social auth
- Email verification required for new accounts
- Custom verification code system for phone/email

### API Design
- RESTful endpoints following DRF conventions
- Consistent serializer structure across apps
- Pagination implemented where appropriate
- Filtering support via django-filter

### Development Environment
- Docker-based development with docker-compose.local.yml
- Hot reload enabled for Django development
- Redis for caching and Celery broker
- Admin interface at `/admin/` with django-unfold styling
