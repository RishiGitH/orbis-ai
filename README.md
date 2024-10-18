# ORBIS AI

A decentralized AI data labeling platform 

## Prerequisites

- Python 3.12+
- Django
- Celery
- Docker
- PostgreSQL
- Redis

## Setup

1. Clone the repository:
   ```
   git 
   cd orbis_ai
   ```

2. Install Poetry:
   ```
   pip install poetry
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Create a `.env` file in the project root and configure the environment variables (see `.env.example`).

5. Activate the virtual environment:
   ```
   poetry shell
   ```

6. Run database migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

## Running the Project

1. Start the Django development server:
   ```
   python manage.py runserver
   ```

2. Start the Celery worker:
   ```
   celery -A config worker -l info
   ```

3. (Optional) Start the Celery beat scheduler:
   ```
   celery -A config beat -l info
   ```

4. Access the API at `http://localhost:8000/api/`
5. Access the Swagger documentation at `http://localhost:8000/swagger/`
6. Access the ReDoc documentation at `http://localhost:8000/redoc/`

## Running Tests

```
pytest
```

## Code Formatting

- To format the code using Black:
  ```
  black .
  ```

- To sort imports using isort:
  ```
  isort .
  ```

- To check for code style issues using flake8:
  ```
  flake8 .
  ```

   ```
   docker-compose up --build
   ```
   ```
   docker-compose run web pytest
   ```