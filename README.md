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
 auditing and rollback support.
- **Leave Management:** Central workflow connecting employees, policies, and HR actions.
  
## Testing and Postman export
- Export Postman collection JSON and environment JSON and include them in the repo.
- Ensure example responses in the collection are accurate and do not contain sensitive data.

---
## System Architecture and Implementation Overview

The HRMS Leave Management System is designed as a **modular monolith**, organized into independent Django apps that represent distinct business domains.  
Each app is isolated in terms of functionality and database models, allowing for clean scalability and potential future migration to microservices.

### Core Modules

#### 1. Authentication (`auth_app`)
- Custom `User` model extending Django’s base with roles: `SUPERADMIN`, `HR`, and `EMPLOYEE`.
- Implements secure JWT-based login and token refresh system.
- Role-based permissions restrict actions at both view and object levels.
- In this demo setup, user registration is open for testing (`AllowAny`), but in production, only authenticated Super Admins or HRs would create users.

#### 2. Organization (`organization`)
- Defines tenant boundaries for HR and Employee data.
- Each user (HR/Employee) is linked to an organization.
- Super Admin manages organization creation and lifecycle.

#### 3. Employee Management (`employee`)
- Stores employee metadata such as department, designation, and joining details.
- Each employee is linked to both a `User` and an `Organization`.
- HR can manage employees only within their organization.

#### 4. Leave Policy (`policy`)
- Defines organization-specific rules: annual limits, carry-forward, encashment eligibility, notice periods, and required documentation.
- Policies are validated for duplicates and conflicting conditions.
- Every update to a policy automatically creates a version record in `LeavePolicyHistory` for full traceability and rollback support.

#### 5. Leave Management (`leave`)
- Core workflow that connects employees, policies, and HR actions.
- Handles leave application, validation, approval, rejection, and cancellation.
- Tracks leave balance and ensures compliance with policy constraints.

---

## Leave Workflow and Validation Logic

The leave management workflow enforces multi-level validation and rule enforcement:

1. **Eligibility Validation** – Employees can apply only for active leave types defined in their organization.  
2. **Policy Constraints** – System verifies:
   - Leave days do not exceed policy limits.
   - Notice period is met.
   - Supporting documents are uploaded if the leave duration exceeds allowed days without documentation.
3. **Role-Based Actions**
   - Employees can apply and view their own leaves.
   - HR users can review, approve, or reject leave requests for their organization.
   - Super Admin can audit or monitor leaves across organizations.
4. **Policy Versioning**
   - Every policy update triggers a new record in `LeavePolicyHistory`.
   - Each leave references the policy version active at the time of application.

---

## Security and Access Control

- Authentication handled through **JWT tokens** (`Authorization: Bearer <token>`).  
- Views and serializers include role-based permission checks:
  - Employees → self-only data access.
  - HR → organization-level access.
  - Super Admin → full system visibility.
- Strong referential integrity across User, Organization, and Employee models.
- Data isolation ensured by filtering queries within the user’s organization context.

---

## Data Integrity and Validation

- Serializer-level validation prevents inconsistent states and ensures compliance with policy definitions.
- Prevents duplicate policy names and overlapping configurations within the same organization.
- Ensures every leave entry maps to a valid employee and policy.
- Transactional updates maintain consistency across leave and policy records.

---

## Architecture Scalability

This system is designed as a **modular monolith**, but structured to evolve into a **microservices architecture** when required.  
Each app can independently scale or migrate into a service with minimal refactoring.

### Migration Path to Microservices
- Split existing apps into dedicated services (Auth, Employee, Policy, Leave).  
- Introduce a central API Gateway for routing and authentication.  
- Use a message broker (RabbitMQ/Kafka) for asynchronous communication and event-driven processes.  
- Add centralized logging and monitoring (e.g., ELK stack).

---

## Future Enhancements

- **Background Jobs:** Integrate Celery for scheduled carry-forward, leave reset, and notification jobs.  
- **Notifications:** Add email/SMS alerts for approvals and rejections.  
- **Analytics Dashboard:** HR metrics for leave trends, policy utilization, and compliance.  
- **Advanced Rule Engine:** Store JSON-based policy rules for flexible evaluation.  
- **Multi-Tenancy:** Support schema or database isolation per organization.  
- **Audit Trail:** Record every change across modules for compliance and auditing.  

---

## Summary

The HRMS Leave Management System provides a complete, policy-driven leave management workflow built on Django REST Framework.  
Its modular monolithic architecture ensures simplicity in development while maintaining scalability and separation of concerns.  
Each module represents a business boundary with defined responsibilities, ensuring clean transitions to microservices in future phases.  
The project demonstrates practical implementation of role-based security, version-controlled policies, and robust leave validation logic for real-world HR systems.
