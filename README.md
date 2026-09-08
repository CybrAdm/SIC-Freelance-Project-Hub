# SIC Freelance Project Hub

A command-line freelance marketplace application built for the **Samsung Innovation Campus (SIC)**
Chapter 3 capstone project — *Effective Python Programming: Functions, Closures, and Classes*.

The system manages clients, freelancers, projects, milestones, invoices, and payments, built
entirely around **Chapter 3 concepts**: object-oriented design with inheritance and
polymorphism, closures, regular expressions, custom exceptions, an iterator, and functional
tools (`map`, `filter`, `reduce`, `lambda`).

## Features

-  **Registration & Login** — role-specific ID formats (`C`/`F`/`A` + digits), 3-attempt login limit, duplicate email/phone prevention, password strength rules
-  **Project Lifecycle** — clients create, update, and delete projects; freelancers browse and choose matching work by skill; automatic health tracking (On Track / At Risk / Late / Completed)
-  **Milestone Workflow** — freelancers submit milestones for review, clients approve or reject, full status-change history is kept per milestone
-  **Invoicing & Payments** — invoices are auto-generated from a project's budget with a configurable commission cut; payments are recorded against an invoice's remaining balance with automatic status tracking (Unpaid / Partially Paid / Paid)
-  **Role-Based Access Control** — every project, milestone, invoice, and payment lookup is checked against the requesting user's ownership, with Admins bypassing the restriction
-  **Reports & Dashboard** — payment totals, freelancer earnings, project health, and a combined dashboard, all Admin-only and exportable to a text file per role
-  **Audit Log** — every meaningful action (login, project created, payment recorded, milestone approved, etc.) is timestamped and recorded
-  **JSON Persistence** — all data is saved to and loaded from the `data/` folder automatically on every change

## Getting Started

### Prerequisites
- Python 3.8+

### Setup

```bash
git clone https://github.com/<your-username>/sic-freelance-project-hub.git
cd sic-freelance-project-hub
```

No manual setup is required — on first run, the program creates a `data/` folder with empty
JSON collections and a default 10% commission rate. If you'd rather start with a ready test
environment, drop the provided dummy `data/*.json` files into that folder instead: they include
a seeded Admin account, two Clients, two Freelancers, and a set of projects, milestones,
invoices, and payments covering every status the system supports.

### Run

```bash
python main.py
```

## Concepts & Design Used

### 1. Inheritance & Polymorphism — `User`, `Client`, `Freelancer`
`User` is the base class holding the fields every account needs (name, email, phone, password,
role, active flag). `Client` and `Freelancer` inherit from it and add their own role-specific
fields — a company name for clients, or skills, an hourly rate, and earnings for freelancers.
Both subclasses override the base class's `profile_summary()` and `to_dict()` methods with
their own formatting, so the same call on a `User` object produces different output depending
on whether it is actually a `Client` or a `Freelancer`, without the caller ever checking the
type directly.

### 2. Closures — the commission engine
A factory function builds and returns an inner "calculator" function that keeps a private
commission rate alive across calls, entirely outside of any class. A second inner function,
using the `nonlocal` keyword, is attached to the calculator so the platform's commission rate
can be changed at any time without rebuilding the closure. Every invoice generated afterward
automatically uses whichever rate was last set.

### 3. Regex validation
Regular expressions enforce exact formats for every identifier and contact field in the
system: user IDs (a role letter followed by digits), project IDs, milestone IDs, invoice
codes, full names, email addresses, Egyptian mobile numbers, and dates in `YYYY-MM-DD` format.

### 4. Custom exceptions
Nine domain-specific exception classes replace generic errors wherever the failure means
something specific to the business, such as an invoice not being found, a payment exceeding
the remaining balance, or a user trying to access data they do not own. Every menu action
wraps its logic in a broad exception-handling block so invalid input or a rule violation
always prints a clean error message instead of crashing the program.

