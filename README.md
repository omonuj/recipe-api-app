# Recipe API App

[![CI/CD](https://github.com/omonuj/recipe-api-app/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/omonuj/recipe-api-app/actions/workflows/ci-cd.yml)

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
- [Interactive API Docs (Swagger)](#interactive-api-docs-swagger)
- [Authentication](#authentication)
- [Running the Tests](#running-the-tests)
- [Linting](#linting)
- [Continuous Integration & Deployment](#continuous-integration--deployment)
- [Deployment (Vercel)](#deployment-vercel)
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
- **Interactive OpenAPI 3 docs** — Swagger UI and ReDoc via `drf-spectacular`.
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
| API docs         | drf-spectacular (OpenAPI 3 / Swagger) |
| Deployment       | Vercel (serverless) + WhiteNoise    |
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

## Interactive API Docs (Swagger)

The API ships with auto-generated **OpenAPI 3.0** documentation powered by
[`drf-spectacular`](https://drf-spectacular.readthedocs.io/). Once the app is
running:

| Tool           | URL                                      |
| -------------- | ---------------------------------------- |
| Swagger UI     | http://127.0.0.1:8000/api/docs/          |
| ReDoc          | http://127.0.0.1:8000/api/redoc/         |
| Raw schema     | http://127.0.0.1:8000/api/schema/        |

Swagger UI is interactive — click **Authorize**, paste `Token <your-token>`,
and you can exercise every endpoint from the browser.

Generate the schema file from the command line:

```bash
docker-compose run --rm app sh -c "python manage.py spectacular --file schema.yml"
```

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

## Continuous Integration & Deployment

CI/CD runs on **GitHub Actions**
([.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml)):

- **`test` job** — on every push and pull request to `master`, spins up the
  Docker stack and runs `wait_for_db`, the full test suite, and `flake8`. This
  is the exact command used locally, so CI mirrors development.
- **`deploy` job** — on pushes to `master` (after tests pass), deploys to
  Vercel using the Vercel CLI. It **skips gracefully** if the Vercel secrets
  aren't configured, so the pipeline stays green until you opt in.

### Enabling automatic deploys

You have two options:

**Option A — Vercel's native Git integration (simplest).** Connect the repo in
the Vercel dashboard; Vercel builds a preview for every PR and deploys `master`
to production automatically. No secrets needed — the `deploy` job stays skipped.

**Option B — Deploy from GitHub Actions.** Add three
[repository secrets](https://github.com/omonuj/recipe-api-app/settings/secrets/actions)
(Settings → Secrets and variables → Actions):

| Secret              | Where to find it                                       |
| ------------------- | ------------------------------------------------------ |
| `VERCEL_TOKEN`      | Vercel → Account Settings → Tokens                     |
| `VERCEL_ORG_ID`     | `.vercel/project.json` after running `vercel link`     |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` after running `vercel link`     |

Once set, every push to `master` runs the tests and then deploys to production.

---

## Deployment (Vercel)

The project is configured to deploy to **Vercel** as a Python serverless
function. The relevant files are [vercel.json](vercel.json),
[api/index.py](api/index.py) (the WSGI entrypoint), and
[build_files.sh](build_files.sh) (collects static assets at build time).

### Serverless caveats (read first)

Vercel has **no persistent filesystem** and no long-running process, so:

- **You must use an external managed PostgreSQL** database — e.g.
  [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres),
  [Neon](https://neon.tech), or [Supabase](https://supabase.com) (all free
  tiers). SQLite / local Postgres will not work.
- **Uploaded recipe images do not persist** between requests. The API works
  fully; only image files are ephemeral. To keep them, wire up cloud storage
  (e.g. S3 or Cloudinary via `django-storages`) as a follow-up.

### 1. Provision a database

Create a Postgres instance with any provider above and copy its connection
string (a `postgres://...` URL).

### 2. Configure environment variables (Vercel dashboard → Settings → Environment Variables)

See [.env.example](.env.example) for the full list:

| Variable               | Example                                  |
| ---------------------- | ---------------------------------------- |
| `SECRET_KEY`           | a long random string                     |
| `DEBUG`                | `0`                                      |
| `ALLOWED_HOSTS`        | `.vercel.app`                            |
| `CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app`        |
| `DATABASE_URL`         | `postgres://user:pass@host:5432/dbname`  |

### 3. Run migrations against the remote database

Serverless functions shouldn't run migrations on cold start, so apply them once
from your machine (or any shell) pointed at the same `DATABASE_URL`:

```bash
DATABASE_URL="postgres://user:pass@host:5432/dbname" \
  python app/manage.py migrate
```

Create an admin user the same way if you want the Django admin:

```bash
DATABASE_URL="postgres://..." python app/manage.py createsuperuser
```

### 4. Deploy

```bash
npm i -g vercel        # first time only
vercel                 # preview deploy
vercel --prod          # production deploy
```

Or connect the GitHub repo in the Vercel dashboard for automatic deploys on
push.

After deploying, your docs will be live at
`https://your-project.vercel.app/api/docs/`.

> **Settings are backward-compatible:** when `DATABASE_URL` and the other
> production variables are absent, the app falls back to the local Docker
> configuration, so `docker-compose up` keeps working unchanged.

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
