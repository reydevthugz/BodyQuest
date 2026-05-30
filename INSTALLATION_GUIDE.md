# BodyQuest — Installation Guide

**Project Name: BodyQuest**

## Required Software

| Software | Purpose |
|----------|---------|
| **Python 3.10+** | Run the application |
| **pip** | Install Python packages |
| **Laragon** | Local Apache/MySQL stack |
| **MySQL / MariaDB** | Database (included with Laragon) |

Optional: **phpMyAdmin** (included with Laragon) to inspect the `gymbro` database.

---

## Step 1: Install Laragon

1. Download and install [Laragon](https://laragon.org/) (full version recommended).
2. Open Laragon.

---

## Step 2: Start MySQL

1. Click **Start All** in Laragon (or start **MySQL** only).
2. Confirm MySQL is running (green indicator).
3. Default port: **3306**.

---

## Step 3: Database (gymbro)

> **Database name remains:** `gymbro`

You do **not** need to create tables manually.

1. Optional: open **phpMyAdmin** from Laragon menu → **Database** → check if `gymbro` exists.
2. On first run, `py main.py` will:
   - Create database `gymbro` if missing
   - Create tables: `users`, `user_goals`, `workout_days`, `progress_logs`, `achievements`
   - Seed **only** the default admin account (if not already present)

**Connection settings** (`config/settings.py`):

| Setting | Value |
|---------|--------|
| Host | `localhost` |
| Port | `3306` |
| User | `root` |
| Password | *(empty)* |
| Database | `gymbro` |

---

## Step 4: Install Python Dependencies

Open a terminal in the project folder:

```bash
cd C:\laragon\www\BodyQuest
pip install -r requirements.txt
```

**requirements.txt** contains only:

```
flet
mysql-connector-python
```

---

## Step 5: Run the Application

```bash
py main.py
```

Expected console output:

```
[BODYQUEST] Initializing MySQL database...
[BODYQUEST] MySQL health check passed (SELECT 1)
[BODYQUEST] Database ready: gymbro
[BODYQUEST] Default admin already exists (no duplicate created)
[BODYQUEST] Launching app...
```

The BodyQuest window should open on the **Login** page.

---

## Default Admin Account

| Field | Value |
|-------|--------|
| Email | `admin@bodyquest.com` |
| Password | `admin123` |

**No demo user accounts** are created. Register normal users via **Sign up**.

**Migration note:** If you previously used `admin@gymbro.com`, that account still works alongside the new default admin.

---

## Troubleshooting

### MySQL not running

**Symptom:** `MySQL connection error` or startup failed.  
**Fix:** Start MySQL in Laragon; confirm port 3306 is free.

### Unknown database

**Symptom:** Database does not exist.  
**Fix:** Run `py main.py` once; migrations create `gymbro` automatically.

### ModuleNotFoundError (flet or mysql)

**Fix:**

```bash
pip install -r requirements.txt
```

Run from project root: `C:\laragon\www\BodyQuest`.

### Invalid admin login

**Fix:** Use exactly `admin@bodyquest.com` / `admin123`.  
Legacy: `admin@gymbro.com` / `admin123` if that account existed before rebrand.  
Check `users` table in phpMyAdmin — row(s) with `role = admin`.

### Port conflict (3306)

**Fix:** Stop other MySQL services or change Laragon MySQL port and update `config/settings.py` `DB_PORT`.

### Missing requirements / wrong Python

**Fix:** Use `py -3` or ensure Python is on PATH. Reinstall: `pip install flet mysql-connector-python`.

### Blank screen or route loop

**Fix:** Close app and restart. Ensure you are logged in with the correct role. Unknown URLs should show **404**, not loop.

### Import errors

**Fix:** Run commands from `BodyQuest` root, not from a subfolder.

---

## Verification Commands

```bash
pip install -r requirements.txt
py scripts\validate_phase9.py
py main.py
```

All validation checks should pass before your defense demo.

---

*See [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) for pre-demo checklist.*
