# Salesroom — Django sales tracker


A runnable sales CRM using Python, Django 5.2, and SQLite, with server-rendered pages and dependency-free SVG dashboard charts. Default currency: MYR (RM). Timezone: Asia/Kuala_Lumpur.

## Start here

Requires Python 3.10+ (tested with Python 3.12). In a terminal, open the extracted `sales_tracker` folder, then:

```bash
cd "Source Code"
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
# Windows Command Prompt
.venv\Scripts\activate.bat
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install and launch:

```bash
python -m pip install -r requirements.lock.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open **http://127.0.0.1:8000/** and sign in with the account you just created. No default admin password is shipped. SQLite is created automatically by `migrate`.

Optional: before entering business records, run `python manage.py seed_demo` to populate fictional customers, sales, payments, follow-ups and targets. It refuses a populated CRM. Demo users cannot log in until you deliberately set a password using `python manage.py changepassword demo_aina` (or the other demo username). Your superuser can see all demo records.

## Included

- Sales overview: booked sales, collections, outstanding balances, six-month revenue graph, customer-stage chart, team results, targets, overdue follow-ups and recent orders.
- Customer CRUD, contact profiles, lead sources, assigned owners, potential values, notes, stage changes and timestamped journey history.
- Sales key-in through orders: multiple product/custom lines, quantities, saved prices, discounts, tax, due dates, status and printable order sheets / browser Save as PDF.
- Payment CRUD, partial/full balance tracking, method and reference. Overpayments, cancellation of paid orders and reductions below paid amounts are rejected.
- Follow-up CRUD: calls, WhatsApp, emails, meetings and tasks; owner, due time, priority, notes, status and completion timestamps. Overdue filtering.
- Product catalogue CRUD for managers; all sales staff can view the catalogue.
- Search, date/status/owner filters where applicable, pagination, and filtered CSV/Excel exports for every module.
- Operations dashboard, team performance, monthly sales targets, activity audit, and built-in Django user administration.
- Session authentication, CSRF protection, password validation/change, ORM queries, scoped records and relationship validation.

## Roles

| Role | Access |
| --- | --- |
| Sales staff (`is_staff=False`) | Own assigned customers, orders, payments and follow-ups; view/export catalogue; own dashboard and target progress |
| Manager (`is_staff=True`) | All CRM records, reassignment, products, targets, operations and team reporting |
| Superuser | Manager features plus `/admin/` for users and audit inspection |

Create users at `/admin/auth/user/` using your superuser. Leave **Staff status** off for salespeople; enable it only for managers. Managers do not need Django model permissions for the CRM application. Business records in Django admin are read-only so edits must use the application's validated workflows.

## Documentation

- `Documentation/INSTALLATION.md` — setup, environment and deployment preparation
- `Documentation/USER_GUIDE.md` — daily operations and accounting definitions
- `Documentation/SCHEMA.md` — relationships, constraints and ERD
- `Documentation/schema.sql` — generated SQLite SQL for CRM migration 0001
- `Documentation/ROUTES.md` — browser route/reference guide (no separate JSON API)
- `Documentation/TESTING.md` — automated results and manual acceptance checks
- `Documentation/OPERATIONS.md` — backup, restore, security and limitations
- `CHANGELOG.md`, `LICENSE`

## Verification and status

36 automated Django tests passed; system and migration consistency checks passed. Fictional demo seeding was executed successfully. Browser visual/JavaScript QA was blocked because the remote browser could not reach the local Django server. This is a functional MVP for local evaluation and small-team adaptation, not an already deployed production service. Production hosting, backups, login throttling and monitoring must be configured before public use. No email/WhatsApp sending, inventory, refunds, subscriptions, attachments or external integrations are implemented.
