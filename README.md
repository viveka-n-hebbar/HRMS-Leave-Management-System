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
- Postman Collection (export included in repository): `HRMS Leave Management API.postman_collection.json`
- Postman Environment (export included): `HRMS-Dev..postman_environment.json`
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

## Implementation Summary

### Core Architecture
This system follows a **modular monolithic architecture** simulating a microservices structure, where each domain (Authentication, Organization, Employee, Leave Policy, and Leave Management) is isolated into its own Django app.  
Each module is independently scalable and communicates through defined data models (via ForeignKey relationships).  
This design allows easy transition to a true microservice architecture in the future using message brokers such as RabbitMQ or Kafka.

### Key Modules and Relationships
- **Organization:** Central tenant entity to which all HRs and Employees belong. Super Admin manages organization lifecycle.
- **Auth (User Management):** Custom User model supporting roles — `SUPERADMIN`, `HR`, and `EMPLOYEE` — with JWT authentication for secure access control.
- **Employee:** Each Employee is linked to both a `User` and an `Organization`.  
  HRs can view or manage only their organization’s employees.
- **Leave Policy:** Defines organization-specific leave rules (Annual, Sick, Casual, Unpaid).  
  Includes parameters like maximum annual days, carry-forward limit, document requirement, and encashment eligibility.
- **Leave Policy History:** Tracks every update to a leave policy as a new version snapshot for auditing and rollback support.
- **Leave Management:** Central workflow connecting employees, policies, and HR actions.  
  Handles leave application, validation, approval, rejection, and cancellation.

### Leave Workflow and Validation Logic
The **Leave Management process** enforces strong business logic at both the model and serializer levels:
- **Eligibility Validation:** Employee can apply for leave only under active policy types defined by their organization.
- **Policy Constraints:**  
  - Validates remaining leave balance and `max_days_per_year` constraint.  
  - Enforces `notice_period_days` before the start date.  
  - Requires document upload if leave exceeds `max_days_without_doc`.  
- **Role-Based Actions:**  
  - Employees can apply and track their own leaves (`/leaves/me/`).  
  - HR users can view, approve, reject, or cancel requests within their organization.  
  - Super Admin has read-only oversight of all organizations.
- **Automated History Tracking:** Each policy update generates a new record in `LeavePolicyHistory`, maintaining a versioned audit trail.

### Security and Access Control
- Implemented using **JWT Authentication** with access and refresh tokens.
- Each endpoint secured by `IsAuthenticated` and custom role-based permission classes.
- Object-level permissions ensure HR and Employees cannot access data from other organizations.

### Validation and Data Integrity
- Serializer-level validation ensures that:
  - Leave requests comply with organization policy constraints.
  - Duplicate policies (same name and type) within the same organization are disallowed.
  - Foreign key consistency is enforced across all modules.
- Strict referential integrity between `User`, `Organization`, and `Employee`.

### Testing and Documentation
- Full API tested using **Postman** with organized collections per module.
- Example responses and environment variables configured for reproducibility.
- Published API documentation for external reference:  
  **[View API Documentation](https://documenter.getpostman.com/view/49544672/2sB3Wjzj65)**

### Future Enhancements
- Integrate background tasks using **Celery** for periodic leave resets, carry-forward automation, and scheduled notifications.
- Add email/SMS notifications for approval or rejection events.
- Implement analytics dashboard for HR metrics (leave utilization, policy compliance).
- Extend system into true microservices using RESTful inter-service communication and message queuing.
- Enhance multi-tenancy with database-level isolation per organization for enterprise scalability.

## Testing and Postman export
- Export Postman collection JSON and environment JSON and include them in the repo.
- Ensure example responses in the collection are accurate and do not contain sensitive data.
