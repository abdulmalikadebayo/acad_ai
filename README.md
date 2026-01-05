# Mini Assessment Engine - Acad AI Backend Test Task

A Django-based REST API for automated academic assessment and grading, featuring LLM-powered evaluation, secure student submissions, and optimized database queries.

**📖 Full API Documentation**: [Postman Collection](https://documenter.getpostman.com/view/29745851/2sBXVcnYos)

## Features

- **Secure Authentication**: Token-based authentication with permission controls
- **Academic Assessment Flow**: Complete exam lifecycle from creation to graded submissions
- **Hybrid Grading System**: Deterministic MCQ grading + GPT-4o powered evaluation for essay questions
- **Query Optimization**: Advanced prefetching, bulk operations, and database indexing
- **Modular Architecture**: Clean separation of concerns with selectors, services, and grading providers

## Tech Stack

- **Framework**: Django 5.2.4 with Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Token Authentication (rest_framework.authtoken)
- **LLM Integration**: OpenAI GPT-4o
- **Python**: 3.12

## Architecture Highlights

### Project Structure
```
server/
├── src/
│   ├── config/              # Django project root
│   │   ├── settings.py      # Django settings, REST framework config
│   │   ├── urls.py          # Root URL configuration
│   │   └── wsgi.py/asgi.py  # WSGI/ASGI entry points
│   ├── assessments/         # Core assessment app
│   │   ├── models.py        # Course, Exam, Question, Submission models
│   │   ├── views.py         # REST API endpoints (5 views)
│   │   ├── serializers.py   # Request/response validation & nested serializers
│   │   ├── selectors.py     # Query optimization layer (prefetching)
│   │   ├── urls.py          # Assessment-specific routes
│   │   ├── constants.py     # Enums (QuestionType, SubmissionStatus)
│   │   ├── permissions.py   # Custom permission classes
│   │   ├── services/
│   │   │   └── submission_service.py  # Business logic for submissions
│   │   └── management/commands/
│   │       └── populate_sample_exam.py  # Sample data generation
│   ├── grading/             # Standalone grading module
│   │   ├── service.py       # Grading orchestration & result normalization
│   │   ├── providers/       # Pluggable grading implementations
│   │   │   ├── __init__.py
│   │   │   └── openai_provider.py  # GPT-4o integration
│   │   ├── prompt.py        # LLM prompt engineering
│   │   ├── dto.py           # Data transfer objects (GradeResult, PerQuestionGrade)
│   │   └── exceptions.py    # Custom grading exceptions
│   ├── user/                # User management app
│   │   ├── models.py        # Profile model
│   │   ├── api.py           # Registration/login endpoints
│   │   ├── serializers.py   # User serializers
│   │   └── urls.py          # User routes
│   ├── media/               # Uploaded files (if any)
│   └── db.sqlite3           # SQLite database (development)
├── Makefile                 # Convenience commands
├── Pipfile/Pipfile.lock     # Python dependencies
├── Dockerfile               # Container configuration
└── .env                     # Environment variables
```

### Key Directories Explained

- **config/** — Django project root containing settings, URL routing, and WSGI/ASGI entry points
- **assessments/** — Core assessment functionality: exam management, student submissions, validation, and API endpoints
- **grading/** — Modular grading engine with provider abstraction (currently OpenAI GPT-4o, extensible for mock providers)
- **user/** — User authentication and profile management (registration, login, token generation)
- **management/commands/** — Custom Django commands for populating sample data


### Database Optimization
- **Selectors Pattern**: Centralized query optimization with `select_related()` and `prefetch_related()`
- **Bulk Operations**: `bulk_create()` and `bulk_update()` for efficient writes
- **Strategic Indexing**: Composite indexes on frequently queried fields
- **N+1 Query Prevention**: Proper use of Django ORM prefetching

### Security Features
- Token authentication on all endpoints
- Permission checks ensuring students only access their own data
- Input validation via serializers
- Transaction atomicity with `@transaction.atomic`
- Unique constraints preventing duplicate submissions

## Setup Instructions

### Prerequisites
- Python 3.12+
- Pipenv (for dependency management)
- PostgreSQL (optional, SQLite works for development)

### Installation

1. **Clone the repository**
```bash
cd server
```

2. **Install dependencies**
```bash
pipenv install
pipenv shell
```

3. **Set up environment variables**

Create a `.env` file in the `server/` directory:
```bash

# Django
DEBUG=True
SECRET_KEY=your-secret-key-here-generate-with-django

# OpenAI (Required for LLM grading)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database (Optional, defaults to SQLite if not set)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

**Important**: The `OPENAI_API_KEY` is required for automated grading to work. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

4. **Run migrations**
```bash
make migrate
```

5. **Create sample data**
```bash
python src/manage.py populate_sample_exam
```

6. **Run the development server**
```bash
make run
```

The API will be available at `http://localhost:8001`

---

## CLI Commands & Makefile Targets

### Pipenv / Django Commands

| Command | Description |
|---------|-------------|
| `pipenv install` | Install all dependencies from Pipfile |
| `pipenv install --ignore-pipfile` | Install from Pipfile.lock (production) |
| `pipenv shell` | Activate virtual environment |
| `pipenv run python src/manage.py migrate` | Run database migrations |
| `pipenv run python src/manage.py makemigrations` | Create new migration files |
| `pipenv run python src/manage.py createsuperuser` | Create admin account |
| `pipenv run python src/manage.py runserver` | Start development server |
| `pipenv run python src/manage.py shell` | Open Django shell |
| `pipenv run python src/manage.py populate_sample_exam` | Load sample exam data |
| `pipenv run python src/manage.py test` | Run unit tests |
| `docker build -t acad_ai:latest .` | Build Docker image |
| `docker run --env-file .env -p 8001:8001 acad_ai` | Run Docker container |

---

### Makefile Commands (Convenience)

For easier development, use these make commands:

| Command | Description |
|---------|-------------|
| `make setup` | Complete setup: migrate + create superuser + run server |
| `make run` | Start development server on port 8001 |
| `make migrate` | Run makemigrations and migrate in one command |
| `make shell` | Open Django shell |
| `make superuser` | Create admin superuser (admin@admin.com / admin) |
| `make clean` | Remove SQLite database and Python cache files |
| `make collectstatic` | Collect static files for production deployment |
| `make run/gunicorn` | Run with Gunicorn for production (port 8000) |
| `make docker/build` | Build Docker image |
| `make tidy` | Format code with black, isort, and autoflake |

### Quick Start with Makefile
```bash
# One-command setup (runs migrations, creates superuser, starts server)
make setup

# Or step-by-step:
pipenv install
make migrate
pipenv run python src/manage.py populate_sample_exam
make run
```

---
| `make tidy` | Format code with black, isort, autoflake |

### Quick Start with Make
```bash
# Complete setup (migrate + superuser + run server)
make setup

# Or step by step:
make migrate
python src/manage.py populate_sample_exam
make run
```


## Project Requirements Met

- ✅ **Database Modeling**: Comprehensive schema with proper normalization, foreign keys, and indexes
- ✅ **Secure Endpoints**: Token authentication, permission checks, input validation
- ✅ **Automated Grading**: LLM integration with modular provider architecture
- ✅ **API Documentation**: Published Postman collection with examples
- ✅ **Query Optimization**: Selectors pattern, prefetching, bulk operations
- ✅ **Django Best Practices**: Generic views, serializers, service layer, transaction safety

