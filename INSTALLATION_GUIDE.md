# GymBro — Installation Guide

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
cd C:\laragon\www\GYMBRO
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
[GYMBRO] Initializing MySQL database...
[GYMBRO] MySQL health check passed (SELECT 1)
[GYMBRO] Database ready: gymbro
[GYMBRO] Default admin already exists (no duplicate created)
[GYMBRO] Launching app...
```

The GymBro window should open on the **Login** page.

---

## Default Admin Account

| Field | Value |
|-------|--------|
| Email | `admin@gymbro.com` |
| Password | `admin123` |

**No demo user accounts** are created. Register normal users via **Sign up**.

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

Run from project root: `C:\laragon\www\GYMBRO`.

### Invalid admin login

**Fix:** Use exactly `admin@gymbro.com` / `admin123`.  
Check `users` table in phpMyAdmin — one row with `role = admin`.

### Port conflict (3306)

**Fix:** Stop other MySQL services or change Laragon MySQL port and update `config/settings.py` `DB_PORT`.

### Missing requirements / wrong Python

**Fix:** Use `py -3` or ensure Python is on PATH. Reinstall: `pip install flet mysql-connector-python`.

### Blank screen or route loop

**Fix:** Close app and restart. Ensure you are logged in with the correct role. Unknown URLs should show **404**, not loop.

### Import errors

**Fix:** Run commands from `GYMBRO` root, not from a subfolder.

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
