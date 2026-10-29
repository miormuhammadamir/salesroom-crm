# Daily sales workflow

## 1. Capture a customer

Choose Customers → New customer. Record their name, company, contact information, source, potential value and notes. Managers can select an owner; salespeople are automatically assigned as owner. Contact email and phone are optional. Similar names and shared contact details are allowed; search existing records before adding a duplicate. There is no automated deduplication or merge.

## 2. Track the relationship

Update the profile stage through New lead → Contacted → Qualified → Proposal → Negotiation → Client, or Lost. Stages can be moved backwards when appropriate. Each actual stage change records its timestamp and actor. Add explanatory context to profile/follow-up notes. A confirmed order does not automatically make a customer a Client: set that stage deliberately when conversion is agreed.

The customer page brings together profile, stage history, orders and follow-up history. Reassigning a customer as a manager also reassigns every associated order and follow-up, preserving the same ownership boundary. Payments follow their order. Historical sales reporting therefore follows the current order owner after reassignment, not the original seller. An audit entry records the reassignment; if immutable original-seller attribution is needed, add that field before using this for commission calculations.

## 3. Record a sale / order

Choose Orders & sales → New order, or New order from a customer profile. Choose a product to copy its description and current price or enter a custom line. Add up to 100 lines. Each order saves its own price snapshot. Enter a discount in RM and tax as a percentage. The order total is `(sum(quantity × unit price) − discount) × (1 + tax / 100)`, rounded to two decimals on the full total, with Python Decimal's default half-even rounding.

Discounts cannot exceed subtotal; quantity must be at least one; prices cannot be negative; tax must be 0–100%; due date cannot precede order date. Statuses: Draft, Confirmed, Processing, Completed, Cancelled. Use Draft for a quotation. Confirm the order when it is booked. Printed sheets are sales orders, not jurisdiction-specific tax invoices. Use Print / Save PDF on the order page and choose your browser's Save as PDF destination.

## 4. Track payment

Choose Payments → New payment and select a Confirmed, Processing or Completed order. Enter positive amount, payment date, method and optional reference. Partial payments are supported; the order's balance and payment status update from recorded payments. A payment exceeding the remaining balance is rejected. An order with payments cannot be cancelled/reverted to Draft or reduced below the total already paid. There is no refund or credit-note ledger; correcting an erroneous payment is done via edit/delete and leaves an activity log entry. Do not delete genuine payments to represent refunds.

## 5. Follow up

Schedule a follow-up with channel, date/time, priority, subject and notes. All times are Malaysia time. A channel is a label only; the application does not send messages or place calls. Mark Done after recording the outcome in notes; completion time is saved. Reopening removes the completion timestamp. Open past-due tasks appear in overdue counts. There are no external reminder notifications.

## Reporting definitions

| Metric | Definition |
| --- | --- |
| Booked sales | Current total of Confirmed, Processing and Completed orders with order dates in the chosen range; includes tax, less discount; not statutory revenue recognition |
| Payments collected | Payments whose paid-on date falls within the chosen range, regardless of order date |
| Outstanding | Total minus recorded payments for all active booked orders, across all dates |
| Relationships / pipeline | Current customer counts by stage, across all dates; not historical stage conversion rates |
| Six-month graph | Six calendar months ending in the selected end date's month, full months, independent of the selected start date |
| Team sales / order count | Booked orders in the reporting range, assigned to the current owner |
| Monthly achievement | Full-calendar-month booked sales in the selected end date's month divided by that month's target; the progress bar caps at 100%, the displayed percentage can exceed it |
| Clients / overdue tasks | Current customer stages / currently overdue open tasks across all dates |

Order and payment dates may be entered in the future. A future-dated record appears when its date is in the selected range; the monthly graph uses the full month. Current totals/statuses are used, so edits affect historical reports. This is an operational sales tracker, not a period-locked accounting system.

## Filters and exports

Search lists by customer, contact, product, subject or payment reference, depending on module. Order search also accepts order number (for example SO-00001). Stage/status, owner and date filters appear where supported. Customer date filtering uses created date; order uses order date; follow-up uses due date; payment uses payment date; targets use target month. CSV and Excel export all filtered matching records, not just the displayed page. Text resembling a spreadsheet formula is prefixed with an apostrophe. CSV includes a UTF-8 BOM for Excel compatibility. Exported files contain personal/business information; handle them accordingly.

## Management

Operations shows all-team totals, overdue work and the latest 15 application audit entries. Sales targets are unique per user/month and require the first day of the month. Superusers can browse the full audit in Django admin. User management actions are recorded in Django's own admin history, separately from CRM activity. Deactivate departing users rather than deleting users who own records. Application business records are read-only in Django admin; use the main CRM for valid edits.

Deletion is confirmed on a dedicated page and requires POST. Customers with orders, orders with payments, and products referenced by order lines are protected from deletion. Unlinked customer deletion cascades to follow-ups and journey events. Deleted records are not recoverable through the app; restore from backup if needed. Prefer keeping real transaction history.
