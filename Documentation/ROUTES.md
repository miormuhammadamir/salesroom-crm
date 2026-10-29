# Browser route reference

This is a server-rendered Django application. There is no JSON/REST API or API-token authentication. Routes use session cookies, standard HTML forms and CSRF tokens. GET renders pages/downloads; business mutations require POST.

| Route | Method | Purpose |
| --- | --- | --- |
| / | GET | Scoped sales overview; optional start/end ISO dates |
| /operations/ | GET | Manager-only operations and team reporting |
| /accounts/login/ | GET, POST | Session login, validated safe next URL |
| /accounts/logout/ | POST | End session |
| /accounts/password/ | GET, POST | Authenticated password change |
| /admin/ | GET, POST | Django administration; superuser manages users; business data read-only |
| /{kind}/ | GET | Paginated list; q, status, owner, start, end, page, overdue filters as supported |
| /{kind}/new/ | GET, POST | Create record |
| /{kind}/{id}/edit/ | GET, POST | Update record within role/ownership scope |
| /{kind}/{id}/delete/ | GET, POST | Confirmation / delete; linked records protected |
| /customers/{id}/ | GET | Profile, journey, orders and follow-ups |
| /orders/{id}/ | GET | Order, lines, totals, printable view and payments |
| /{kind}/export/csv/ | GET | Filtered CSV export, with audit entry |
| /{kind}/export/xlsx/ | GET | Filtered XLSX export, with audit entry |

`kind`: customers, orders, followups, payments, products, targets. Targets are manager-only. Product writes are manager-only. Unknown kinds/record IDs return 404. Cross-owner records return 404 rather than disclosing existence. Explicit management permission failures return 403. Invalid date filters return 400. Validation errors re-render the form with status 200; successful mutations redirect (302) to avoid duplicate posts on refresh. Authentication failures redirect to login.

Order item forms use Django inline formset management fields with the `items` prefix; revision is required when editing existing customers/orders. Integrations should be implemented as a separately validated API rather than scripting undocumented HTML fields.
