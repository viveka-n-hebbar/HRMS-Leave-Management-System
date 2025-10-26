# HRMS Leave Management System

A Django REST Framework based HRMS Leave Management System.  
Modular monolithic design that simulates microservices by separating domains into apps: `auth_app`, `organization`, `employee`, `policy`, and `leave`. Multi-tenancy is implemented via foreign-key relationships to the `Organization` model.

## Features (brief)
- Super Admin, HR, Employee roles (role-based access)
- Organization onboarding (Super Admin)
- User registration and JWT authentication
- Employee records linked to users and organizations
- Leave policy creation (Annual, Sick, Casual, Unpaid) with validations
- Leave apply/approve/reject/cancel workflow
- Policy version history
- Postman collection + API documentation provided

## Prerequisites (Windows)
- Python 3.10+ or 3.11+ (3.12 worked for you previously)
- Git
- PostgreSQL (optional; sqlite3 works for local testing)
- Virtual environment

## Quick setup (Windows)

1. Clone the repository
```bash
git clone <your_github_repo_url>
cd <project_folder>
```

2. Create & activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` (or set environment variables) — minimal:
```
DJANGO_SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:pass@localhost:5432/dbname   # optional for Postgres
DEBUG=True
```

## Database migrations (recommended order)
Run migrations in this order to avoid FK/migration dependency issues:

```bash
python manage.py makemigrations organization
python manage.py makemigrations auth_app
python manage.py makemigrations employee
python manage.py makemigrations policy
python manage.py makemigrations leave
python manage.py migrate
```

Notes:
- If you use `sqlite3` you can run `python manage.py migrate` after making migrations; ordering still helps avoid inconsistent history.
- If you ever change or delete migrations, remove `db.sqlite3` only when safe (dev only).

## Create initial data (examples)
Open Django shell or create fixtures. Example using shell:
```bash
python manage.py shell
```
```python
from organization.models import Organization
from auth_app.models import User

org = Organization.objects.create(name="Acme Pvt Ltd", code="ACME", timezone="Asia/Kolkata")
# Create superadmin via createsuperuser or:
User.objects.create_superuser(email="admin@example.com", username="admin", password="password")
# Create HR using superadmin token or via admin UI
```

## Run server
```bash
python manage.py runserver
```
Application runs at `http://127.0.0.1:8000/` by default.

## API endpoints (high level)
- Auth: register, login (JWT)
- Organization: list/create/detail/update/delete
- Employee: list/create/detail/update/delete, `/employees/me/`
- Policy: list/create/detail/update/delete, `/policies/myorg/`, `/policies/{id}/history/`
- Leave: apply (POST `/leaves/`), employee history (`/leaves/me/`), HR approve/reject (`PUT /leaves/{id}/action/`)

## Postman collection & API documentation
- Postman Collection (export included in repository): `HRMS_API_Collection.json`
- Postman Environment (export included): `HRMS_ENV.json`
- Public API documentation (published): https://documenter.getpostman.com/view/49544672/2sB3Wjzj65

## Recommended Postman flow (short)
1. Import collection and environment JSON.
2. Set `{{base_url}}` and tokens in environment.
3. Use Super Admin login to get access token, then create organization and HR.
4. Use HR account to create employees and policies.
5. Use employee account to apply for leaves, and HR to approve/reject.

## Notes about authentication and roles
- JWT tokens are issued on login. Use the access token in `Authorization: Bearer <token>` header.
- Super Admin typically has no `organization` set. HR and Employee must be associated with an `Organization`.
- Registration endpoints are protected: Super Admin or HR create HR/Employee accounts (project simulates this by checking `request.user.role`).

## What was implemented (what you have)
- Models: Organization, User (custom), Employee, LeavePolicy, Leave, LeavePolicyHistory
- Role-based permissions at view level
- Policy validations (policy serializer checks)
- Leave validation examples (notice period, document requirement, yearly caps)
- Policy version/history (snapshot stored on update)
- Postman collection + published documentation link

## What can be added easily (future improvements)
- Background job worker (Celery) for escalations, scheduled carry-forward, encashment processing
- Notification/email integration (SMTP or external service)
- More advanced rule engine for policy conditions (store JSON rules and a lightweight evaluator)
- Move each app into separate microservice with API gateway and message broker for true microservices

## Future scope (short)
This project is a modular monolith designed to be split later into independent microservices. To scale:
- Convert apps to services (Auth, Employee, Policy, Leave) with separate deployments
- Use message broker (RabbitMQ/Kafka) for async events (approvals, escalations)
- Add centralized logging, monitoring, and multi-tenant isolation layers (schema-per-tenant or DB-per-tenant if required)

## How to produce `requirements.txt`
From your virtual environment:
```bash
pip freeze > requirements.txt
```

## Testing and Postman export
- Export Postman collection JSON and environment JSON and include them in the repo.
- Ensure example responses in the collection are accurate and do not contain sensitive data.

## Contact / Submission
- Include this repository zip, GitHub repo URL, exported Postman collection JSON, exported Postman environment JSON, and the public Postman documentation link when submitting.

Postman documentation link:
https://documenter.getpostman.com/view/49544672/2sB3Wjzj65
