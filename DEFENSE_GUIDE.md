# BodyQuest — Defense Guide

**Project Name: BodyQuest**

Short, defendable answers for instructor questions during project presentation.

---

## General

**What is BodyQuest?**  
A beginner-focused fitness desktop app built with Python Flet and MySQL. Users follow daily workout plans; admins monitor real user data.

**What problem does it solve?**  
Beginners need a simple, structured plan with visible progress—not an overwhelming generic fitness app.

**Who are the target users?**  
Beginners who want guided daily workouts and accountability through unlock rules and achievements.

**Why is it beginner-focused?**  
All plans use "Beginner" difficulty, modest daily time (about 20–35 minutes), and sequential day unlocking so users cannot skip ahead.

---

## Technology

**Why Python Flet?**  
Single-language stack: UI and logic in Python. Fast to build a modern desktop interface without a separate web frontend.

**Why MySQL / Laragon?**  
Persistent relational data (users, plans, days, logs, achievements) similar to production setups. Laragon provides local MySQL for development and demos.

**Why not React / Tailwind?**  
Project requirement and scope: desktop Python app, not a browser SPA. Flet handles UI; MySQL handles data.

**Why not SQLite?**  
MySQL matches course/production expectations, supports multi-table relationships, and runs on Laragon alongside other web tools.

---

## Architecture

**What architecture did you use?**  
Layered MVC-style: Pages → Controllers → Requests / Services → Repositories → Database.

**What is MVC in your project?**  
- **Model:** `models/` constants and templates; data shape from MySQL rows.  
- **View:** `pages/` and `components/` (Flet UI).  
- **Controller:** `controllers/` — handle button actions, call services, return routes/messages.

**What is the request pattern?**  
`requests/` validate input only (email format, password strength, goal type, admin filters)—no SQL, no UI.

**What is the service pattern?**  
`services/` contain business rules: start plan, complete day, award achievements, admin summaries.

**What is the repository pattern?**  
`repositories/` contain all SQL with parameterized queries—one place to maintain database access.

**Why separate pages, controllers, services, and repositories?**  
Easier testing, clearer defense explanation, and changes to SQL or UI do not break unrelated layers.

---

## Authentication

**How does login work?**  
User enters email/password → `auth_request` validates → `auth_service` verifies hash → session stores safe user fields → redirect by role and active plan.

**How does admin login work?**  
Same login page. Default admin `admin@bodyquest.com` / `admin123` → `role = admin` → `/admin/dashboard`.

**What is the default admin account?**  
`admin@bodyquest.com` / `admin123` — created once by `database/seeders.py` if missing. No demo users are seeded.

**Legacy admin during migration:**  
`admin@gymbro.com` / `admin123` still works if that account existed before the rebrand.

**How are user and admin routes separated?**  
`router.route_guard` redirects wrong roles; layouts call `require_user` / `require_admin`; admin pages never show user workout flow as home.

---

## User Features

**How does goal setup work?**  
User picks one of five goals → stored in session → plan preview shows duration and sample week.

**How does plan generation work?**  
`plan_service` uses goal templates and duration → `goal_repository` inserts goal → `workout_repository` inserts days (Day 1 unlocked).

**How does the unlock system work?**  
Only the current unlocked incomplete day can be completed; completing it unlocks the next day number.

**How does activity completion work?**  
Controller validates → service checks ownership and lock state → marks day complete → logs progress → unlocks next or completes goal.

**How does change plan work?**  
User confirms → active goal marked `replaced` → new goal and days created → Plan Switcher achievement once → old history kept.

**How does workout history work?**  
Repository joins completed `workout_days` with `user_goals` for that user—all plan statuses (active, replaced, completed).

**How are achievements earned?**  
`achievement_service` checks rules after completions (streaks, goal type, full plan) → repository inserts if not duplicate.

---

## Admin Features

**What can admin manage?**  
View all normal users, their goals, progress, achievements, history; system leaderboard and reports.

**How does admin monitor users?**  
Dashboard stats, user list with search/filters, drill-down to details/achievements/history.

**How are reports generated?**  
`admin_repository` aggregates counts and averages with SQL; UI handles zero users without division errors.

**How does leaderboard work?**  
Users ranked by achievements, completed goals, completed workout days, then current progress percentage.

---

## Security

**How do you protect admin pages?**  
Route guard + `is_admin_session` in admin layout + controller `require_admin`.

**How do you prevent normal users from accessing admin features?**  
Redirect to `/user/dashboard` with flash message if a user hits `/admin/*`.

**How do you protect user data?**  
Queries filter by `user_id` from session; completion checks `goal_belongs_to_user`.

**How do you prevent duplicate active plans or achievements?**  
`create_goal` replaces active plan first; `achievement_exists` before insert; `log_exists` for progress logs.

---

## Limitations and Future Improvements

**Limitations**  
- Desktop-only (Flet local app).  
- Single-machine MySQL (Laragon).  
- Beginner plans only; no trainer/coach role.  
- No email verification or password reset.

**Future improvements**  
- Hosted MySQL / cloud deploy.  
- Mobile-friendly Flet or web build.  
- Email notifications, social features, custom plan editor.  
- Environment variables for secrets (not hardcoded admin in settings for production).

**Can this be deployed online?**  
Yes with changes: remote MySQL, secure secrets, HTTPS if a web build is added. Current design targets local Laragon demo.

**Can this support mobile users?**  
Flet supports mobile targets in theory; UI would need responsive tuning and remote database hosting.

---

*See also: [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md), [DEMO_SCRIPT.md](DEMO_SCRIPT.md), [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md).*