### 5. Functional tools — `map`, `filter`, `reduce`, `lambda`
Short lambda expressions serve as inline sort keys and filter conditions throughout the
manager layer. `filter()` is used to pull out active, late, or available projects and to
narrow payment histories to what a given user is allowed to see. `reduce()` accumulates
running totals such as the amount already paid on an invoice, a freelancer's total earnings,
and the platform's total commission. `map()` transforms the list of freelancers into a list of
earnings-report rows in a single pass.

### 6. Iterator protocol — `ProjectIterator`
A custom iterator class implements the iterator protocol explicitly, keeping its own internal
position and raising `StopIteration` once it has walked through every project, rather than
relying only on Python's built-in list iteration.

### 7. Modules used
- `datetime` — timestamps every audit log entry and computes project health from the deadline
- `re` — every regex-based validator in `validators.py`
- `json` — persists all collections to `data/*.json` on every change
- `functools.reduce` — every aggregate total (payments, earnings, commission)

## Menu Flow

```
Landing Page → Login / Register / Exit
   ├─ Client Menu     → Profile, Projects, Milestones, Invoices, Payments,
   │                     Reports, My Activity
   ├─ Freelancer Menu → Profile, Projects, Milestones, Invoices, Payments,
   │                     Reports, View Earnings, My Activity
   └─ Admin Menu      → Profile, Users, Projects, Milestones,
                         Finance & Reports, Audit Logs, My Activity,
                         Save Data, Load Data
        └─ Finance & Reports → Generate/View/Update Invoice, Invoice Status,
                                Record/View Payment, Payment History/Status,
                                Update Commission Rate, Payment Report,
                                Freelancer Earnings Report, Project Report,
                                Dashboard, Export Report
```

## Validation Rules
- All menus re-prompt on invalid input instead of crashing or exiting; typing `cancel`, `back`, or `n` returns to the previous menu at any point.
- Registration rejects empty fields, duplicate email/phone, weak passwords, and IDs that don't match the expected role prefix.
- Login allows a maximum of 3 attempts before returning to the landing page.
- Payments are rejected if they are zero, negative, non-numeric, or exceed the invoice's remaining balance.
- A project cannot be invoiced until a freelancer is assigned, and cannot be invoiced twice.
- A freelancer cannot hold more than 3 active projects (`Pending`/`In Progress`) at once.
- Milestone amounts cannot push a project's milestone total above its budget.
- Every finance, project, and milestone action is checked against the requesting user's ownership before it runs.

## Project Structure

```
sic-freelance-project-hub/
├── main.py
├── classes.py
├── manager.py
├── validators.py
├── menus/
│   ├── menus.py
│   ├── menu_helpers.py
│   ├── project_menus.py
│   ├── milestone_menus.py
│   ├── finance_menus.py
│   └── admin_menus.py
├── data/
│   ├── users.json
│   ├── projects.json
│   ├── milestones.json
│   ├── invoices.json
│   ├── payments.json
│   ├── audit_logs.json
│   └── settings.json
└── README.md
```

## Known Limitations
- There is no automated test suite; correctness is demonstrated manually through happy-path, edge-case, and exception demos.
- The Admin menu can manage existing Clients/Freelancers but cannot create a new account on their behalf — account creation only happens through self-registration.
- No memoization/caching is implemented; values such as freelancer earnings and project health are recomputed from scratch on every request.
- The application is single-user/single-session; concurrent runs against the same `data/` folder are not supported.
- There is no pagination or keyword search; lookups require an exact ID, and long lists print in full.
- A project can only ever have one invoice generated for it; there is no support for multi-invoice billing.
- The maximum number of active projects per freelancer (`MAX_ACTIVE_PROJECTS = 3`) is a fixed constant, not configurable from the menus.
- Skill matching requires an exact (case-insensitive) skill name, not a fuzzy or partial-text match.
- The system has no notification mechanism; status changes are only visible the next time the affected user opens the relevant menu.
