# GymBro — System Overview

## Project Title

**GymBro** — A Beginner Fitness Plan Tracker (Python Flet + MySQL)

## Short Description

GymBro is a desktop fitness application that helps beginners choose a fitness goal, follow a structured daily workout plan, unlock activities day by day, track progress, and earn achievements. A separate admin interface monitors registered users, plans, and system-wide analytics.

## Problem Statement

Many beginners struggle to stay consistent with fitness because they lack a simple, guided plan and visible progress. Generic apps can feel overwhelming. GymBro focuses on **beginner-friendly**, goal-based daily plans with clear unlock rules and motivation through achievements.

## System Objective

- Let users **register**, **set a goal**, and **complete daily activities** in sequence.
- Preserve **workout history** when users change plans.
- Give administrators **real-time visibility** into user registration, active plans, achievements, and reports.
- Use a **clean layered architecture** suitable for academic defense and future extension.

## User Role

| Aspect | Description |
|--------|-------------|
| Who | Registered normal users (`role = user`) |
| Access | `/user/*` routes only |
| Capabilities | Signup, login, goal setup, plan preview, start plan, daily activity, timeline, history, achievements, change plan, profile, logout |
| Data scope | **Own data only** — goals, workouts, logs, achievements tied to their `user_id` |

## Admin Role

| Aspect | Description |
|--------|-------------|
| Who | Default admin (`admin@gymbro.com`) — seeded once at startup if missing |
| Access | `/admin/*` routes only |
| Capabilities | Dashboard, user management (search/filter), per-user details/achievements/history, all achievements, leaderboard, reports, profile, logout |
| Data scope | **System-wide** — all users with `role = user` (admin is never counted as a normal user) |

## Main User Features

1. **Signup / Login** — Email validation, strong password rules, role `user`.
2. **Goal Setup** — Five beginner goals with suggested durations.
3. **Plan Preview** — First-week sample before starting.
4. **Start Plan** — Generates workout days in MySQL; only Day 1 unlocked.
5. **Dashboard** — Progress, current day, recent achievements/history.
6. **Daily Activity** — Complete current unlocked day only.
7. **Plan Timeline** — Completed / current / locked day states.
8. **Workout History** — All completed days (active, replaced, completed plans).
9. **Achievements** — Earned badges (no duplicates).
10. **Change Plan** — Replace active plan; history preserved.
11. **Profile & Logout**

## Main Admin Features

1. **Admin Dashboard** — Totals, goal distribution, recent activity, top users.
2. **User Management** — Search, filters (Active, Inactive, Completed Goal, Changed Plan).
3. **User Details** — Progress, goal, achievements count, last activity.
4. **Selected User Achievements / History**
5. **All Achievements** — System-wide list with search/badge filter.
6. **Leaderboard** — Ranked by achievements, completed goals, workout days, progress.
7. **Reports** — Aggregated metrics (safe with zero users).
8. **Admin Profile & Logout**

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3 |
| UI | Flet (desktop) |
| Database | MySQL / MariaDB via Laragon |
| DB driver | mysql-connector-python |
| Local server | Laragon (`localhost:3306`, database `gymbro`) |

**Not used:** SQLite, React, Tailwind, `client_storage`, `flet_core`, Node.js frontend.

## Database Overview

| Table | Purpose |
|-------|---------|
| `users` | Accounts (`admin` / `user`), hashed passwords |
| `user_goals` | Fitness goals (`active`, `completed`, `replaced`) |
| `workout_days` | Daily plan rows per goal (unlock/complete flags) |
| `progress_logs` | Actions: started plan, completed day, completed plan |
| `achievements` | Badges earned per user (optional `goal_id`) |

Tables are created automatically by `database/migrations.py`. Missing columns (e.g. `password_hash`) are added safely without dropping data.

## Architecture Pattern

```
Pages (UI)
  → Controllers (actions, orchestration)
    → Requests (input validation)
    → Services (business logic)
      → Repositories (parameterized SQL)
        → Database (connection, migrations, seeding)
```

**Components** — Reusable UI (theme, cards, buttons, layouts).  
**Utils** — Routes, responses, security, dates, messages.

## Routing Overview

- **Public:** `/login`, `/signup`, `/404`
- **User:** `/user/dashboard`, `/user/goal-setup`, `/user/plan-preview`, `/user/activity`, `/user/timeline`, `/user/achievements`, `/user/history`, `/user/profile`, `/user/change-plan`
- **Admin:** `/admin/dashboard`, `/admin/users`, `/admin/users/details`, `/admin/users/achievements`, `/admin/users/history`, `/admin/achievements`, `/admin/leaderboard`, `/admin/reports`, `/admin/profile`

`router.py` enforces role-based redirects (guest → login, user ↔ admin separation, no active plan → goal setup).

## Security Overview

- PBKDF2-HMAC-SHA256 password hashing with per-user salt.
- Session stores only `user_id`, `role`, `full_name`, `email` — never passwords.
- Parameterized queries in repositories only.
- Route guards and layout guards for admin/user separation.
- Activity completion checks goal ownership and current unlocked day.
- Duplicate active goals and achievements prevented at repository/service level.

## Fitness Plan Logic Overview

| Goal | Duration (days) |
|------|-----------------|
| Lose Weight | 30 |
| Gain Muscle | 30 |
| Improve Endurance | 21 |
| Improve Flexibility | 14 |
| General Fitness | 30 |

Templates rotate through beginner warmup, main activity, cooldown, and safety tips. Plans are generated when the user clicks **Start Plan**.

## Unlock System

- **Day 1** is unlocked when the plan is created.
- User may complete **only** the current unlocked, incomplete day.
- On completion: day marked done, `progress_logs` entry, next day unlocked.
- On final day: goal status → `completed`, plan champion achievement eligible.
- Locked days cannot be completed or skipped.

## Achievement System

Examples: First Step Completed, 3-Day Streak, 7-Day Consistency, Cardio Starter, Strength Beginner, Flexibility Builder, Plan Switcher (one per user when replacing active plan), Full Plan Champion (all days done).

Achievements are inserted only if not already earned for that user/name/goal combination.

## Change Plan

1. User confirms via dialog (Dashboard or Profile).
2. Redirect to `/user/change-plan` (goal selection).
3. Active plan → `replaced` with `replaced_at`.
4. New plan created; only new Day 1 unlocked.
5. Completed workouts from old plans remain in **Workout History**.

---

*For installation, see [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md). For defense Q&A, see [DEFENSE_GUIDE.md](DEFENSE_GUIDE.md).*
