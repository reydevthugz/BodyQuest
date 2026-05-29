# GymBro

**GymBro** is a beginner-focused fitness desktop application built with **Python Flet** and **Laragon MySQL**. Users sign up, choose a fitness goal, complete daily workouts with sequential unlocking, and earn achievements. Administrators monitor real user progress through a separate admin dashboard.

---

## System Overview

| Role | Purpose |
|------|---------|
| **User** | Sign up, set goals, complete daily workouts, view timeline/history/achievements |
| **Admin** | Monitor users, plans, achievements, leaderboard, and reports |

**Seeding policy:** Only the **default admin** is created automatically. Normal users register through **Signup** — no demo/fake users are inserted.

---

## Features

### User Features

- Sign up and log in (validated email and password)
- Five beginner fitness goals with plan preview
- Start plan → generated workout days in MySQL
- Daily activity completion and next-day unlock
- Plan timeline (completed / current / locked)
- Workout history (includes replaced and completed plans)
- Achievements (no duplicates)
- Change current plan (history preserved)
- Profile and logout

### Admin Features

- Dashboard with live MySQL statistics
- User management (search and filters)
- Per-user details, achievements, and workout history
- All achievements, leaderboard, reports
- Admin profile and logout

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| UI | Flet (desktop) |
| Database | MySQL / MariaDB (Laragon) |
| Driver | mysql-connector-python |

**Not used:** SQLite, React, Tailwind, `client_storage`, `flet_core`, Node.js frontend.

---

## Architecture

```
Pages → Controllers → Requests (validation)
                   → Services (business logic)
                     → Repositories (SQL)
                       → Database (connection, migrations, seeding)
```

See **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** for the full folder tree and layer rules.

---

## Folder Structure (Summary)

```
GYMBRO/
├── main.py, app.py, router.py
├── config/, database/, models/
├── repositories/, requests/, controllers/, services/
├── components/, pages/, utils/
└── scripts/          # Optional QA validators
```

---

## Database Setup

| Setting | Value |
|---------|--------|
| Database | `gymbro` |
| Host | `localhost` |
| Port | `3306` |
| User | `root` |
| Password | *(empty)* |

**Tables:** `users`, `user_goals`, `workout_days`, `progress_logs`, `achievements`

Created automatically on first run via `database/migrations.py` (no data loss on restart).

---

## Default Admin Account

| Field | Value |
|-------|--------|
| Email | `admin@gymbro.com` |
| Password | `admin123` |
| Role | `admin` |

If this account already exists, startup will **not** create a duplicate.

---

## Installation & Run

```bash
cd C:\laragon\www\GYMBRO
pip install -r requirements.txt
py main.py
```

**Prerequisites:** Python 3, Laragon with MySQL running.

Detailed steps: **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**

---

## Route List

### Public / Auth

| Route | Description |
|-------|-------------|
| `/login` | Login (users and admin) |
| `/signup` | Register new user |
| `/404` | Page not found |

### User Routes

| Route | Description |
|-------|-------------|
| `/user/dashboard` | Main user home |
| `/user/goal-setup` | Choose fitness goal |
| `/user/plan-preview` | Preview plan before start |
| `/user/activity` | Current day workout |
| `/user/timeline` | Plan day statuses |
| `/user/achievements` | User badges |
| `/user/history` | Completed workouts |
| `/user/profile` | Profile, change plan, logout |
| `/user/change-plan` | Goal selection when changing plan |

### Admin Routes

| Route | Description |
|-------|-------------|
| `/admin/dashboard` | System overview |
| `/admin/users` | User management |
| `/admin/users/details` | Selected user details |
| `/admin/users/achievements` | Selected user achievements |
| `/admin/users/history` | Selected user history |
| `/admin/achievements` | All achievements |
| `/admin/leaderboard` | Rankings |
| `/admin/reports` | Analytics |
| `/admin/profile` | Admin profile and logout |

---

## Security Notes

- Passwords stored with **PBKDF2-HMAC-SHA256** + per-user salt
- Session stores only safe user fields (never passwords)
- Parameterized SQL in repositories only
- Role-based route guards (admin ↔ user separation)
- Activity completion: ownership + unlocked-day validation
- Duplicate active goals and achievements prevented

Validate: `py scripts\validate_phase8_qa.py`

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) | Full system description |
| [DEFENSE_GUIDE.md](DEFENSE_GUIDE.md) | Instructor Q&A |
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Setup and troubleshooting |
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | Presentation script |
| [DEMO_CHECKLIST.md](DEMO_CHECKLIST.md) | Demo rehearsal checklist |
| [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) | Pre-submission checklist |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Code organization |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MySQL connection error | Start MySQL in Laragon |
| Database missing | Run `py main.py` once |
| Admin login fails | Use `admin@gymbro.com` / `admin123` |
| Empty admin lists | Normal before any user signs up |
| Import errors | Run from project root |
| Module not found | `pip install -r requirements.txt` |

---

## Phase Summary

| Phase | Focus |
|-------|--------|
| 1 | Flet UI (dark / neon theme) |
| 2 | Laragon MySQL authentication |
| 3 | User fitness plans and unlock logic |
| 4 | Admin management |
| 5 | Final QA |
| 6 | Demo preparation and documentation |
| 7 | MVC + Request + Service + Repository refactor |
| 8 | Security, validation, password hashing |
| 9 | Testing, debugging, stability |
| 10 | Final submission and defense package |

---

## Final Validation

```bash
py scripts\validate_phase10.py
```

---

## Authors / Contributors

- **[Your Name]** — Developer / Presenter  
- **Course / Institution** — [Add your school or subject]  
- **Date** — [Submission date]

---

## License / Academic Use

Built for coursework demonstration and defense. For production use, add environment-based secrets, HTTPS, and hosted database configuration.
