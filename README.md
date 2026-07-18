# Recipe API App

A RESTful API for managing recipes, built with **Django** and the **Django REST
Framework**. Authenticated users can create and manage their own recipes,
including the tags and ingredients that describe them, and upload an image for
each recipe.

The project runs entirely in Docker, uses **PostgreSQL** for persistence, ships
with a full **unit-test suite**, and enforces style with **flake8**.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [Running the Tests](#running-the-tests)
- [Linting](#linting)
- [Data Model](#data-model)
- [License](#license)

---

## Features

- **Custom user model** that authenticates by email instead of username.
- **Token authentication** for all protected endpoints.
- **Recipes** — full CRUD, scoped to the authenticated user.
- **Tags & Ingredients** — create and list user-owned recipe attributes.
- **Filtering** — filter recipes by tags/ingredients, and filter tags/
  ingredients to only those assigned to a recipe.
- **Image upload** — attach an image to a recipe via a dedicated endpoint.
- **Django admin** customised for the email-based user model.
- **`wait_for_db`** management command so the app starts cleanly once
  PostgreSQL is ready.
- **Comprehensive test suite** covering models, admin, management commands,
  and every API endpoint.

---

## Tech Stack

| Layer            | Technology                          |
| ---------------- | ----------------------------------- |
| Language         | Python 3.11                         |
| Web framework    | Django 4.2 (LTS)                    |
| API framework    | Django REST Framework 3.15          |
| Database         | PostgreSQL 15                       |
| DB driver        | psycopg2 2.9                        |
| Image handling   | Pillow 10                           |
| Containerisation | Docker & Docker Compose             |
| Linting          | flake8 7                            |
| CI               | Travis CI (`.travis.yml`)           |

> **Note on dependencies:** the original project targeted Django 2.1 / Python
> 3.6–3.7, all of which are end-of-life. The stack has been upgraded to the
> current Django LTS line and supported runtimes. See
> [requirements.txt](requirements.txt).

---

## Project Structure

```
recipe-api-app/
├── app/
│   ├── app/                  # Django project (settings, root URLs, WSGI)
│   ├── core/                 # Shared models, admin, migrations, mgmt commands
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── wait_for_db.py
│   │   ├── models.py         # User, Tag, Ingredient, Recipe
│   │   └── tests/
│   ├── user/                 # User registration, token auth, profile
│   ├── recipe/               # Recipe, Tag & Ingredient API
│   └── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .travis.yml
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### 1. Clone the repository

```bash
git clone <repository-url>
cd recipe-api-app
```

### 2. Build the image

```bash
docker-compose build
```

### 3. Run the database migrations

```bash
docker-compose run --rm app sh -c "python manage.py migrate"
```

### 4. Start the app

```bash
docker-compose up
```

The API is now available at **http://127.0.0.1:8000/**.

The `app` service command automatically waits for the database, applies
migrations, and starts the development server:

```
python manage.py wait_for_db && python manage.py migrate && python manage.py runserver 0.0.0.0:8000
```

### 5. (Optional) Create an admin user

```bash
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

Then visit the Django admin at **http://127.0.0.1:8000/admin/**.

---

## Configuration

The database connection is configured through environment variables (set in
[docker-compose.yml](docker-compose.yml)):

| Variable   | Description                | Default (compose)      |
| ---------- | -------------------------- | ---------------------- |
| `DB_HOST`  | PostgreSQL host            | `db`                   |
| `DB_NAME`  | Database name              | `app`                  |
| `DB_USER`  | Database user              | `postgres`             |
| `DB_PASS`  | Database password          | `supersecretpassword`  |

> **Security:** the `SECRET_KEY` and `DEBUG=True` settings in
> [app/app/settings.py](app/app/settings.py) are development defaults. Override
> them (and set `DEBUG=False` with a proper `ALLOWED_HOSTS`) before deploying to
> production.

---

## API Reference

All endpoints are namespaced under `/api/`.

### User

| Method        | Endpoint            | Auth | Description                          |
| ------------- | ------------------- | ---- | ------------------------------------ |
| `POST`        | `/api/user/create/` | No   | Register a new user.                 |
| `POST`        | `/api/user/token/`  | No   | Obtain an auth token.                |
| `GET`         | `/api/user/me/`     | Yes  | Retrieve the authenticated profile.  |
| `PUT`/`PATCH` | `/api/user/me/`     | Yes  | Update name and/or password.         |

### Recipes

| Method        | Endpoint                                 | Description                    |
| ------------- | ---------------------------------------- | ------------------------------ |
| `GET`         | `/api/recipe/recipes/`                   | List the user's recipes.       |
| `POST`        | `/api/recipe/recipes/`                   | Create a recipe.               |
| `GET`         | `/api/recipe/recipes/{id}/`              | Retrieve a recipe (detailed).  |
| `PUT`/`PATCH` | `/api/recipe/recipes/{id}/`              | Update a recipe.               |
| `DELETE`      | `/api/recipe/recipes/{id}/`              | Delete a recipe.               |
| `POST`        | `/api/recipe/recipes/{id}/upload-image/` | Upload a recipe image.         |

**Filtering:** `GET /api/recipe/recipes/?tags=1,2&ingredients=3,4`

### Tags

| Method | Endpoint                  | Description             |
| ------ | ------------------------- | ----------------------- |
| `GET`  | `/api/recipe/tags/`       | List the user's tags.   |
| `POST` | `/api/recipe/tags/`       | Create a tag.           |

**Filtering:** `GET /api/recipe/tags/?assigned_only=1` — only tags assigned to a
recipe.

### Ingredients

| Method | Endpoint                        | Description                 |
| ------ | ------------------------------- | --------------------------- |
| `GET`  | `/api/recipe/ingredients/`      | List the user's ingredients.|
| `POST` | `/api/recipe/ingredients/`      | Create an ingredient.       |

**Filtering:** `GET /api/recipe/ingredients/?assigned_only=1` — only ingredients
assigned to a recipe.

---

## Authentication

Protected endpoints use **Token authentication**.

1. Register a user:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/user/create/ \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "testpass123", "name": "Jane"}'
   ```

2. Obtain a token:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/user/token/ \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "testpass123"}'
   # => {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
   ```

3. Use the token on protected requests:

   ```bash
   curl http://127.0.0.1:8000/api/recipe/recipes/ \
     -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
   ```

---

## Running the Tests

Tests run inside the container against the configured database:

```bash
docker-compose run --rm app sh -c "python manage.py test"
```

Run tests and linting together (the same command Travis CI uses):

```bash
docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py test && flake8"
```

The suite covers:

- **Models** — user creation/normalisation, superusers, string representations,
  and the recipe image file-path helper.
- **Admin** — user list, change, and add pages.
- **Management commands** — `wait_for_db` (ready and retry paths).
- **User API** — registration, token issuance, validation, and profile
  management.
- **Recipe / Tag / Ingredient API** — listing, creation, filtering, per-user
  scoping, updates, deletion, and image upload.

---

## Linting

```bash
docker-compose run --rm app sh -c "flake8"
```

Configuration lives in [app/.flake8](app/.flake8) (migrations, `manage.py`, and
`settings.py` are excluded).

---

## Data Model

- **User** — email (unique, login field), name, `is_active`, `is_staff`.
- **Tag** — name, owning user.
- **Ingredient** — name, owning user.
- **Recipe** — title, time (minutes), price, optional link, image, and
  many-to-many relations to tags and ingredients; owned by a user.

All tags, ingredients, and recipes are always scoped to the authenticated user
who created them.

---

## License

This project is distributed for educational purposes. Add a license file to
define usage terms for your own fork.
