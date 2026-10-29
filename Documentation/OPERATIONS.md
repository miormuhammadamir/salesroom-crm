# Operations and maintenance

## Backup

Back up before migrations and regularly after business use. Keep encrypted copies off the application disk with controlled access. The following uses SQLite's online backup API; run from Source Code with the Python environment active. It respects SQLITE_PATH through Django settings.

```bash
python manage.py shell -c "import sqlite3; from pathlib import Path; from datetime import datetime; from django.conf import settings; Path('backups').mkdir(exist_ok=True); source=sqlite3.connect(settings.DATABASES['default']['NAME']); destination=sqlite3.connect('backups/salesroom-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.sqlite3'); source.backup(destination); destination.close(); source.close()"
```

This creates a local backup only; copy it to your controlled backup destination. Test restore regularly. Include environment configuration/host settings in your recovery process without placing secrets in the source archive.

## Restore / rollback

1. Stop every application process and prevent writes.
2. Preserve a copy of the current database for investigation.
3. Replace the configured database file with the selected consistent backup; remove no journal/WAL files without understanding the current SQLite state.
4. Restore the application source/dependency version matching that database and restart.
5. Verify login, customer/order counts, totals, payments and latest activity before reopening access.

For updates: take a backup, test the update/migrations against a copy, then deploy in a maintenance window. For a failed initial install with no business data, create a fresh database at a new path and rerun migrate. Never casually delete or reset a business database. Data recovery from individual record deletion is not built into the application.

## User access

Use a superuser to create/deactivate users. Salespeople are ordinary users; Staff status grants manager access to all CRM information. Business-model permissions in Django admin are intentionally not used to grant CRM scope. Do not delegate user-administration permissions to untrusted staff. Audit entries are read-only through the app/admin, but are not cryptographically immutable against a database/host administrator. CRM audit contains action, entity ID and label, not full before/after row copies. It records application mutations/exports; login events, direct database changes and reads are not logged there. Django user admin changes use its own history.

## Production work still required

Provision a persistent Python host, HTTPS, static-file serving, unique secret, DEBUG=0, exact allowed hosts, external login throttling and monitoring. Built-in Django login has no rate limiter here; no MFA, password-reset email or SSO integration is included. Session/CSRF middleware, password validation, template escaping and ORM parameterization are used. No arbitrary uploads or raw SQL user queries are accepted.

SQLite is the requested first database and suits evaluation or limited write concurrency. Transactions provide all-or-nothing application writes, but SQLite's coarse locking can cause database-locked errors under concurrent load. Customer/order revision checks reject stale forms; other records follow last-save-wins behavior. Aggregate payment rules have not been stress-tested concurrently. PostgreSQL is the next step for sustained concurrent team use, with specific migration/load/concurrency testing.

Dashboard and exports calculate totals in Python and load matching orders; this is deliberately simple for the first SQLite version. Large datasets need database-side aggregates, batched/streamed exports and measured indexing/query improvements. There is no inventory, purchase/procurement workflow, refunds, commission calculation, statutory tax invoicing, multi-currency, period locking, attachment storage, bulk import, multi-tenant isolation or scheduled notifications. Follow-up channels are tracking labels only.

Use export for reporting, not database backup. Exports do not preserve every relationship/history field. Delete is a hard delete after confirmation and retention policies must be set by the business.

Official references:
- https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- https://docs.djangoproject.com/en/5.2/ref/databases/#sqlite-notes
- https://docs.djangoproject.com/en/5.2/topics/auth/default/
