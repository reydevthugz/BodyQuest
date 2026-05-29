# GymBro — Final Submission Checklist

Use this before submitting the project or presenting your defense.

---

## Before Running

- [ ] Laragon installed
- [ ] MySQL started (green in Laragon)
- [ ] Python 3 installed (`py --version`)
- [ ] Terminal opened at `C:\laragon\www\GYMBRO`
- [ ] `pip install -r requirements.txt` completed

---

## Database Checklist

- [ ] Database name: `gymbro`
- [ ] Host: `localhost`, port `3306`
- [ ] User: `root`, password: empty
- [ ] `py main.py` creates tables if missing
- [ ] No tables dropped on restart
- [ ] Default admin exists: `admin@gymbro.com`
- [ ] No demo users seeded automatically
- [ ] Password hashing columns present (`password_hash`, `password_salt`)

---

## Authentication Checklist

- [ ] Signup creates `role = user`
- [ ] Duplicate email blocked
- [ ] Weak password rejected (8+ chars, letter + number)
- [ ] Admin login → `/admin/dashboard`
- [ ] User without plan → `/user/goal-setup`
- [ ] User with active plan → `/user/dashboard`
- [ ] Logout clears session
- [ ] Protected routes blocked after logout

---

## User Flow Checklist

- [ ] Sign up new user
- [ ] Select fitness goal
- [ ] Plan preview loads
- [ ] Start plan works
- [ ] Dashboard shows progress
- [ ] Complete Day 1 activity
- [ ] Day 2 unlocks on timeline
- [ ] History shows completion
- [ ] Achievements appear (no duplicates)
- [ ] Change plan (old history kept)
- [ ] Profile and logout work

---

## Admin Flow Checklist

- [ ] Login `admin@gymbro.com` / `admin123`
- [ ] Admin dashboard loads (empty state OK if no users)
- [ ] User management list (admin not in list)
- [ ] Search / filter users
- [ ] User details for selected user
- [ ] Selected user achievements
- [ ] Selected user workout history
- [ ] All achievements page
- [ ] Leaderboard page
- [ ] Reports page (no crash with zero data)
- [ ] Admin profile and logout

---

## Security Checklist

- [ ] Passwords not shown in UI or session
- [ ] User cannot open `/admin/*`
- [ ] Admin redirected from `/user/*`
- [ ] SQL parameterized in repositories only
- [ ] Cannot complete locked or duplicate days
- [ ] Only one active goal per user
- [ ] Achievements not duplicated

---

## UI Checklist

- [ ] Dark theme with neon green / blue accents
- [ ] Glass-style cards visible
- [ ] Empty states on lists with no data
- [ ] Error messages user-friendly (no raw SQL)
- [ ] Change plan dialog opens and closes
- [ ] Snackbars on signup / start plan
- [ ] No blank pages on valid routes
- [ ] 404 page for unknown routes

---

## Architecture Checklist

- [ ] No SQL in `pages/` or `controllers/`
- [ ] No Flet UI in `repositories/` or `services/`
- [ ] Business logic in `services/`
- [ ] Validation in `requests/`

---

## Forbidden Technology Scan

- [ ] No SQLite required to run
- [ ] No React / Tailwind / Node frontend in project
- [ ] No `client_storage` or `flet_core` in app code
- [ ] `requirements.txt` only: `flet`, `mysql-connector-python`

---

## Automated Validation

```bash
py scripts\validate_phase10.py
```

- [ ] All checks passed

---

## Submission Checklist

- [ ] `README.md` updated
- [ ] `SYSTEM_OVERVIEW.md` included
- [ ] `DEFENSE_GUIDE.md` included
- [ ] `INSTALLATION_GUIDE.md` included
- [ ] `DEMO_SCRIPT.md` included
- [ ] `PROJECT_STRUCTURE.md` included
- [ ] `FINAL_CHECKLIST.md` (this file) included
- [ ] Source code folders complete (`pages`, `controllers`, `services`, etc.)
- [ ] No `.env` secrets committed (if added later)
- [ ] Project runs with: `pip install -r requirements.txt` then `py main.py`

---

## Final Run

```bash
pip install -r requirements.txt
py main.py
```

**Default admin:** `admin@gymbro.com` / `admin123`  
**Users:** Create only via Signup during demo.
