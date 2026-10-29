# Testing

## Automated

From `Source Code` with the environment active:

```bash
python manage.py test crm --verbosity 1
python manage.py check
python manage.py makemigrations --check --dry-run
```

Actual validation: Python 3.12, Django 5.2.18, openpyxl 3.1.5. **36 tests passed**, Django system check reported no issues, and migration check reported no changes. Demo seeding also ran successfully in a fresh local CRM. Initial testing found a Decimal/float error for freshly created in-memory orders; the order calculation was corrected and the full suite rerun successfully.

Coverage includes authentication, list scoping, cross-owner access, manager permissions, staff page/form rendering, customer ownership and journey history, stale customer edits, reassignment, order arithmetic, invalid line/date/discount input, price snapshots, payment/partial balance validation, overpayment rejection, paid-order cancellation protection, follow-up completion/reopening, protected deletion, audit deletion entries, CSV formula escaping, XLSX readability, export scoping/filtering, target export, dashboard excluded statuses, invalid dates, CSRF, target uniqueness/month validation, unknown routes and populated-demo refusal.

Test databases are temporary and isolated from your workspace's db.sqlite3. Test accounts are created only in those temporary databases. Requirements lock file reproduces the validated packages.

Production-settings check was also run with DEBUG=0 and a generated temporary secret: it reported only security.W021 because HSTS preload is intentionally not opted into. Domain preload enrollment requires a deliberate hosting decision; this setting is not silently enabled.

Final package validation: JavaScript syntax check passed with `node --check`; the staff page-rendering test was rerun after the final template markup correction. The ZIP was extracted into a temporary clean directory, then migrations, demo seed, system check, a seeded dashboard request and an Excel export all passed with a new SQLite database. The archive contains no runtime database, virtual environment or login credentials.

## Manual acceptance before real use

1. Create a superuser, manager and two sales users. Confirm each role's navigation and records.
2. Add a customer, advance stages and inspect journey history. Reassign as manager and confirm related order/task visibility changes.
3. Create an order with multiple lines, custom items, discount and tax. Use Add item, remove a line, test validation errors and save.
4. Confirm the order; record partial then final payment. Attempt an overpayment and a paid-order cancellation.
5. Schedule a follow-up, mark it Done and reopen it. Check Malaysia-time display and overdue filtering.
6. Set monthly targets and reconcile dashboard sales, collections, outstanding and monthly progress with sample records.
7. Exercise search, status/owner/date filters, multiple pages and exports. Open CSV/XLSX in the intended spreadsheet application.
8. Print an order / Save as PDF; check page layout. Test phone, tablet, desktop, keyboard navigation, form labels, focus, contrast and screen reader output.
9. Run production `check --deploy`, verify HTTPS/static assets, login throttling, error logging and backup/restore on the actual host.

## Limits of verification

No real browser visual/JavaScript acceptance test was completed: the cloud browser's localhost endpoint did not reach the execution container's Django server. Server-side templates were exercised by the Django test client, but responsive appearance, Add item/product autofill, SVG drawing, printing and browser compatibility need manual confirmation. No load, multi-worker concurrency, public-host deployment, email delivery, external integration or penetration test was performed. No claims of production certification are made.
