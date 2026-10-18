# Healthcare Backend

A Django REST Framework API for email-based JWT authentication, private patient records, shared doctor directory records with creator-only edits, and patient-doctor assignments. PostgreSQL is the configured database.

## Requirements and setup

Requires Python 3.10+ and PostgreSQL 14+ reachable by the application. Create database/user with privileges, then:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with a strong DJANGO_SECRET_KEY and PostgreSQL credentials
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Linux/macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Example PostgreSQL SQL (run as an administrator):

```sql
CREATE USER healthcare_user WITH PASSWORD 'replace-this-password';
CREATE DATABASE healthcare_db OWNER healthcare_user;
```

Use a random secret key in production. `DJANGO_DEBUG=False` requires a secret and allowed hosts. Configure HTTPS and set `DJANGO_ALLOWED_HOSTS` to the deployment hostnames. `.env` is ignored by Git.

## API

All protected routes require `Authorization: Bearer <access>`. Register and login are public. JSON validation follows DRF's standard error response format.

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create user (`name`, `email`, `password`) |
| POST | `/api/auth/login/` | Obtain `access` and `refresh` tokens |
| POST | `/api/auth/token/refresh/` | Rotate refresh token and obtain access token |
| GET/POST | `/api/patients/` | List owned patients / create patient |
| GET/PUT/DELETE | `/api/patients/{id}/` | Retrieve, replace, or delete owned patient |
| GET/POST | `/api/doctors/` | List doctors / create doctor |
| GET/PUT/DELETE | `/api/doctors/{id}/` | Retrieve doctor / creator-only update or delete |
| GET/POST | `/api/mappings/` | List mappings for owned patients / create assignment |
| GET | `/api/mappings/{patient_id}/` | List doctors assigned to owned patient |
| DELETE | `/api/mappings/{mapping_id}/` | Delete a mapping attached to owned patient |

Patient JSON requires `name`, `date_of_birth` (ISO date), and `gender` (`female`, `male`, `other`, `prefer_not_to_say`); optional fields are `email`, `phone`, `address`. Doctor requires `name`, `specialization`, `email`, and `phone`; `address` is optional. Mapping accepts integer `patient` and `doctor` IDs. Server-managed IDs, timestamps, and ownership fields are read-only.

Patient records are visible only to their owner. Doctors are visible to authenticated users, while only their creator may modify them. A user can assign a doctor only to their own patient. Duplicate assignments are blocked both by validation and a database unique constraint. Lists are paginated (20 per page).

## Postman

Import `postman_collection.json`. Set `base_url` (default `http://127.0.0.1:8000`) and run Register/Login. Login's test script saves the access token into `access_token`; the collection uses it as a Bearer token. Collection variables include sample IDs to update for detail and delete requests. Requests document expected status codes in their descriptions.

## Tests

Run using a separate Django test database:

```powershell
py manage.py test
```

```sh
python manage.py test
```

Django creates and destroys a dedicated test database; it does not use the configured database's existing data. A reachable PostgreSQL service is needed for test execution because PostgreSQL is the configured backend.

## Troubleshooting

- `connection refused`: start PostgreSQL and check `DB_HOST`/`DB_PORT`.
- `password authentication failed`: check `.env` credentials and database grants.
- Missing configuration in production: set `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and all `DB_*` values.
- PowerShell blocks activation: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` if permitted, or invoke `.venv\Scripts\python.exe` directly.
- `No module named ...`: activate the virtual environment and run `pip install -r requirements.txt`.
