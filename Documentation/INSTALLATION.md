# Installation

## Local setup

Follow the root README. `requirements.lock.txt` contains the exact dependency versions used for validation. `requirements.txt` expresses compatible ranges for later deliberate upgrades. Upgrade dependencies in a test environment and rerun the suite before release.

Windows users may use `py` in place of `python`. If PowerShell prevents activation, use Command Prompt activation or call `.venv\Scripts\python.exe` directly. No Node.js, frontend build, external CDN, or separate database server is required.

`python manage.py seed_demo` is optional and adds only fictional demonstration data. Run it only against an empty CRM; its transaction rolls back on conflicts. It creates three ordinary users (`demo_aina`, `demo_daniel`, `demo_sara`) with unusable passwords. Use your newly created superuser to inspect their records. Never enter real information into a demo copy.

## Configuration

Settings read process environment variables. `.env.example` is a reference, not a dotenv loader. Set variables in your shell or process manager.

| Variable | Default | Purpose |
| --- | --- | --- |
| DJANGO_DEBUG | 1 | Development mode; set to 0 for production |
| DJANGO_SECRET_KEY | Development-only fallback | Required unique secret when DEBUG=0; do not commit it |
| DJANGO_ALLOWED_HOSTS | localhost,127.0.0.1,[::1] | Comma-separated accepted hosts, no schemes or ports |
| SQLITE_PATH | Source Code/db.sqlite3 | Database file location; persistent writable disk and existing parent required |

Use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` inside the activated environment to generate your own secret locally. Store it in your hosting secret manager, not in source control.

## Deployment preparation

This package has not been publicly deployed. Use a Python WSGI host with persistent disk for SQLite; static-only hosting and Cloudflare Workers do not run this Django app. Start with one application worker and low write concurrency. For a growing sales team, move to PostgreSQL and retest concurrency before expanding workers.

Set DEBUG=0, the secret key, exact allowed domain and a persistent SQLITE_PATH. Use a production WSGI server serving `config.wsgi:application` behind HTTPS; do not use Django's development server publicly. Install your chosen server separately. Run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Serve `staticfiles/` as `/static/` through your host/reverse proxy. The production settings enable HTTPS redirects, secure cookies and HSTS. If TLS terminates at a proxy, configure HTTPS forwarding only for a trusted proxy that strips incoming spoofed headers; otherwise redirects may loop. Do not blindly trust forwarded headers. Add external login rate limiting, logging, monitoring and backups, then perform the manual tests in TESTING.md. Production host/proxy setup is environment-specific and has not been tested here.

Official deployment guidance: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
